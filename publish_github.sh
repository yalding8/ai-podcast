#!/bin/bash
# 快速发布到GitHub脚本

set -e

echo "🚀 准备发布到GitHub..."
echo ""

# 检查是否已初始化Git
if [ ! -d .git ]; then
    echo "📦 初始化Git仓库..."
    git init
    git branch -M main
fi

# 检查敏感文件
echo "🔒 检查敏感信息..."
if git ls-files | grep -q "^\.env$"; then
    echo "❌ 错误: .env文件在Git中，请先移除！"
    echo "运行: git rm --cached .env"
    exit 1
fi

# 显示将要提交的文件
echo ""
echo "📋 将要提交的文件："
git status --short

echo ""
read -p "确认提交这些文件？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 1
fi

# 添加所有文件
echo ""
echo "📝 添加文件..."
git add .

# 提交
echo ""
read -p "输入提交信息: " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="Update: $(date +%Y-%m-%d)"
fi

git commit -m "$commit_msg"

# 检查远程仓库
if ! git remote | grep -q origin; then
    echo ""
    echo "🔗 未配置远程仓库"
    read -p "输入GitHub仓库URL (如: https://github.com/username/ai-podcast.git): " repo_url
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        echo "✅ 已添加远程仓库"
    else
        echo "⚠️ 未添加远程仓库，请手动运行:"
        echo "   git remote add origin <URL>"
        exit 0
    fi
fi

# 推送
echo ""
echo "📤 推送到GitHub..."
git push -u origin main

echo ""
echo "✅ 发布完成！"
echo "🌐 访问: $(git remote get-url origin | sed 's/\.git$//')"
