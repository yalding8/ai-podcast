# 发布到GitHub指南

## 📋 发布前检查

### 1. 确认敏感信息已排除
```bash
# 检查.env文件不在仓库中
cat .gitignore | grep .env

# 确认没有API密钥泄露
grep -r "sk-" --include="*.py" . | grep -v ".env.example" | grep -v "示例"
```

### 2. 测试核心功能
```bash
# 测试新架构
python -m ai_poadcast.cli import --help
python examples/dependency_injection_demo.py

# 测试旧脚本兼容性
python ai_poadcast_main/import_raw_story.py --help
```

## 🚀 发布步骤

### 步骤1：初始化Git仓库
```bash
cd "/Users/ningding/Desktop/AI POADCAST"

# 初始化Git
git init

# 添加所有文件
git add .

# 首次提交
git commit -m "Initial commit: AI Podcast automation system v2.0

- 模块化架构（ai_poadcast/）
- 依赖注入（LLM客户端）
- 统一配置管理（Pydantic）
- 向后兼容（ai_poadcast_main/）
- 完整文档和示例"
```

### 步骤2：创建GitHub仓库

1. 访问 https://github.com/new
2. 填写信息：
   - Repository name: `ai-podcast`
   - Description: `国际教育新闻播客自动化系统 - 将新闻自动转化为播客节目`
   - Public/Private: 选择
   - 不要勾选 "Initialize with README"（已有README.md）

### 步骤3：关联远程仓库
```bash
# 添加远程仓库（替换为你的用户名）
git remote add origin https://github.com/YOUR_USERNAME/ai-podcast.git

# 或使用SSH
git remote add origin git@github.com:YOUR_USERNAME/ai-podcast.git

# 验证远程仓库
git remote -v
```

### 步骤4：推送到GitHub
```bash
# 重命名分支为main
git branch -M main

# 推送到GitHub
git push -u origin main
```

### 步骤5：添加标签
```bash
# 创建版本标签
git tag -a v2.0.0 -m "Version 2.0.0 - Modular architecture with dependency injection"

# 推送标签
git push origin v2.0.0
```

## ⚙️ GitHub仓库设置

### About部分
```
Description: 国际教育新闻播客自动化系统 - 将新闻自动转化为播客节目
Website: （如有）
Topics: python, podcast, automation, llm, tts, news, education, rss
```

### 分支保护（可选）
Settings → Branches → Add rule
- Branch name pattern: `main`
- ✅ Require pull request reviews before merging

## 📝 后续维护

### 日常提交
```bash
# 查看状态
git status

# 添加更改
git add .

# 提交
git commit -m "描述更改内容"

# 推送
git push
```

### 创建新版本
```bash
# 更新版本号
git tag -a v2.1.0 -m "Version 2.1.0 - 新功能描述"
git push origin v2.1.0
```

### 创建Release
1. 访问 https://github.com/YOUR_USERNAME/ai-podcast/releases
2. 点击 "Draft a new release"
3. 选择标签（如 v2.0.0）
4. 填写标题和说明
5. 发布

## 🔒 安全提醒

### 已忽略的敏感文件
- `.env` - 环境变量（包含API密钥）
- `source_archive/` - 原文档案
- `audio_exports/` - 音频文件
- `脚本输出/` - 生成的脚本
- `要点卡片/` - 要点卡片

### 如果不小心提交了敏感信息
```bash
# 从历史中删除文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin --force --all
```

## 📊 推荐的GitHub Actions（可选）

创建 `.github/workflows/test.yml`：
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -e .
      - run: pytest tests/
```

## ✅ 完成检查

- [ ] Git仓库已初始化
- [ ] 远程仓库已关联
- [ ] 代码已推送到GitHub
- [ ] 版本标签已创建
- [ ] README.md显示正常
- [ ] .gitignore生效（敏感文件未上传）
- [ ] About信息已填写
- [ ] Topics已添加

## 🎉 发布完成！

仓库地址：`https://github.com/YOUR_USERNAME/ai-podcast`

分享给其他人：
```bash
git clone https://github.com/YOUR_USERNAME/ai-podcast.git
cd ai-podcast
pip install -e .
```
