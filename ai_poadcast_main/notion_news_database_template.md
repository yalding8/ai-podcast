# Notion数据库：国际教育新闻库

## 数据库结构

### 必需字段

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| 标题 | Title | 新闻标题（英文原文） | "UK extends PSW visa to 3 years" |
| 来源 | Select | 新闻来源 | ICEF Monitor / The PIE / 官网 |
| 原文链接 | URL | 原始URL | https://... |
| 发布日期 | Date | 新闻发布时间 | 2025-01-15 |
| 类别 | Multi-select | 新闻分类 | 政策/院校/考试/排名 |
| 国家/地区 | Multi-select | 涉及国家 | 英国/美国/澳洲 |
| 优先级 | Select | 重要程度 | 🔴高/🟡中/🟢低 |
| 状态 | Select | 处理状态 | 待筛选/已选用/已归档 |
| 中文摘要 | Text | AI生成的中文要点 | （自动填充） |
| 证据等级 | Select | 来源可信度 | A级/B级/C级 |

### 可选字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 影响人群 | Multi-select | 本科生/研究生/博士/家长 |
| 时效性 | Select | 紧急/本周/本月/长期 |
| 关键词 | Tags | 签证/奖学金/申请/语言考试 |
| 原文长度 | Number | 字数（用于判断翻译成本） |
| 已用期数 | Relation | 关联到播客期数 |

---

## 筛选标准（评分卡）

### 优先级判断规则

**🔴 高优先级（必选）：**
- [ ] 政策变化且影响面广（如签证/学费政策）
- [ ] 官方一手来源（政府/考试机构/TOP院校）
- [ ] 时间敏感（申请deadline/考试报名）
- [ ] 数据重大（如录取率暴跌/学费大涨）

**🟡 中优先级（备选）：**
- [ ] 行业趋势分析（如某国留学生增长）
- [ ] 院校排名变化（QS/THE前50）
- [ ] 新项目/新专业开设
- [ ] 考试题型/评分调整

**🟢 低优先级（可忽略）：**
- [ ] 单个院校活动（除非TOP10）
- [ ] 个人申请经验分享
- [ ] 旧闻翻炒（超过30天且无新进展）
- [ ] 地域性太强（如仅限某一城市）

---

## 每周选题配比建议

**总计5-8条新闻，按以下比例：**

| 类别 | 数量 | 占比 | 示例 |
|------|------|------|------|
| 🏛️ 政策类 | 2-3条 | 40% | 签证政策/移民法规/学费调整 |
| 🎓 院校类 | 1-2条 | 25% | 排名变化/新专业/合作项目 |
| 📝 考试类 | 1-2条 | 25% | 托福/雅思/GRE改革 |
| 📊 数据类 | 1条 | 10% | 录取率/就业率/薪资报告 |

---

## 快速筛选工作流（5分钟）

### 方法A：Feedly内筛选
1. 在Feedly中使用"保存到Notion"功能（需配置集成）
2. 只保存标题含关键词的：visa / admission / policy / ranking
3. 每日早晨一次性浏览，标记"今日必看"

### 方法B：导出CSV批量处理
1. Feedly导出未读RSS → CSV文件
2. 上传到ChatGPT → 批量分类打分
3. 将高分项复制到Notion

---

## Prompt模板：自动筛选与打分

```markdown
你是国际教育播客的选题编辑。请对以下新闻列表进行筛选打分：

**评分标准：**
- 政策变化 +3分
- 官方来源 +2分
- 时间敏感 +2分
- 影响面广 +2分
- 数据驱动 +1分
- 旧闻翻炒 -2分
- 地域性太强 -1分

**新闻列表：**
1. [标题1] - [来源] - [日期]
2. [标题2] - [来源] - [日期]
...

**输出格式（JSON）：**
{
  "selected": [
    {
      "index": 1,
      "score": 8,
      "reason": "英国签证政策重大调整，影响所有申请者",
      "category": "政策类",
      "priority": "高"
    }
  ],
  "rejected": [...]
}
```

---

## 实战案例

### 输入示例（Feedly今日10条新闻）

1. UK Government announces PSW visa extension to 3 years - GOV.UK - 2025-01-15
2. Cambridge opens new AI research center - Cambridge News - 2025-01-14
3. IELTS introduces online speaking test - IELTS Official - 2025-01-13
4. Student shares Harvard application tips - Reddit - 2025-01-12
5. QS Rankings 2026: MIT still #1 - QS Top Universities - 2025-01-10
6. Australia raises student visa fees by 15% - Home Affairs - 2025-01-15
7. Small college in Ohio closes program - Local News - 2025-01-11
8. Study: International students boost UK economy - ICEF Monitor - 2025-01-14
9. Yale announces new scholarship program - Yale News - 2025-01-13
10. Tips for writing personal statement - Blog Post - 2025-01-09

### 筛选结果

**✅ 已选用（5条）：**
1. #1 - PSW签证延长（政策/高优先级/官方）
2. #3 - 雅思口语在线化（考试/高优先级/官方）
3. #6 - 澳洲签证费上涨（政策/高优先级/官方）
4. #8 - 留学生经济贡献数据（数据/中优先级/权威）
5. #9 - 耶鲁新奖学金（院校/中优先级/TOP10）

**❌ 已拒绝（5条）：**
- #2 - 单个研究中心（影响面窄）
- #4 - 个人经验分享（C级来源）
- #5 - 排名变化小（MIT连续#1无新意）
- #7 - 地域性太强（小院校关闭）
- #10 - 旧内容（博客文章非新闻）

---

## 下一步

筛选完成后，进入【阶段2：要点提取与翻译】
