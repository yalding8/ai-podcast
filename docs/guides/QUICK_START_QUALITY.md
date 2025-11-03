# 快速提升新闻质量指南

## 立即可用的3个方法

### 方法1：提高优先级阈值（最简单）
```bash
# 只采集优先级≥9的新闻
python ai_poadcast_main/daily_workflow.py --auto-min-priority 9 --min-priority 9

# 只采集优先级=10的新闻（最高质量）
python ai_poadcast_main/daily_workflow.py --auto-min-priority 10 --min-priority 10
```

### 方法2：使用NewsAPI（需注册）
```bash
# 1. 注册免费API: https://newsapi.org (每天100次)
# 2. 设置环境变量
export NEWSAPI_KEY="your_key_here"

# 3. 运行采集
python ai_poadcast_main/collect_newsapi.py

# 4. 查看结果
cat ai_poadcast_main/newsapi_queue.json
```

### 方法3：手动添加高质量新闻
```bash
# 从ICEF Monitor、The PIE News等网站手动复制
pbpaste | python ai_poadcast_main/import_raw_story.py \
    --title "标题" \
    --source "ICEF Monitor" \
    --url "https://..." \
    --published-date 2025-11-02 \
    --fetch --store-html
```

## 推荐的高质量源

### 每日必查（优先级10）
1. ICEF Monitor - https://monitor.icef.com
2. The PIE News - https://thepienews.com
3. USCIS - https://www.uscis.gov/newsroom
4. UK Home Office - https://www.gov.uk/government/organisations/uk-visas-and-immigration

### 每周必查（优先级9）
1. Study International - https://www.studyinternational.com
2. University World News - https://www.universityworldnews.com
3. IIE Open Doors - https://www.iie.org
4. QS Rankings - https://www.topuniversities.com

## 质量标准

✅ **优先采集**
- 政府官方政策变化
- 签证/移民新规
- 大学排名发布
- 考试政策更新
- 奖学金项目启动

❌ **排除内容**
- UK GOV Education的非国际教育内容
- Reddit的讨论帖
- 单个学校的活动新闻
- 地方性教育新闻
