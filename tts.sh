#!/bin/bash
# 讯飞TTS快捷启动脚本

# 加载环境变量
export XUNFEI_APP_ID="你的APPID"
export XUNFEI_API_SECRET="你的APISecret"
export XUNFEI_API_KEY="你的APIKey"

# 调用Python脚本，传递所有参数
python tts_xunfei.py "$@"
