# AI Podcast - 国际教育新闻播客自动化系统

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

将国际教育新闻自动转化为播客节目的完整工具链。

## ✨ 特性

- 📰 **自动采集**：RSS源、网页抓取、API集成
- 📝 **智能提取**：LLM驱动的要点卡片生成
- 🎙️ **脚本生成**：专业播客脚本自动创作
- 🔊 **音频合成**：多TTS引擎支持（讯飞/火山）
- 🏗️ **模块化架构**：依赖注入、配置管理、易测试

## 🚀 快速开始

### 1. 安装

```bash
git clone https://github.com/yalding8/ai-podcast.git
cd ai-podcast
pip install -e .
```

### 2. 配置

```bash
cp .env.example .env
vim .env  # 配置 API 密钥
```

必须配置：
- `DEEPSEEK_API_KEY` 或 `OPENAI_API_KEY` - LLM服务
- `VOLC_API_KEY` - 火山引擎 TTS

### 3. 一键运行

```bash
make full-pipeline
```

这会自动执行：
1. 采集RSS新闻
2. 提取要点卡片
3. 生成播客脚本
4. 合成音频
5. 后期处理
6. 发布RSS Feed

### 4. 分步执行

```bash
make collect   # 只采集新闻
make extract   # 只提取要点
make script    # 只生成脚本
make audio     # 只合成音频
```

详细安装指南见 [docs/INSTALL.md](docs/INSTALL.md)

## 📁 项目结构

```
ai_poadcast/              # 新架构（模块化）
├── core/                 # 核心功能（档案、索引）
├── collectors/           # 新闻采集（RSS、网页）
├── processors/           # 内容处理（提取、校验）
├── generators/           # 脚本生成（Prompt、LLM）
├── llm/                  # LLM客户端（OpenAI、Anthropic、DeepSeek）
└── utils/                # 工具函数

ai_poadcast_main/         # 旧脚本（保持兼容）
├── import_raw_story.py   # 原文导入
├── collect_rss_feeds.py  # RSS采集
├── daily_workflow.py     # 每日流水线
└── generate_stage3_script.py  # 脚本生成

docs/                     # 文档
├── INSTALL.md            # 安装指南
├── ARCHITECTURE.md       # 架构设计
└── guides/               # 使用指南
```

## 📖 文档

- [安装指南](docs/INSTALL.md) - 详细安装步骤
- [架构设计](docs/ARCHITECTURE.md) - 系统架构
- [TTS配置](docs/guides/volcengine_tts_complete_guide.md) - 音频合成
- [优质源](docs/guides/QUALITY_SOURCES.md) - 新闻源配置

## 🔧 工作流

```
Stage 0: 新闻采集 → Stage 1: 原文导入 → Stage 2: 要点提取
    ↓
Stage 3: 脚本生成 → Stage 4: QA审核 → Stage 5: 音频合成
```

## 🎯 核心功能

### LLM 自动切换
当主要LLM服务不可用时，自动切换到备用服务：
```
DeepSeek (503) → OpenAI → Anthropic
```

### 文本过滤
自动过滤脚本中的注释和说明：
- 以 `#` 开头的注释行
- `**脚本说明**` 区域

### 音色选择
默认使用北京小爷音色（情感丰富、亲切自然），可通过 `--speaker` 参数切换。

## 🤝 贡献

欢迎提交Issue和Pull Request！详见 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 许可

MIT License

## 🙏 致谢

- OpenAI / Anthropic / DeepSeek - LLM支持
- 火山引擎 / 讯飞 - TTS服务
- BeautifulSoup / Pydantic - 核心依赖
