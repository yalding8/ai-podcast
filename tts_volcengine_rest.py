#!/usr/bin/env python3
"""
火山引擎 TTS REST API 客户端（v3 单向接口）
使用简单的 HTTP POST 请求，无需 WebSocket
"""
import argparse
import json
import logging
import os
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def synthesize_tts(
    api_key: str,
    text: str,
    speaker: str = "zh_male_beijingxiaoye_emo_v2_mars_bigtts",
    format: str = "mp3",
    sample_rate: int = 24000,
) -> bytes:
    """调用火山引擎 TTS REST API"""
    
    url = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"
    
    headers = {
        "x-api-key": api_key,
        "X-Api-Resource-Id": "volc.service_type.10029",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
    }
    
    additions = {
        "disable_markdown_filter": True,
        "enable_language_detector": True,
        "enable_latex_tn": True,
        "disable_default_bit_rate": True,
        "max_length_to_filter_parenthesis": 0,
        "cache_config": {
            "text_type": 1,
            "use_cache": True,
        },
    }
    
    payload = {
        "req_params": {
            "text": text,
            "speaker": speaker,
            "additions": json.dumps(additions, ensure_ascii=False),
            "audio_params": {
                "format": format,
                "sample_rate": sample_rate,
            },
        }
    }
    
    logger.info(f"发送请求到 {url}")
    logger.info(f"使用音色: {speaker}, 格式: {format}")
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        raise RuntimeError(
            f"TTS 请求失败: HTTP {response.status_code}\n{response.text}"
        )
    
    # 响应是 NDJSON 格式（每行一个 JSON）
    import base64
    audio_chunks = []
    
    for line in response.text.strip().split("\n"):
        if not line:
            continue
        try:
            chunk = json.loads(line)
            code = chunk.get("code")
            
            # code=0 表示数据块，code=20000000 表示成功结束
            if code == 0:
                # 音频数据在 data 字段，Base64 编码
                if chunk.get("data"):
                    audio_chunks.append(base64.b64decode(chunk["data"]))
            elif code == 20000000:
                # 成功结束
                logger.debug("接收完成")
            else:
                # 错误
                raise RuntimeError(f"TTS 服务返回错误: {chunk}")
        except json.JSONDecodeError as e:
            logger.warning(f"解析 JSON 失败: {e}")
            continue
    
    if not audio_chunks:
        raise RuntimeError("未接收到音频数据")
    
    audio_data = b"".join(audio_chunks)
    
    logger.info(f"音频接收完成: {len(audio_data)} 字节 ({len(audio_data) / 1024:.2f} KB)")
    return audio_data


def main():
    parser = argparse.ArgumentParser(description="火山引擎 TTS REST API 合成")
    parser.add_argument("--text-file", default="script.txt", help="输入文本文件")
    parser.add_argument("--output", default="output.mp3", help="输出音频文件")
    parser.add_argument(
        "--speaker",
        default="zh_male_beijingxiaoye_emo_v2_mars_bigtts",
        help="音色（默认男声，可选 zh_female_cancan_mars_bigtts）",
    )
    parser.add_argument("--format", default="mp3", choices=["mp3", "wav"], help="音频格式")
    parser.add_argument("--sample-rate", type=int, default=24000, help="采样率")
    
    args = parser.parse_args()
    
    # 读取环境变量（使用 x-api-key）
    api_key = os.getenv("VOLC_API_KEY") or os.getenv("VOLC_AUTH_TOKEN")
    
    if not api_key:
        raise ValueError("请设置环境变量 VOLC_API_KEY 或 VOLC_AUTH_TOKEN")
    
    # 读取文本
    text_file = Path(args.text_file)
    if not text_file.exists():
        raise FileNotFoundError(f"文本文件不存在: {text_file}")
    
    text = text_file.read_text(encoding="utf-8").strip()
    logger.info(f"读取文本: {len(text)} 字符")
    
    # 人工确认
    print("\n" + "="*60)
    print(f"即将使用以下配置生成音频：")
    print(f"  文本文件: {text_file}")
    print(f"  文本长度: {len(text)} 字符")
    print(f"  音色: {args.speaker}")
    print(f"  输出文件: {args.output}")
    print("="*60)
    
    confirm = input("\n请确认脚本内容无误后继续 (输入 yes 继续): ").strip().lower()
    if confirm != "yes":
        print("已取消音频生成")
        return
    
    print("\n开始生成音频...\n")
    
    # 合成音频
    audio_data = synthesize_tts(
        api_key=api_key,
        text=text,
        speaker=args.speaker,
        format=args.format,
        sample_rate=args.sample_rate,
    )
    
    # 保存文件
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(audio_data)
    
    logger.info(f"音频已保存: {output_path}")


if __name__ == "__main__":
    main()
