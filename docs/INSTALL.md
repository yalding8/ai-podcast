# 安装指南

## 快速安装

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入API密钥

# 4. 测试安装
pytest -v
```

## 常见问题

### lxml编译失败

**错误：** `error: command '/usr/bin/clang' failed`

**解决：** 已从requirements.txt移除lxml，使用html.parser替代

### 其他依赖问题

```bash
# 最小化安装（仅核心功能）
pip install requests feedparser beautifulsoup4 websocket-client

# 添加LLM支持
pip install openai anthropic

# 添加测试工具
pip install pytest pytest-cov
```

## 验证安装

```bash
# 测试RSS采集
python ai_poadcast_main/collect_rss_feeds.py

# 运行单元测试
pytest

# 测试完整流程
python ai_poadcast_main/daily_workflow.py --dry-run
```
