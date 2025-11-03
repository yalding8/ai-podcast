#!/bin/bash
# 自动化功能演示脚本

echo "🎬 AI POADCAST 自动化功能演示"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 考试爬虫演示
echo -e "${BLUE}📚 演示 1: 考试官网爬虫${NC}"
echo "命令: python ai_poadcast_main/exam_sites_crawler.py"
echo ""
read -p "按回车继续..."
python ai_poadcast_main/exam_sites_crawler.py
echo ""

# 2. 音频处理演示
echo -e "${BLUE}🎵 演示 2: 音频后期处理${NC}"
echo "功能: 音量标准化、降噪、添加片头片尾、背景音乐"
echo ""
echo "示例命令:"
echo "  python audio_postprocess.py \\"
echo "    --input audio_exports/2025/episode_2025-10-29_xiaoyan.mp3 \\"
echo "    --output audio_exports/2025/episode_2025-10-29_final.mp3 \\"
echo "    --normalize-only"
echo ""
read -p "按回车继续..."
echo ""

# 3. 自动发布演示
echo -e "${BLUE}📡 演示 3: 自动发布工具${NC}"
echo "支持平台: 小宇宙、喜马拉雅、RSS Feed"
echo ""
echo "示例命令:"
echo "  python auto_publish.py \\"
echo "    --audio audio_exports/2025/episode_2025-11-03_final.mp3 \\"
echo "    --title '异乡早咖啡 2025-11-03' \\"
echo "    --description '今日国际教育资讯' \\"
echo "    --platforms rss"
echo ""
read -p "按回车继续..."
echo ""

# 4. CI/CD演示
echo -e "${BLUE}⚙️  演示 4: CI/CD流程${NC}"
echo "GitHub Actions配置文件: .github/workflows/podcast_pipeline.yml"
echo ""
echo "流程阶段:"
echo "  1. collect-news      - 采集新闻"
echo "  2. extract-summaries - 提取摘要"
echo "  3. generate-script   - 生成脚本"
echo "  4. synthesize-audio  - 合成音频"
echo "  5. publish-episode   - 发布节目"
echo ""
echo "定时运行: 每天UTC 00:00 (北京时间 08:00)"
echo "手动触发: GitHub Actions页面"
echo ""
read -p "按回车继续..."
echo ""

# 5. Makefile演示
echo -e "${BLUE}🛠️  演示 5: Makefile快捷命令${NC}"
echo ""
make help
echo ""
read -p "按回车继续..."
echo ""

# 总结
echo -e "${GREEN}✅ 演示完成！${NC}"
echo ""
echo "📖 详细文档:"
echo "  - AUTOMATION_GUIDE.md  - 完整使用指南"
echo "  - README.md            - 项目总览"
echo "  - INDEX.md             - 文档索引"
echo ""
echo "🚀 快速开始:"
echo "  make collect           - 采集新闻"
echo "  make full-pipeline     - 完整流水线"
echo "  python test_automation.py - 测试所有功能"
echo ""
