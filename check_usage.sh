#!/bin/bash
# 检查讯飞TTS使用量

echo "=== 讯飞TTS使用统计 ==="
echo ""

# 统计今天生成的音频数量
TODAY=$(date +%Y-%m-%d)
AUDIO_DIR="audio_exports/$(date +%Y)"

if [ -d "$AUDIO_DIR" ]; then
    count=$(find "$AUDIO_DIR" -name "*$(date +%Y-%m-%d)*" -type f | wc -l | tr -d ' ')
    echo "今日已生成音频: $count 个"
    
    if [ $count -lt 500 ]; then
        echo "✅ 剩余免费额度: $((500 - count)) 次"
    else
        echo "⚠️  已超出免费额度，可能产生费用"
    fi
else
    echo "今日已生成音频: 0 个"
    echo "✅ 剩余免费额度: 500 次"
fi

echo ""
echo "提示: 讯飞免费额度为 500次/天"
