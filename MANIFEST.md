# 项目文件清单

## 核心文件（必需）

### 根目录
- README.md - 项目主文档
- START_HERE.md - 快速入门
- LICENSE - MIT许可证
- .gitignore - Git忽略规则
- .env.example - 环境变量模板
- setup.py - 安装配置
- requirements.txt - Python依赖

### 新架构（ai_poadcast/）
- ai_poadcast/ - 模块化包
  - core/ - 核心功能
  - collectors/ - 数据采集
  - processors/ - 内容处理
  - generators/ - 脚本生成
  - llm/ - LLM客户端
  - utils/ - 工具函数
  - config.py - 配置管理
  - cli.py - 命令行入口

### 旧脚本（ai_poadcast_main/）
- import_raw_story.py - 原文导入
- collect_rss_feeds.py - RSS采集
- daily_workflow.py - 每日流水线
- generate_stage3_script.py - 脚本生成
- 其他工具脚本...

### TTS工具
- tts_xunfei.py - 讯飞TTS
- tts_volcengine.py - 火山TTS
- test_tts.py - TTS测试

## 文档（docs/）
- docs/README_FULL.md - 完整操作手册
- docs/ARCHITECTURE.md - 架构设计
- docs/guides/ - 使用指南
- docs/archive/ - 历史文档

## 重构文档
- REFACTOR_GUIDE.md - 重构指南
- DEPENDENCY_INJECTION.md - 依赖注入
- CONFIG_MANAGEMENT.md - 配置管理
- CONTRIBUTING.md - 贡献指南

## 示例（examples/）
- dependency_injection_demo.py
- config_usage_demo.py

## 测试（tests/）
- test_dependency_injection.py
- test_core_functions.py

## 归档（legacy/）
- 旧版本文件
- 临时脚本

## 数据目录（.gitignore）
- source_archive/ - 原文档案
- audio_exports/ - 音频输出
- 脚本输出/ - 脚本文件
- 要点卡片/ - 要点卡片
