#!/usr/bin/env python3
"""
火山引擎 TTS HTTP REST API 客户端（简化版）
使用 v1 WebSocket API，比 v3 更稳定
"""
import argparse
import asyncio
import json
import logging
import os
import uuid
from pathlib import Path

import websockets

# 添加 protocols 路径
import sys
DEMO_DIR = Path(__file__).resolve().parent / "vendor" / "volcengine_ws_demo"
sys.path.insert(0, str(DEMO_DIR))

from protocols import MsgType, full_client_request, receive_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_cluster(voice: str) -> str:
    """根据音色判断集群"""
    if voice.startswith("S_"):
        return "volcano_icl"
    return "volcano_tts"


async def synthesize_tts(
    appid: str,
    token: str,
    text: str,
    voice_type: str = "zh_female_cancan_mars_bigtts",
    encoding: str = "mp3",
    endpoint: str = "wss://openspeech.bytedance.com/api/v1/tts/ws_binary",
) -> bytes:
    """调用火山引擎 TTS API"""
    
    cluster = get_cluster(voice_type)
    headers = {"Authorization": f"Bearer;{token}"}
    
    logger.info(f"连接到 {endpoint}")
    websocket = await websockets.connect(
        endpoint, additional_headers=headers, max_size=10 * 1024 * 1024
    )
    
    logid = websocket.response.headers.get("x-tt-logid", "N/A")
    logger.info(f"已连接，Logid: {logid}")
    
    try:
        # 构建请求
        request = {
            "app": {
                "appid": appid,
                "token": token,
                "cluster": cluster,
            },
            "user": {
                "uid": str(uuid.uuid4()),
            },
            "audio": {
                "voice_type": voice_type,
                "encoding": encoding,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "operation": "submit",
            },
        }
        
        # 发送请求
        await full_client_request(websocket, json.dumps(request).encode())
        logger.info("请求已发送")
        
        # 接收音频数据
        audio_data = bytearray()
        while True:
            msg = await receive_message(websocket)
            
            if msg.type == MsgType.FrontEndResultServer:
                continue
            elif msg.type == MsgType.AudioOnlyServer:
                audio_data.extend(msg.payload)
                logger.debug(f"接收音频数据：{len(msg.payload)} 字节")
                if msg.sequence < 0:  # 最后一条消息
                    break
            else:
                raise RuntimeError(f"TTS 转换失败: {msg}")
        
        if not audio_data:
            raise RuntimeError("未接收到音频数据")
        
        logger.info(f"音频接收完成：{len(audio_data)} 字节")
        return bytes(audio_data)
        
    finally:
        await websocket.close()
        logger.info("连接已关闭")


async def main():
    parser = argparse.ArgumentParser(description="火山引擎 TTS 合成")
    parser.add_argument("--text-file", default="script.txt", help="输入文本文件")
    parser.add_argument("--output", default="output.mp3", help="输出音频文件")
    parser.add_argument("--voice", default="zh_female_cancan_mars_bigtts", help="音色")
    parser.add_argument("--encoding", default="mp3", choices=["mp3", "wav"], help="音频格式")
    
    args = parser.parse_args()
    
    # 读取环境变量
    appid = os.getenv("VOLC_APP_ID")
    token = os.getenv("VOLC_AUTH_TOKEN")
    
    if not appid or not token:
        raise ValueError("请设置环境变量 VOLC_APP_ID 和 VOLC_AUTH_TOKEN")
    
    # 读取文本
    text_file = Path(args.text_file)
    if not text_file.exists():
        raise FileNotFoundError(f"文本文件不存在: {text_file}")
    
    text = text_file.read_text(encoding="utf-8").strip()
    logger.info(f"读取文本：{len(text)} 字符")
    
    # 合成音频
    audio_data = await synthesize_tts(
        appid=appid,
        token=token,
        text=text,
        voice_type=args.voice,
        encoding=args.encoding,
    )
    
    # 保存文件
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(audio_data)
    
    logger.info(f"音频已保存：{output_path} ({len(audio_data) / 1024:.2f} KB)")


if __name__ == "__main__":
    asyncio.run(main())
