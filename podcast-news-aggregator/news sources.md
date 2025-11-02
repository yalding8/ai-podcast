# 国际教育播客 - 信息源完整清单

## 📊 信息源分层架构

```
Tier 1: 行业权威源（深度+准确性）
Tier 2: 广域雷达（覆盖+时效性）
Tier 3: RSS生成器（补盲）
Tier 4: 主动监测（官网直抓）
```

---

## 🎯 Tier 1: 行业权威源

### 教育行业媒体

| 名称 | RSS链接 | 更新频率 | 优先级 |
|------|---------|---------|--------|
| **ICEF Monitor** | https://monitor.icef.com/feed/ | 日更 | ⭐⭐⭐⭐⭐ |
| **The PIE News** | https://thepienews.com/feed/ | 日更 | ⭐⭐⭐⭐⭐ |
| **University World News** | https://www.universityworldnews.com/rss/ | 日更 | ⭐⭐⭐⭐ |
| **Inside Higher Ed** | https://www.insidehighered.com/rss/all | 日更 | ⭐⭐⭐⭐ |
| **Times Higher Education** | https://www.timeshighereducation.com/feeds/all | 日更 | ⭐⭐⭐⭐ |

### 排名与数据机构

| 名称 | RSS链接 | 更新频率 | 优先级 |
|------|---------|---------|--------|
| **QS Top Universities** | https://www.topuniversities.com/rss.xml | 周更 | ⭐⭐⭐⭐ |
| **THE World Rankings** | https://www.timeshighereducation.com/world-university-rankings/feed | 周更 | ⭐⭐⭐⭐ |
| **StudyPortals** | https://www.studyportals.com/feed/ | 周更 | ⭐⭐⭐ |

### 专业协会

| 名称 | RSS链接 | 更新频率 | 优先级 |
|------|---------|---------|--------|
| **NAFSA** | https://www.nafsa.org/rss.xml | 周更 | ⭐⭐⭐⭐ |
| **EAIE** | https://www.eaie.org/feed.xml | 周更 | ⭐⭐⭐⭐ |
| **IIE** | https://www.iie.org/rss | 周更 | ⭐⭐⭐ |

---

## ⚡ Tier 2: 广域雷达系统

### NewsCatcher API 配置

```python
# 关键词组合
QUERIES = [
    "international education",
    "university admission OR college admission",
    "student visa",
    "study abroad",
    "international student",
    "higher education policy",
    "education reform"
]

# 目标国家
COUNTRIES = [
    "US",  # 美国
    "GB",  # 英国
    "CA",  # 加拿大
    "AU",  # 澳大利亚
    "NZ",  # 新西兰
    "FR",  # 法国
    "SG",  # 新加坡
    "JP"   # 日本
]

# 语言
LANGUAGES = ["en", "zh", "es", "fr", "de", "ja","cn"]
```

### GDELT API 配置

```python
# 查询模板
GDELT_QUERIES = {
    "policy": "(education policy OR university policy OR student visa policy)",
    "admission": "(university admission OR college admission OR application)",
    "rankings": "(university ranking OR college ranking OR QS OR THE)",
    "funding": "(scholarship OR financial aid OR tuition OR funding)",
    "research": "(research collaboration OR academic partnership)",
    "exam": "(IELTS OR TOEFL OR GRE OR GMAT OR Duolingo English Test)"
}

# 时间范围
TIMESPAN = "1d"  # 每日更新

# 语言覆盖（GDELT自动翻译65种语言）
# 无需额外配置，直接用英文查询即可
```

---

## 🔧 Tier 3: RSSHub 路由配置

### 考试机构

```yaml
# IELTS
- name: IELTS官网新闻
  url: https://ielts.org/news-and-insights
  frequency: daily

# TOEFL/ETS
- name: ETS/TOEFL新闻
  url: https://www.ets.org/newsroom.html
  frequency: weekly

# Duolingo English Test
- name: Duolingo English Test
  url: https://blog.englishtest.duolingo.com/rss/
  frequency: weekly

# Cambridge Assessment
- name: Cambridge Assessment
  url: https://www.cambridge.org/news-and-insights
  frequency: weekly
```

### 各国教育部/移民局

```yaml
# 英国
- name: UK GOV - Education
  url: https://www.gov.uk/government/organisations/department-for-education
  frequency: daily

- name: UK GOV - Visas & Immigration
  url: https://www.gov.uk/government/organisations/uk-visas-and-immigration
  frequency: daily

# 美国
- name: US Dept of Education
  url: https://www.ed.gov/about/news
  frequency: daily

- name: US State Dept - Student Visas
  url: https://travel.state.gov/content/travel/en/rss.html
  frequency: weekly

# 加拿大
- name: IRCC Canada
  url: https://www.canada.ca/en/immigration-refugees-citizenship/news.html
  frequency: daily

# 澳大利亚
- name: Dept of Education Australia
  url: https://www.education.gov.au/newsroom
  frequency: daily

- name: Dept of Home Affairs
  url: https://www.homeaffairs.gov.au/news-media
  frequency: daily
```

### 招生平台

```yaml
# UCAS (英国)
- name: UCAS News
  url: https://www.ucas.com/corporate/news-and-key-documents/news
  frequency: weekly

# Common App (美国)
- name: Common Application
  url: https://www.commonapp.org/blog
  frequency: weekly
```

---

## 🎯 Tier 4: 主动监测（爬虫配置）

### 重点院校官网

```yaml
universities:
  - name: Harvard University
    news_url: https://news.harvard.edu/gazette/
    selector: .post-item
    frequency: daily
    
  - name: Stanford University
    news_url: https://news.stanford.edu/
    selector: .news-item
    frequency: daily
    
  - name: Oxford University
    news_url: https://www.ox.ac.uk/news
    selector: .news-article
    frequency: daily
    
  - name: Cambridge University
    news_url: https://www.cam.ac.uk/news
    selector: .news-list-item
    frequency: daily

  # 添加更多重点院校...
```

### 地区特色平台

```yaml
asia_pacific:
  - name: Study in China
    url: https://www.studyinchina.edu.cn/
    frequency: weekly
    
  - name: Study in Japan
    url: https://www.studyinjapan.go.jp/
    frequency: weekly
    
  - name: Education New Zealand
    url: https://www.enz.govt.nz/news
    frequency: weekly

europe:
  - name: Study in Europe
    url: https://www.studying-in-europe.org/
    frequency: weekly
    
  - name: Campus France
    url: https://www.campusfrance.org/en/news
    frequency: weekly

north_america:
  - name: EducationUSA
    url: https://educationusa.state.gov/
    frequency: weekly
    
  - name: EduCanada
    url: https://www.educanada.ca/
    frequency: weekly
```

---

## 📈 信息源优先级评分系统

### 评分标准

| 维度 | 权重 | 说明 |
|------|------|------|
| 权威性 | 30% | 来源可信度 |
| 时效性 | 25% | 更新频率 |
| 独家性 | 20% | 是否首发 |
| 相关性 | 15% | 与主题匹配度 |
| 完整性 | 10% | 信息完整程度 |

### 评分等级

- **S级 (90-100分)**: 必须采集，优先处理
  - ICEF Monitor
  - The PIE News
  - 各国教育部官网

- **A级 (80-89分)**: 核心来源，日常采集
  - 考试机构官网
  - 排名机构
  - 主流教育媒体

- **B级 (70-79分)**: 重要来源，选择性采集
  - 地区特色平台
  - 院校官网

- **C级 (60-69分)**: 参考来源，作为补充
  - 社交媒体
  - 论坛讨论

---

## 🔄 更新策略

### 采集频率

```python
COLLECTION_SCHEDULE = {
    "high_priority": "*/30 * * * *",    # 每30分钟
    "medium_priority": "0 */2 * * *",   # 每2小时
    "low_priority": "0 8,20 * * *",     # 每天2次（早晚）
}
```

### 去重策略

```python
DEDUP_CONFIG = {
    "method": "hash + semantic",
    "hash_fields": ["url", "title"],
    "semantic_threshold": 0.85,
    "time_window": "7d"  # 7天内重复视为同一篇
}
```

---

## 💾 数据存储结构

```json
{
  "article_id": "unique_hash",
  "source": "ICEF Monitor",
  "source_tier": 1,
  "title": "UK Universities Face Visa Crackdown",
  "url": "https://...",
  "published_date": "2025-01-28T10:00:00Z",
  "scraped_date": "2025-01-28T10:15:00Z",
  "language": "en",
  "country": "GB",
  "category": "policy",
  "tags": ["visa", "UK", "policy_change"],
  "priority_score": 95,
  "content": {
    "summary": "摘要...",
    "full_text": "全文...",
    "key_points": ["要点1", "要点2"]
  },
  "entities": {
    "universities": ["Oxford", "Cambridge"],
    "organizations": ["UKVI"],
    "persons": [],
    "locations": ["United Kingdom"]
  },
  "sentiment": "negative",
  "status": "pending_review"
}
```

---

## 📝 使用建议

### MVP阶段（第1-3月）
- ✅ Tier 1 全部启用
- ✅ Tier 2 使用GDELT（免费）
- ✅ Tier 3 配置5-10个关键路由
- ⏸️ Tier 4 暂缓，手动补充

### 成长期（第4-12月）
- ✅ 增加NewsCatcher API
- ✅ 扩展RSSHub路由至30+
- ✅ 启动10个关键网站爬虫
- ✅ 建立完整的去重和评分系统

### 成熟期（12月+）
- ✅ 完整的4层架构
- ✅ 50+网站主动爬取
- ✅ 社交媒体监测
- ✅ 机器学习自动分类和打分

---

## 🚨 注意事项

1. **版权合规**
   - 只使用摘要（<30%原文）
   - 标注来源
   - 提供原文链接

2. **robots.txt遵守**
   ```bash
   # 检查示例
   curl https://127.0.0.1:1200/robots.txt
   ```

3. **请求频率控制**
   - 官网爬取：≥5秒/次
   - API调用：遵守各平台限制
   - RSSHub：默认1小时缓存

4. **数据质量监控**
   - 每日采集量统计
   - 去重率监控
   - 错误率报警（>5%触发）

---

## 📞 技术支持

遇到问题？检查以下资源：

- RSSHub文档: https://docs.rsshub.app/
- GDELT文档: https://blog.gdeltproject.org/
- NewsCatcher文档: https://docs.newscatcherapi.com/