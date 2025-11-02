#!/usr/bin/env python3
"""
讯飞在线语音合成（TTS）客户端
支持流式合成、多发音人、SSML控制

环境变量：
- XUNFEI_APP_ID: d018e2dc（必填）
- XUNFEI_API_SECRET: MWExMTNmYmIyYzUzZjRkMmUzMTNlZWNm（必填）
- XUNFEI_API_KEY: c90405383bccbb7dd5f93e9d940dca91（必填）

使用示例：
    python tts_xunfei.py --text-file 脚本输出/2025-10-29/episode_2025-10-29_final.md \\
        --output audio_exports/2025/episode_2025-10-29_xiaoyan.mp3 \\
        --voice xiaoyan --speed 50

支持的发音人：
    xiaoyan(普通话女声) / aisjiuxu(四川话) / aisjinger(东北话) 等
    完整列表见：https://www.xfyun.cn/services/online_tts
"""

import os
import sys
import time
import json
import hmac
import base64
import hashlib
import argparse
import websocket
from datetime import datetime
from urllib.parse import urlencode
from pathlib import Path

class XunfeiTTS:
    """讯飞TTS WebSocket客户端"""
    
    def __init__(self, app_id, api_secret, api_key):
        self.app_id = app_id
        self.api_secret = api_secret
        self.api_key = api_key
        self.ws_url = "wss://tts-api.xfyun.cn/v2/tts"
        self.audio_chunks = []
        
    def create_auth_url(self):
        """生成带鉴权的WebSocket URL"""
        # RFC1123格式时间戳
        now = datetime.now()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 拼接签名原文
        signature_origin = f"host: ws-api.xfyun.cn\n"
        signature_origin += f"date: {date}\n"
        signature_origin += f"GET /v2/tts HTTP/1.1"
        
        # 生成签名
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature_sha = base64.b64encode(signature_sha).decode('utf-8')
        
        # 构造authorization
        authorization_origin = (
            f'api_key="{self.api_key}", '
            f'algorithm="hmac-sha256", '
            f'headers="host date request-line", '
            f'signature="{signature_sha}"'
        )
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        
        # 拼接最终URL
        params = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        return f"{self.ws_url}?{urlencode(params)}"
    
    def synthesize(self, text, voice="xiaoyan", speed=50, volume=50, 
                   pitch=50, audio_format="lame", sample_rate=16000,
                   max_retries=3, retry_base_delay=1):
        """
        合成语音
        
        Args:
            text: 待合成文本（建议<8000字，超长需分段）
            voice: 发音人（xiaoyan/aisjiuxu/xiaoyu等）
            speed: 语速 0-100，默认50
            volume: 音量 0-100，默认50
            pitch: 音高 0-100，默认50
            audio_format: 音频格式（raw/lame/speex），推荐lame(mp3)
            sample_rate: 采样率（8000/16000/24000）
        
        Returns:
            bytes: 音频数据（mp3格式）
        """
        retry_delay = max(0.5, retry_base_delay)
        for attempt in range(1, max_retries + 1):
            self.audio_chunks = []
            error_message = None
            completed = False
            
            def on_open(ws):
                """WebSocket连接建立"""
                print(f"[XunfeiTTS] 连接成功，开始合成（发音人：{voice}，语速：{speed}）")
                
                # 构造请求参数
                params = {
                    "common": {"app_id": self.app_id},
                    "business": {
                        "aue": audio_format,  # lame=mp3, raw=wav
                        "auf": f"audio/L16;rate={sample_rate}",
                        "vcn": voice,
                        "speed": speed,
                        "volume": volume,
                        "pitch": pitch,
                        "bgs": 0,  # 背景音（0=无，1=有）
                        "tte": "UTF8"  # 文本编码
                    },
                    "data": {
                        "status": 2,  # 2=一次性传输
                        "text": base64.b64encode(text.encode('utf-8')).decode('utf-8')
                    }
                }
                ws.send(json.dumps(params))
            
            def on_message(ws, message):
                """接收合成结果"""
                nonlocal error_message, completed
                try:
                    data = json.loads(message)
                    code = data.get("code")
                    
                    if code != 0:
                        error_msg = data.get("message", "未知错误")
                        error_message = f"错误 {code}: {error_msg}"
                        ws.close()
                        return
                    
                    # 提取音频数据
                    audio_base64 = data.get("data", {}).get("audio")
                    if audio_base64:
                        audio_data = base64.b64decode(audio_base64)
                        self.audio_chunks.append(audio_data)
                    
                    # 检查是否完成
                    status = data.get("data", {}).get("status")
                    if status == 2:  # 2=合成完成
                        completed = True
                        print(f"[XunfeiTTS] ✅ 合成完成，共 {len(self.audio_chunks)} 段")
                        ws.close()
                        
                except Exception as e:
                    error_message = f"处理消息时出错: {e}"
                    ws.close()
            
            def on_error(ws, error):
                nonlocal error_message
                if not error_message:
                    error_message = f"WebSocket错误: {error}"
            
            def on_close(ws, close_status_code, close_msg):
                nonlocal error_message
                if close_status_code and close_status_code != 1000 and not error_message:
                    error_message = f"连接关闭，状态码 {close_status_code}"
            
            # 建立WebSocket连接
            ws_url = self.create_auth_url()
            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            ws.run_forever()
            
            if error_message or not completed or not self.audio_chunks:
                reason = error_message or "未收到合成结果"
                if attempt == max_retries:
                    raise RuntimeError(reason)
                sleep_seconds = retry_delay
                print(f"[XunfeiTTS] ⚠️ 第 {attempt} 次合成失败：{reason}，将在 {sleep_seconds} 秒后重试")
                time.sleep(sleep_seconds)
                retry_delay *= 2
                continue
            
            # 合并音频块
            return b"".join(self.audio_chunks)
        
        raise RuntimeError("合成失败：超过最大重试次数")


def split_text(text, max_length=4000):
    """
    分段处理长文本
    
    Args:
        text: 原始文本
        max_length: 每段最大字符数（讯飞建议<8000，保险起见用4000）
    
    Returns:
        list: 文本片段列表
    """
    if len(text) <= max_length:
        return [text]
    
    segments = []
    # 按段落分割
    paragraphs = text.split('\n\n')
    
    current_segment = ""
    for para in paragraphs:
        if len(current_segment) + len(para) + 2 <= max_length:
            current_segment += para + "\n\n"
        else:
            if current_segment:
                segments.append(current_segment.strip())
            current_segment = para + "\n\n"
    
    if current_segment:
        segments.append(current_segment.strip())
    
    return segments


def main():
    parser = argparse.ArgumentParser(description='讯飞TTS语音合成工具')
    parser.add_argument('--text', type=str, help='待合成文本（直接输入）')
    parser.add_argument('--text-file', type=str, help='文本文件路径')
    parser.add_argument('--output', type=str, required=True, help='输出音频路径（.mp3）')
    parser.add_argument('--voice', type=str, default='xiaoyan', 
                       help='发音人（默认：xiaoyan）')
    parser.add_argument('--speed', type=int, default=50, 
                       help='语速 0-100（默认：50）')
    parser.add_argument('--volume', type=int, default=50, 
                       help='音量 0-100（默认：50）')
    parser.add_argument('--pitch', type=int, default=50, 
                       help='音高 0-100（默认：50）')
    parser.add_argument('--segment-size', type=int, default=4000,
                       help='分段合成的最大字符数（默认：4000）')
    parser.add_argument('--max-retries', type=int, default=3,
                       help='每段合成失败后的最大重试次数（默认：3）')
    parser.add_argument('--retry-delay', type=float, default=1.0,
                       help='首次重试的等待秒数，之后指数退避（默认：1.0）')
    
    args = parser.parse_args()
    
    # 获取环境变量
    app_id = os.getenv('XUNFEI_APP_ID')
    api_secret = os.getenv('XUNFEI_API_SECRET')
    api_key = os.getenv('XUNFEI_API_KEY')
    
    if not all([app_id, api_secret, api_key]):
        print("❌ 请设置环境变量：XUNFEI_APP_ID, XUNFEI_API_SECRET, XUNFEI_API_KEY")
        print("获取方式：https://console.xfyun.cn/services/tts")
        sys.exit(1)
    
    # 读取文本
    if args.text:
        text = args.text
    elif args.text_file:
        with open(args.text_file, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        print("❌ 请提供 --text 或 --text-file 参数")
        sys.exit(1)
    
    # 清理文本（移除Markdown标记）
    text = text.replace('#', '').replace('*', '').replace('`', '')
    text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
    
    print(f"[XunfeiTTS] 文本长度：{len(text)} 字符")
    
    # 初始化客户端
    tts = XunfeiTTS(app_id, api_secret, api_key)
    
    # 分段合成
    if args.segment_size <= 0:
        print("❌ --segment-size 必须为正整数")
        sys.exit(1)
    if args.max_retries < 1:
        print("❌ --max-retries 至少为 1")
        sys.exit(1)
    if args.retry_delay <= 0:
        print("❌ --retry-delay 必须为正数")
        sys.exit(1)
    
    segments = split_text(text, max_length=args.segment_size)
    print(f"[XunfeiTTS] 分为 {len(segments)} 段合成")
    
    all_audio = []
    try:
        for i, segment in enumerate(segments, 1):
            print(f"\n[XunfeiTTS] 正在合成第 {i}/{len(segments)} 段...")
            try:
                audio_data = tts.synthesize(
                    text=segment,
                    voice=args.voice,
                    speed=args.speed,
                    volume=args.volume,
                    pitch=args.pitch,
                    max_retries=args.max_retries,
                    retry_base_delay=args.retry_delay
                )
            except RuntimeError as e:
                print(f"[XunfeiTTS] ❌ 合成失败：{e}")
                sys.exit(1)
            all_audio.append(audio_data)
            time.sleep(0.5)  # 避免频率过高
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断，已停止合成")
        sys.exit(130)
    
    # 保存音频
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        for audio in all_audio:
            f.write(audio)
    
    print(f"\n✅ 音频已保存至：{output_path}")
    print(f"   文件大小：{output_path.stat().st_size / 1024:.2f} KB")


if __name__ == '__main__':
    main()

