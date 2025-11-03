# 时间限制放宽修改记录

## 修改日期
2025-11-03

## 修改目的
完全放宽所有新闻采集脚本的时间限制，确保能够获取更多历史新闻，不再受72小时或3天的限制。

## 修改文件清单

### 1. collect_rss_feeds.py
**位置**: `ai_poadcast_main/collect_rss_feeds.py`  
**修改内容**:
- 第217行: `min_age_hours=72` → `min_age_hours=0`
- **效果**: RSS采集不再限制时间范围，可获取所有可用的历史新闻

### 2. collect_newsapi.py
**位置**: `ai_poadcast_main/collect_newsapi.py`  
**修改内容**:
- 第30行: `timedelta(days=3)` → `timedelta(days=30)`
- **效果**: NewsAPI采集从3天扩展到30天

### 3. gdelt_monitor.py
**位置**: `ai_poadcast_main/gdelt_monitor.py`  
**修改内容**:
- 第36行: `hours: int = 24` → `hours: int = 720`（30天）
- 文档字符串更新，说明默认为720小时（30天）
- **效果**: GDELT搜索从24小时扩展到30天

### 4. test_newscatcher.py
**位置**: `podcast-news-aggregator/scripts/test_newscatcher.py`  
**修改内容**:
- 第42行: `def search_education_news(self, days=1)` → `days=30`
- 第169行: `tester.search_education_news(days=1)` → `days=30`
- **效果**: NewsCatcher测试脚本从1天扩展到30天

## 验证方法

运行以下命令验证修改是否生效：

```bash
# 1. 测试RSS采集（应该获取更多新闻）
python ai_poadcast_main/collect_rss_feeds.py

# 2. 查看采集结果
cat ai_poadcast_main/news_queue.json | jq '.total'

# 3. 运行完整工作流
python ai_poadcast_main/daily_workflow.py --collect

# 4. 检查日志中的新闻数量
cat ai_poadcast_main/logs/rss_run_summary.json | jq '.total_items'
```

## 预期效果

修改后，新闻采集数量应该显著增加：
- **修改前**: 通常只能获取最近72小时内的新闻（约10-30条）
- **修改后**: 可以获取所有可用的历史新闻（预计50-200条，取决于RSS源的历史深度）

## 注意事项

1. **RSS源限制**: 某些RSS源本身只提供最近的条目（如最新20条），即使放宽时间限制也无法获取更早的新闻
2. **去重机制**: `source_archive/_index.json` 中已存在的URL会被自动过滤
3. **性能影响**: 首次运行可能需要更长时间，后续运行会因为去重而快速完成
4. **API配额**: NewsAPI和NewsCatcher等付费服务有调用次数限制，扩大时间范围可能消耗更多配额

## 回滚方法

如需恢复原有时间限制，修改以下值：
- `collect_rss_feeds.py`: `min_age_hours=0` → `min_age_hours=72`
- `collect_newsapi.py`: `timedelta(days=30)` → `timedelta(days=3)`
- `gdelt_monitor.py`: `hours: int = 720` → `hours: int = 24`
- `test_newscatcher.py`: `days=30` → `days=1`
