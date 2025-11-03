# 架构设计

## 设计原则

1. **模块化**：职责单一，松耦合
2. **依赖注入**：便于测试和扩展
3. **配置驱动**：统一配置管理
4. **向后兼容**：保留旧脚本

## 核心模块

### core - 核心功能
- `ArchiveManager`：原文档案管理
- `IndexManager`：索引管理

### collectors - 数据采集
- `WebFetcher`：网页抓取
- `RSSCollector`：RSS源采集

### processors - 内容处理
- `SummaryExtractor`：要点提取
- `ContentValidator`：内容校验

### generators - 脚本生成
- `PromptBuilder`：Prompt构建
- `ScriptGenerator`：脚本生成（依赖注入）

### llm - LLM客户端
- `OpenAIClient`：OpenAI接口
- `AnthropicClient`：Anthropic接口
- `DeepSeekClient`：DeepSeek接口
- `create_llm_client()`：工厂函数

### utils - 工具函数
- `slugify()`：文本转slug
- `parse_date()`：日期解析
- `clean_markdown()`：清理Markdown

## 数据流

```
新闻源 → Collector → Archive → Processor → Generator → TTS → 音频
         ↓           ↓          ↓           ↓
       RSS/Web    source_    要点卡片    脚本文件
                  archive/
```

## 依赖关系

```
cli.py
  ├── core (ArchiveManager, IndexManager)
  ├── collectors (WebFetcher)
  ├── processors (ContentValidator)
  └── utils (slugify, parse_date)

generators/script.py
  └── llm (LLMClient - 依赖注入)

llm/factory.py
  ├── config (settings)
  └── llm clients (OpenAI, Anthropic, DeepSeek)
```

## 扩展点

1. **新增LLM提供商**：实现`generate()`接口
2. **新增采集源**：继承`Collector`基类
3. **自定义处理器**：实现`process()`方法
4. **新增TTS引擎**：添加客户端类

## 测试策略

- **单元测试**：Mock依赖，测试单个模块
- **集成测试**：测试模块间协作
- **端到端测试**：完整流程验证

查看示例：`tests/test_dependency_injection.py`
