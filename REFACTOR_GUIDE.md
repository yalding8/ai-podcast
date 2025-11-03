# 重构指南

## 新架构概览

```
ai_poadcast/
├── __init__.py              # 包初始化
├── cli.py                   # 统一命令行入口
├── core/                    # 核心功能
│   ├── __init__.py
│   ├── archive.py          # 档案管理
│   └── index.py            # 索引管理
├── collectors/              # 新闻采集
│   ├── __init__.py
│   ├── rss.py              # RSS采集
│   └── web.py              # 网页抓取
├── processors/              # 内容处理
│   ├── __init__.py
│   ├── extractor.py        # 要点提取
│   └── validator.py        # 内容校验
├── generators/              # 脚本生成
│   ├── __init__.py
│   ├── prompt.py           # Prompt构建
│   └── script.py           # 脚本生成
└── utils/                   # 工具函数
    ├── __init__.py
    ├── text.py             # 文本处理
    └── date.py             # 日期处理
```

## 迁移步骤

### 阶段1：核心功能（已完成）
- [x] 创建基础目录结构
- [x] 实现 ArchiveManager（档案管理）
- [x] 实现 IndexManager（索引管理）
- [x] 实现 WebFetcher（网页抓取）
- [x] 实现 ContentValidator（内容校验）
- [x] 实现工具函数（text, date）
- [x] 创建统一CLI入口

### 阶段2：采集模块（待迁移）
从 `ai_poadcast_main/` 迁移：
- [ ] `collect_rss_feeds.py` → `collectors/rss.py`
- [ ] `feeds_config.py` → `collectors/config.py`
- [ ] `scrape_exam_sites.py` → `collectors/exam.py`

### 阶段3：处理模块（待迁移）
- [ ] `batch_extract.py` → `processors/extractor.py`
- [ ] Stage 2 提取逻辑

### 阶段4：生成模块（待迁移）
- [ ] `prepare_stage3_prompt.py` → `generators/prompt.py`
- [ ] `generate_stage3_script.py` → `generators/script.py`

### 阶段5：工作流整合（待迁移）
- [ ] `daily_workflow.py` → `cli.py` 子命令
- [ ] `process_queue.py` → 队列处理模块

## 使用方式

### 旧方式（保持兼容）
```bash
python ai_poadcast_main/import_raw_story.py --title "..." --url "..."
```

### 新方式（推荐）
```bash
python -m ai_poadcast.cli import --title "..." --url "..."
```

## 优势

1. **模块化**：职责清晰，易于维护
2. **可测试**：每个模块独立测试
3. **可扩展**：新增功能只需添加模块
4. **统一入口**：所有命令通过 `cli.py` 调用
5. **类型安全**：使用类型注解

## 向后兼容

- 保留 `ai_poadcast_main/` 中的原始脚本
- 新代码逐步迁移到 `ai_poadcast/`
- 两套系统并行运行，确保平滑过渡

## 下一步

1. 测试新CLI：`python -m ai_poadcast.cli import --help`
2. 迁移RSS采集逻辑
3. 添加单元测试
4. 更新文档
