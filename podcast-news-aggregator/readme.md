# 国际教育资讯AI播客工厂

> **自动化采集、处理、生成国际教育新闻播客的完整解决方案**

## 🎯 项目简介

这是一个端到端的AI播客生产系统，专注于国际教育领域的新闻资讯。系统自动从全球多个来源采集新闻，经过去重、分类、翻译、生成脚本，最后输出可供播客使用的内容。

### 核心特点

- ✅ **多源采集**: 整合行业权威媒体 + GDELT全球监测 + RSSHub定制源
- ✅ **智能处理**: 自动去重、语义聚类、优先级评分
- ✅ **多语言**: 支持采集65种语言，输出中文内容
- ✅ **完全免费**: 核心功能基于开源工具和免费API
- ✅ **可扩展**: 模块化设计，易于添加新功能

---

## 📁 项目结构

```
podcast-news-aggregator/
├── config/                    # 配置文件
│   └── api_keys.env.template # API密钥模板
├── scripts/                   # 核心脚本
│   ├── test_newscatcher.py   # NewsCatcher测试
│   ├── test_gdelt.py         # GDELT测试
│   └── integrated_demo.py    # 完整流程演示
├── data/                      # 数据存储
│   ├── articles_*.json       # 采集的新闻
│   ├── script_*.json         # 生成的脚本
│   └── report_*.md           # 格式化报告
├── docker-compose.yml         # RSSHub部署配置
├── NEWS_SOURCES.md           # 信息源完整清单
├── RSSHUB_GUIDE.md           # RSSHub使用指南
└── README.md                 # 本文档
```

---

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Docker & Docker Compose（可选，用于RSSHub）
- 网络连接（用于API调用）

### 第1步：克隆并安装

```bash
# 进入项目目录
cd podcast-news-aggregator

# 安装Python依赖
pip install requests --break-system-packages
```

### 第2步：运行演示

```bash
# 运行完整流程演示（无需API密钥）
python3 scripts/integrated_demo.py
```

你会看到：
- ✅ 采集5条演示新闻
- ✅ 自动去重和分类
- ✅ 生成播客脚本
- ✅ 输出Markdown报告

### 第3步：查看结果

```bash
# 查看生成的报告
ls -lh data/
cat data/report_*.md
```

---

## 🔧 完整部署（生产环境）

### 1. 配置API密钥

```bash
# 复制配置模板
cp config/api_keys.env.template config/api_keys.env

# 编辑配置文件
nano config/api_keys.env
```

**获取API密钥：**
- **NewsCatcher**: https://www.newscatcherapi.com/ （免费版200次/月）
- **GDELT**: 无需密钥，完全免费 ✅

### 2. 部署RSSHub

```bash
# 启动RSSHub服务
docker-compose up -d

# 检查状态
docker-compose ps

# 访问RSSHub
# 浏览器打开: http://localhost:1200
```

### 3. 测试API连接

```bash
# 测试NewsCatcher（需要密钥）
export NEWSCATCHER_API_KEY='your_key_here'
python3 scripts/test_newscatcher.py

# 测试GDELT（无需密钥）
python3 scripts/test_gdelt.py
```

---

## 📊 信息源配置

系统采用**四层信息源架构**：

### Tier 1: 行业权威源（已配置）
- ICEF Monitor
- The PIE News  
- Times Higher Education
- Inside Higher Ed

### Tier 2: 广域雷达（需配置API）
- **GDELT**: 免费，覆盖100+语言 ✅
- **NewsCatcher**: 付费，120,000+源

### Tier 3: RSSHub定制源（需部署）
- 考试机构（IELTS/TOEFL）
- 各国教育部
- 招生平台

### Tier 4: 主动爬取（高级功能）
- 重点院校官网
- 特定政策页面

详细配置见 → [NEWS_SOURCES.md](NEWS_SOURCES.md)

---

## 💡 使用场景

### 场景1: 每日新闻播客

```bash
# 每天早上8点运行
0 8 * * * cd /path/to/project && python3 scripts/integrated_demo.py
```

### 场景2: 特定主题深度分析

修改查询关键词：
```python
queries = [
    "UK student visa policy",
    "Ivy League admission statistics"
]
```

### 场景3: 多语言监测

GDELT自动支持65种语言：
```python
# 用英文关键词搜索全球新闻
search_multilingual("international education")
```

---

## 🔄 工作流程

```
1. 信息采集
   ↓
2. 去重聚类 (基于标题+内容相似度)
   ↓
3. 分类打分 (政策/院校/考试/排名)
   ↓
4. 生成脚本 (结构化JSON + Markdown)
   ↓
5. 人工审核 (通过Notion/自定义工具)
   ↓
6. AI配音 (NotebookLM/Azure TTS)
   ↓
7. 发布分发 (RSS/喜马拉雅/小宇宙)
```

---

## 📈 性能指标（MVP阶段）

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 采集量 | 100-200条/天 | 覆盖主要来源 |
| 去重率 | >90% | 避免重复内容 |
| 处理时间 | <5分钟 | 从采集到脚本 |
| 准确率 | >95% | 分类和关键信息 |

---

## 🛠️ 技术栈

### 核心技术
- **Python 3.8+**: 主要开发语言
- **GDELT API**: 全球新闻监测（免费）
- **NewsCatcher API**: 结构化新闻数据（可选）
- **RSSHub**: RSS feed生成器

### 可选集成
- **n8n/Make**: 低代码自动化
- **Notion**: 人工审核工作台
- **NotebookLM**: AI播客生成
- **Feedly/Inoreader**: RSS聚合

---

## 📝 开发路线图

### ✅ 已完成
- [x] 核心采集引擎
- [x] 去重和分类
- [x] 脚本生成
- [x] 演示系统

### 🚧 进行中
- [ ] NewsCatcher集成
- [ ] 向量化语义搜索
- [ ] Notion审核工作台

### 📅 计划中
- [ ] 自动TTS生成
- [ ] 多栏目支持
- [ ] 播客平台自动发布

---

## 🤝 贡献指南

欢迎提交Issue和PR！

### 如何贡献
1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证

---

## 🙏 致谢

- [GDELT Project](https://www.gdeltproject.org/) - 提供免费的全球新闻监测
- [NewsCatcher](https://www.newscatcherapi.com/) - 提供高质量新闻API
- [RSSHub](https://docs.rsshub.app/) - 强大的RSS生成工具

---

## 📞 联系方式

遇到问题？

1. 查看 [常见问题](FAQ.md)
2. 提交 [Issue](https://github.com/your-repo/issues)
3. 参考文档:
   - [信息源配置指南](NEWS_SOURCES.md)
   - [RSSHub使用指南](RSSHUB_GUIDE.md)

---

## ⚠️ 重要声明

### 版权与合规
- ✅ 仅使用新闻摘要（<30%原文）
- ✅ 标注所有信息来源
- ✅ 提供原文链接
- ✅ 遵守各网站的robots.txt
- ❌ 不全文转载或商业转售

### 数据使用
本系统仅用于：
- ✅ 个人学习和研究
- ✅ 非商业播客制作
- ✅ 教育信息传播

如需商业使用，请联系各信息源获取授权。

---

**🎉 开始使用吧！祝你的播客大获成功！**