#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
from volcengine.tts.TtsService import TtsService
from config import VOLCENGINE_APPID, VOLCENGINE_ACCESS_KEY

# 初始化
tts_service = TtsService()
tts_service.set_app_id(VOLCENGINE_APPID)
tts_service.set_token(VOLCENGINE_ACCESS_KEY)

# 测试文本
TEXT = """
大家好，欢迎收听《国际教育周报》。
今天我们要聊的是英国PSW签证延长的消息。
"""

# 构建请求
request = {
    'app': {
        'appid': VOLCENGINE_APPID,
        'token': VOLCENGINE_ACCESS_KEY,
        'cluster': 'volcano_tts'
    },
    'user': {
        'uid': 'test_user'
    },
    'audio': {
        'voice_type': 'BV700_V2_streaming',  # 灿灿
        'encoding': 'mp3',
        'speed_ratio': 0.9,
        'volume_ratio': 1.0,
        'pitch_ratio': 1.0,
    },
    'request': {
        'reqid': str(uuid.uuid4()),
        'text': TEXT,
        'text_type': 'plain',
        'operation': 'submit'
    }
}

# 生成音频
print("🎙️ 开始生成...")
response = tts_service.standard_tts(request)

# 保存文件
with open("test.mp3", 'wb') as f:
    f.write(response['data'])

print("✅ 成功！文件：test.mp3")
print(f"💰 费用：¥{len(TEXT) * 0.0002:.4f}")