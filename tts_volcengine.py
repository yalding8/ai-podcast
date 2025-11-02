#!/usr/bin/env python3
"""
Volcengine MaaS 双向流式 WebSocket TTS 客户端 (V3，支持复刻 / 混音 mix)
---------------------------------------------------------------------------
使用方式：
1. 安装依赖：pip install websockets
2. 设置必须的环境变量：
   - VOLC_APP_ID：应用 AppID
   - VOLC_AUTH_TOKEN：Access Token 或 API Key
   - VOLC_MAAS_ENDPOINT：WebSocket 端点，如 wss://openspeech.bytedance.com/api/v3/tts/ws_binary
3. 可选环境变量：
   - VOLC_CLUSTER：集群名称，可不填（根据 voice_type 自动推断）
   - VOLC_VOICE_TYPE：主音色，默认 S_zh_general
   - VOLC_VOICE_CLONE_ID：复刻音色 ID（需要开通复刻）
   - VOLC_MIX_CONFIG：JSON 字符串，用于定义混音轨道
   - TTS_OUTPUT_FILE：输出音频文件名，默认 output.wav
   - TTS_TEXT_FILE：输入文本文件，默认 script.txt
   - TTS_ENCODING：返回音频格式，默认 wav，可选 mp3/ogg 等
   - TTS_SAMPLE_RATE：采样率，默认 24000
   - TTS_SPEED：语速倍率，默认 1.0
   - TTS_VOLUME：音量倍率，默认 1.0
   - TTS_PITCH：音调倍率，默认 0

示例：
export VOLC_APP_ID=xxxx
export VOLC_AUTH_TOKEN=yyyy
export VOLC_MAAS_ENDPOINT=wss://openspeech.bytedance.com/api/v3/tts/ws_binary
python tts_volcengine.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import contextlib

import websockets

# 将 demo 协议工具加入路径（用于解析/封装消息）
DEMO_DIR = Path(__file__).resolve().parent / "vendor" / "volcengine_ws_demo"
if DEMO_DIR.exists():
    sys.path.insert(0, str(DEMO_DIR))

from protocols import (  # type: ignore  # noqa: E402
    EventType,
    Message,
    MsgType,
    MsgTypeFlagBits,
    audio_only_client,
    finish_connection,
    finish_session,
    full_client_request,
    receive_message,
    start_connection,
    start_session,
    wait_for_event,
)

logger = logging.getLogger("volcengine.tts.websocket")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def _env(key: str, default: Optional[str] = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Missing environment variable: {key}")
    return value


def _optional_json_env(key: str) -> Optional[Any]:
    raw = os.getenv(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Environment variable {key} 不是合法 JSON: {exc}") from exc


def _infer_cluster(voice_type: str) -> str:
    """
    根据音色判断集群：
    - S_* 前缀通常为火山自研 ICL 集群
    - 其他默认为 volcano_tts
    """
    if voice_type.startswith("S_"):
        return "volcano_icl"
    return "volcano_tts"


def _chunk_text(text: str, chunk_size: int = 300) -> List[str]:
    """
    将文本分块，用于实时流式合成。
    """
    text = text.strip()
    if not text:
        return []
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


@dataclass
class AudioConfig:
    voice_type: str
    encoding: str = "wav"
    sample_rate: int = 24000
    speed_ratio: float = 1.0
    volume_ratio: float = 1.0
    pitch: float = 0.0
    voice_clone_id: Optional[str] = None
    mix_config: Optional[Any] = None  # 允许任意 JSON 结构，如 [{"voice_type":"S_zh_A","gain":0.7},{"voice_type":"bgm_pop","gain":0.3}]
    extra_params: Dict[str, Any] = field(default_factory=dict)

    def to_request_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "voice_type": self.voice_type,
            "encoding": self.encoding,
            "sample_rate": self.sample_rate,
            "speed_ratio": self.speed_ratio,
            "volume_ratio": self.volume_ratio,
            "pitch_ratio": self.pitch,
        }
        if self.voice_clone_id:
            result["voice_clone_id"] = self.voice_clone_id
        if self.mix_config:
            result["mix_streams"] = self.mix_config
        result.update(self.extra_params)
        return result


@dataclass
class TTSClientConfig:
    app_id: str
    auth_token: str
    endpoint: str
    auth_scheme: str = "Bearer;"  # 新版也兼容 Bearer token
    cluster: Optional[str] = None
    uid: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_extra: Dict[str, Any] = field(default_factory=dict)


class TTSDuplexClient:
    def __init__(self, client_cfg: TTSClientConfig, audio_cfg: AudioConfig):
        self.client_cfg = client_cfg
        self.audio_cfg = audio_cfg
        self.session_id = str(uuid.uuid4())
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.audio_buffer = bytearray()
        self._finished = asyncio.Event()

    async def __aenter__(self) -> "TTSDuplexClient":
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def _connect(self) -> None:
        headers = {"Authorization": f"{self.client_cfg.auth_scheme}{self.client_cfg.auth_token}"}
        logger.info("Connecting to %s", self.client_cfg.endpoint)
        self.websocket = await websockets.connect(
            self.client_cfg.endpoint,
            additional_headers=headers,
            max_size=16 * 1024 * 1024,
        )
        logger.info(
            "Connected, x-tt-logid=%s",
            self.websocket.response.headers.get("x-tt-logid", "N/A")
            if self.websocket.response
            else "N/A",
        )

        await start_connection(self.websocket)
        await wait_for_event(
            self.websocket,
            MsgType.FullServerResponse,
            EventType.ConnectionStarted,
        )

        logger.info("Connection established, starting session %s", self.session_id)
        start_payload = self._build_start_payload()
        await start_session(
            self.websocket,
            json.dumps(start_payload, ensure_ascii=False).encode("utf-8"),
            self.session_id,
        )
        await wait_for_event(
            self.websocket,
            MsgType.FullServerResponse,
            EventType.SessionStarted,
        )
        logger.info("Session started")

    def _build_start_payload(self) -> Dict[str, Any]:
        cluster = self.client_cfg.cluster or _infer_cluster(self.audio_cfg.voice_type)
        return {
            "app": {
                "appid": self.client_cfg.app_id,
                "token": self.client_cfg.auth_token,
                "cluster": cluster,
            },
            "user": {"uid": self.client_cfg.uid},
            "audio": self.audio_cfg.to_request_dict(),
            "request": self.client_cfg.request_extra or {},
        }

    async def stream_text(self, text: str, chunk_size: int = 300) -> bytes:
        if not self.websocket:
            raise RuntimeError("WebSocket 尚未建立")

        async def receiver() -> None:
            try:
                while True:
                    msg = await receive_message(self.websocket)
                    logger.debug("recv <- %s", msg)

                    if msg.type == MsgType.AudioOnlyServer:
                        self.audio_buffer.extend(msg.payload)
                        if msg.flag in (
                            MsgTypeFlagBits.LastNoSeq,
                            MsgTypeFlagBits.NegativeSeq,
                        ):
                            logger.info("音频数据接收完毕")
                            self._finished.set()
                            break
                    elif msg.type == MsgType.FullServerResponse:
                        self._handle_server_event(msg)
                    elif msg.type == MsgType.Error:
                        raise RuntimeError(f"TTS 服务返回错误，code={msg.error_code}")
            except Exception as exc:
                logger.error("Receiver 线程异常：%s", exc)
                self._finished.set()
                raise

        chunks = _chunk_text(text, chunk_size=chunk_size)
        if not chunks:
            raise ValueError("输入文本为空，无法合成")

        recv_task = asyncio.create_task(receiver())

        for idx, chunk in enumerate(chunks):
            payload = {
                "text": chunk,
                "is_final": idx == len(chunks) - 1,
            }
            await audio_only_client(
                self.websocket,
                json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                MsgTypeFlagBits.PositiveSeq if idx < len(chunks) - 1 else MsgTypeFlagBits.NegativeSeq,
            )
            logger.info("已发送文本分段 %d/%d", idx + 1, len(chunks))

        await self._finished.wait()

        recv_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await recv_task

        await finish_session(self.websocket, self.session_id)
        await wait_for_event(
            self.websocket,
            MsgType.FullServerResponse,
            EventType.SessionFinished,
        )
        logger.info("Session finished")

        await finish_connection(self.websocket)
        await wait_for_event(
            self.websocket,
            MsgType.FullServerResponse,
            EventType.ConnectionFinished,
        )
        logger.info("Connection closed gracefully")

        return bytes(self.audio_buffer)

    def _handle_server_event(self, msg: Message) -> None:
        if msg.event in (
            EventType.TaskStarted,
            EventType.TTSResponse,
            EventType.PodcastRoundStart,
            EventType.PodcastRoundEnd,
        ):
            logger.info("服务事件：%s -> %s", msg.event.name, msg.payload.decode() if msg.payload else "")

    async def close(self) -> None:
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
            logger.info("WebSocket closed")


def load_script(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"未找到脚本文件：{path}")
    return path.read_text(encoding="utf-8")


def save_audio(path: Path, data: bytes) -> None:
    path.write_bytes(data)
    logger.info("音频已保存：%s (%.2f KB)", path, len(data) / 1024)


async def main() -> None:
    text_path = Path(os.getenv("TTS_TEXT_FILE", "script.txt"))
    output_path = Path(os.getenv("TTS_OUTPUT_FILE", "output.wav"))

    # 读取文本
    text = load_script(text_path)

    # 构建配置
    audio_cfg = AudioConfig(
        voice_type=os.getenv("VOLC_VOICE_TYPE", "S_zh_general"),
        encoding=os.getenv("TTS_ENCODING", "wav"),
        sample_rate=int(os.getenv("TTS_SAMPLE_RATE", "24000")),
        speed_ratio=float(os.getenv("TTS_SPEED", "1.0")),
        volume_ratio=float(os.getenv("TTS_VOLUME", "1.0")),
        pitch=float(os.getenv("TTS_PITCH", "0.0")),
        voice_clone_id=os.getenv("VOLC_VOICE_CLONE_ID"),
        mix_config=_optional_json_env("VOLC_MIX_CONFIG"),
        extra_params=_optional_json_env("VOLC_AUDIO_EXTRAS") or {},
    )

    client_cfg = TTSClientConfig(
        app_id=_env("1474910664"),
        auth_token=_env("_UVnEQFD_Mrq7OKFN_ulNKIyJhV6vdGl"),
        endpoint=_env(
            "VOLC_MAAS_ENDPOINT",
            "wss://openspeech.bytedance.com/api/v3/tts/bidirection",
        ),
        auth_scheme=os.getenv("VOLC_AUTH_SCHEME", "Bearer;"),
        cluster=os.getenv("VOLC_CLUSTER"),
        request_extra=_optional_json_env("VOLC_REQUEST_EXTRAS") or {},
    )

    async with TTSDuplexClient(client_cfg, audio_cfg) as client:
        audio = await client.stream_text(text)
        save_audio(output_path, audio)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("用户终止执行")
