# AI Podcast - 国际教育新闻播客自动化系统

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

将国际教育新闻自动转化为播客节目的完整工具链。

## ✨ 特性

- 📰 **自动采集**：RSS源、网页抓取、API集成
- 📝 **智能提取**：LLM驱动的要点卡片生成
- 🎙️ **脚本生成**：专业播客脚本自动创作
- 🔊 **音频合成**：多TTS引擎支持（讯飞/火山/Edge）
- 🏗️ **模块化架构**：依赖注入、配置管理、易测试

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/ai-poadcast.git
cd ai-poadcast

# 安装依赖
pip install -e .

# 可选：安装LLM和TTS支持
pip install -e ".[llm,tts]"
```

### 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
vim .env
```

### 使用

```bash
# 导入新闻
python -m ai_poadcast.cli import \
  --title "新闻标题" \
  --url "https://..." \
  --fetch

# 或使用旧脚本（兼容）
python ai_poadcast_main/import_raw_story.py --title "..." --url "..."
```

## 📁 项目结构

```
ai_poadcast/              # 新架构（模块化）
├── core/                 # 核心功能（档案、索引）
├── collectors/           # 新闻采集（RSS、网页）
├── processors/           # 内容处理（提取、校验）
├── generators/           # 脚本生成（Prompt、LLM）
├── llm/                  # LLM客户端（OpenAI、Anthropic、DeepSeek）
├── utils/                # 工具函数
├── config.py             # 统一配置
└── cli.py                # 命令行入口

ai_poadcast_main/         # 旧脚本（保持兼容）
├── import_raw_story.py   # 原文导入
├── collect_rss_feeds.py  # RSS采集
├── daily_workflow.py     # 每日流水线
└── ...

docs/                     # 文档
├── guides/               # 使用指南
└── archive/              # 历史文档
```

## 📖 文档

- [快速入门](START_HERE.md) - 5分钟上手
- [完整指南](README.md) - 详细操作手册
- [重构指南](REFACTOR_GUIDE.md) - 新旧架构对比
- [依赖注入](DEPENDENCY_INJECTION.md) - 架构设计
- [配置管理](CONFIG_MANAGEMENT.md) - 环境配置

## 🏗️ 架构亮点

### 依赖注入

```python
# 旧方式：硬编码
client = OpenAI()

# 新方式：依赖注入
from ai_poadcast.llm import create_llm_client
from ai_poadcast.generators.script import ScriptGenerator

llm = create_llm_client(provider="deepseek")
generator = ScriptGenerator(llm)
```

### 统一配置

```python
# 旧方式：分散配置
api_key = os.getenv("OPENAI_API_KEY")

# 新方式：统一配置
from ai_poadcast.config import settings
api_key = settings.openai_api_key
```

## 🔧 工作流

```
Stage 0: 新闻采集 → Stage 1: 原文导入 → Stage 2: 要点提取
    ↓
Stage 3: 脚本生成 → Stage 4: QA审核 → Stage 5: 音频合成
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可

MIT License

## 🙏 致谢

- OpenAI / Anthropic / DeepSeek - LLM支持
- 讯飞 / 火山引擎 - TTS服务
- BeautifulSoup / Pydantic - 核心依赖
