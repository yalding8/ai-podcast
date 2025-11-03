#!/usr/bin/env python3
"""
高质量新闻源采集器 - 专注权威源
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from premium_feeds_config import PREMIUM_SOURCES, QUALITY_FILTERS
from collect_rss_feeds import (
    parse_feed_with_fallback, normalize_url, 
    deduplicate_by_title, load_seen_urls
)

def collect_premium_news():
    """采集高质量新闻源"""
    print("🔥 启动高质量新闻采集...")
    
    seen_urls = load_seen_urls()
    all_items = []
    
    for source_name, config in PREMIUM_SOURCES.items():
        if config.get('method') == 'scrape':
            print(f"⚠️ {source_name}: 需要爬虫，跳过")
            continue
            
        rss_url = config.get('rss')
        if not rss_url:
            continue
            
        print(f"📡 采集: {source_name}")
        
        feed = parse_feed_with_fallback(source_name, rss_url)
        if not feed:
            continue
            
        max_items = config.get('max_items', 3)
        priority = config.get('priority', 7)
        
        count = 0
        for entry in feed.entries:
            if count >= max_items:
                break
                
            url = normalize_url(getattr(entry, 'link', ''))
            if not url or url in seen_urls:
                continue
                
            # 质量过滤
            title = entry.title
            summary = getattr(entry, 'summary', '')
            
            # 检查最少字数
            if len(title + summary) < QUALITY_FILTERS['min_word_count']:
                continue
                
            # 检查排除词
            text_lower = (title + ' ' + summary).lower()
            if any(word in text_lower for word in QUALITY_FILTERS['exclude_keywords']):
                continue
                
            all_items.append({
                'title': title,
                'url': url,
                'source': source_name,
                'published': getattr(entry, 'published', ''),
                'summary': summary[:200],
                'tags': config.get('tags', []),
                'priority': priority,
                'collected_at': datetime.now(timezone.utc).isoformat()
            })
            count += 1
            
        print(f"  ✅ 采集 {count} 条")
        time.sleep(1)  # 避免请求过快
    
    # 去重
    unique_items = deduplicate_by_title(all_items)
    
    # 保存
    if unique_items:
        output_file = Path("ai_poadcast_main/premium_news_queue.json")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'total': len(unique_items),
                'items': sorted(unique_items, key=lambda x: x['priority'], reverse=True)
            }, f, ensure_ascii=False, indent=2)
            
        print(f"💾 保存 {len(unique_items)} 条高质量新闻")
        return unique_items
    
    return []

if __name__ == "__main__":
    collect_premium_news()