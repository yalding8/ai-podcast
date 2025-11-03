# 文档索引

## 📚 核心文档

### 入门
- [../README.md](../README.md) - 项目主页和快速开始
- [INSTALL.md](INSTALL.md) - 详细安装指南

### 架构
- [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构设计

## 📖 使用指南

### TTS 配置
- [guides/volcengine_tts_complete_guide.md](guides/volcengine_tts_complete_guide.md) - 火山引擎 TTS 完整指南
- [guides/XUNFEI_TTS_SETUP.md](guides/XUNFEI_TTS_SETUP.md) - 讯飞 TTS 配置

### 新闻源
- [guides/QUALITY_SOURCES.md](guides/QUALITY_SOURCES.md) - 优质新闻源配置

### 快速参考
- [guides/QUICK_REFERENCE.md](guides/QUICK_REFERENCE.md) - 常用命令速查
- [guides/QUICK_START_QUALITY.md](guides/QUICK_START_QUALITY.md) - 质量控制快速开始

## 🔧 工具脚本

### Makefile 命令
```bash
make help          # 查看所有命令
make full-pipeline # 完整流水线
make collect       # 采集新闻
make extract       # 提取要点
make script        # 生成脚本
make audio         # 合成音频
make clean         # 清理临时文件
```

### Python 脚本
```bash
# 采集新闻
python ai_poadcast_main/collect_rss_feeds.py

# 每日流水线
python ai_poadcast_main/daily_workflow.py

# 生成脚本
python ai_poadcast_main/generate_stage3_script.py --date 2025-11-03

# 合成音频
python tts_volcengine_rest.py --text-file script.txt --output audio.mp3
```

## 📦 项目结构

```
ai-podcast/
├── ai_poadcast/              # 新架构（模块化）
├── ai_poadcast_main/         # 旧脚本（兼容）
├── docs/                     # 文档（当前目录）
├── audio_exports/            # 音频输出
├── source_archive/           # 新闻归档
├── 脚本输出/                 # 脚本输出
├── 要点卡片/                 # 要点卡片
├── Makefile                  # 构建脚本
├── .env.example              # 环境变量模板
└── README.md                 # 项目主页
```

## 🔗 外部资源

- [GitHub 仓库](https://github.com/yalding8/ai-podcast)
- [火山引擎 TTS 文档](https://www.volcengine.com/docs/6561/97465)
- [讯飞 TTS 文档](https://www.xfyun.cn/doc/tts/online_tts/API.html)

## 📝 更新日志

查看 [archive/](../archive/) 目录了解历史更新记录。
