#!/bin/bash

# 国际教育播客系统 - 一键启动脚本 (Mac修复版)

set -e  # 遇到错误立即退出

echo "=================================================="
echo "  国际教育播客系统 - 快速启动向导"
echo "=================================================="
echo ""

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 项目目录: $SCRIPT_DIR"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装"
    exit 1
fi

echo "✅ Python3已安装: $(python3 --version)"

# 检查依赖
echo ""
echo "检查Python依赖..."
python3 -c "import requests" 2>/dev/null || {
    echo "📦 安装requests库..."
    pip3 install requests
}

echo "✅ 依赖检查完成"

# 选择运行模式
echo ""
echo "=================================================="
echo "请选择运行模式:"
echo "=================================================="
echo "1) 快速演示 (无需API密钥，使用模拟数据)"
echo "2) 测试GDELT API (完全免费)"
echo "3) 测试NewsCatcher API (需要密钥)"
echo "4) 部署RSSHub服务 (需要Docker)"
echo "5) 查看使用文档"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 启动快速演示..."
        echo ""
        python3 "$SCRIPT_DIR/scripts/integrated_demo.py"
        echo ""
        echo "=================================================="
        echo "✅ 演示完成！查看生成的文件:"
        echo "=================================================="
        ls -lh "$SCRIPT_DIR/data/"
        echo ""
        echo "💡 提示: 使用以下命令查看报告"
        echo "   cat data/report_*.md"
        ;;
    2)
        echo ""
        echo "🌍 测试GDELT API (完全免费)..."
        echo ""
        python3 "$SCRIPT_DIR/scripts/test_gdelt.py"
        ;;
    3)
        echo ""
        read -p "请输入NewsCatcher API密钥: " api_key
        export NEWSCATCHER_API_KEY="$api_key"
        echo ""
        echo "🔍 测试NewsCatcher API..."
        echo ""
        python3 "$SCRIPT_DIR/scripts/test_newscatcher.py"
        ;;
    4)
        if ! command -v docker &> /dev/null; then
            echo "❌ 未找到Docker，请先安装"
            echo "   下载地址: https://www.docker.com/products/docker-desktop"
            exit 1
        fi
        
        echo ""
        echo "🐳 启动RSSHub服务..."
        echo ""
        docker-compose up -d
        
        echo ""
        echo "=================================================="
        echo "✅ RSSHub已启动！"
        echo "=================================================="
        echo "访问地址: http://localhost:1200"
        echo ""
        echo "查看日志: docker logs podcast-rsshub"
        echo "停止服务: docker-compose down"
        ;;
    5)
        echo ""
        echo "📚 查看文档..."
        echo ""
        if [ -f "$SCRIPT_DIR/readme.md" ]; then
            cat "$SCRIPT_DIR/readme.md"
        elif [ -f "$SCRIPT_DIR/README.md" ]; then
            cat "$SCRIPT_DIR/README.md"
        else
            echo "❌ 未找到README文档"
        fi
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "🎉 感谢使用！"
echo "=================================================="
echo ""
echo "📖 更多帮助:"
echo "   - 完整文档: cat readme.md"
echo "   - 信息源配置: cat \"news sources.md\""
echo "   - RSSHub指南: cat RSSHUB_GUIDE.md"
echo ""