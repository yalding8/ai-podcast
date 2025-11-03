#!/bin/bash
# 生成不同音色的试听样本

set -a
[ -f .env ] && . ./.env
set +a

SAMPLE_TEXT="大家好，欢迎收听异乡早咖啡，我是大刘。今天是2025年11月3日，我们将在8分钟内快速带你盘点国际教育领域的重磅动态。本期我们聚焦三个关键词：女性领导力、名校路径、长学制规划。"

OUTPUT_DIR="audio_exports/voice_samples"
mkdir -p "$OUTPUT_DIR"

echo "$SAMPLE_TEXT" > /tmp/voice_sample.txt

echo "🎙️ 生成音色试听样本..."
echo ""

# 男性音色
echo "1️⃣ 生成：传统男性新闻播报（傲娇霸总）..."
python tts_volcengine_rest.py \
  --text-file /tmp/voice_sample.txt \
  --speaker zh_male_aojiaobazong_moon_bigtts \
  --output "$OUTPUT_DIR/01_male_news_aojiaobazong.mp3" <<< "yes"

echo ""
echo "2️⃣ 生成：北京小爷（情感丰富）..."
python tts_volcengine_rest.py \
  --text-file /tmp/voice_sample.txt \
  --speaker zh_male_beijingxiaoye_emo_v2_mars_bigtts \
  --output "$OUTPUT_DIR/02_male_beijingxiaoye.mp3" <<< "yes"

echo ""
echo "3️⃣ 生成：清厚少爷（磁性温和）..."
python tts_volcengine_rest.py \
  --text-file /tmp/voice_sample.txt \
  --speaker zh_male_qinghoushaoye_moon_bigtts \
  --output "$OUTPUT_DIR/03_male_qinghoushaoye.mp3" <<< "yes"

echo ""
echo "4️⃣ 生成：醇厚大叔..."
python tts_volcengine_rest.py \
  --text-file /tmp/voice_sample.txt \
  --speaker zh_male_chunhoudashu_moon_bigtts \
  --output "$OUTPUT_DIR/04_male_chunhoudashu.mp3" <<< "yes"

# 女性音色
echo ""
echo "5️⃣ 生成：甜美女声（灿灿）..."
python tts_volcengine_rest.py \
  --text-file /tmp/voice_sample.txt \
  --speaker zh_female_cancan_mars_bigtts \
  --output "$OUTPUT_DIR/05_female_cancan.mp3" <<< "yes"

echo ""
echo "6️⃣ 生成：爽快女声（思思）..."
python tts_volcengine_rest.py \
  --text-file /tmp/voice_sample.txt \
  --speaker zh_female_shuangkuaisisi_moon_bigtts \
  --output "$OUTPUT_DIR/06_female_shuangkuaisisi.mp3" <<< "yes"

echo ""
echo "7️⃣ 生成：温婉女声（小荷）..."
python tts_volcengine_rest.py \
  --text-file /tmp/voice_sample.txt \
  --speaker zh_female_wanwanxiaohe_moon_bigtts \
  --output "$OUTPUT_DIR/07_female_wanwanxiaohe.mp3" <<< "yes"

echo ""
echo "✅ 所有样本生成完成！"
echo ""
echo "📂 试听文件位置: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR"/*.mp3

rm /tmp/voice_sample.txt
