#!/usr/bin/env python3
"""
考试机构网站爬虫
针对没有RSS的官网（IELTS、TOEFL等）
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import json
from pathlib import Path

EXAM_SITES = {
    'IELTS': {
        'url': 'https://ielts.org/news-and-insights',
        'selector': '.news-item',  # 需要根据实际页面调整
        'title_selector': '.news-title',
        'link_selector': 'a',
        'date_selector': '.news-date'
    },
    'TOEFL': {
        'url': 'https://www.ets.org/toefl/test-takers/ibt/news.html',
        'selector': '.news-article',
        'title_selector': 'h3',
        'link_selector': 'a',
        'date_selector': '.date'
    }
}

def scrape_site(site_name, config):
    """爬取单个网站"""
    print(f"\n🕷️  正在爬取: {site_name}")
    
    try:
        response = requests.get(config['url'], timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    items = []
    
    # 根据配置提取
    for article in soup.select(config['selector'])[:10]:  # 最多取10条
        try:
            title_elem = article.select_one(config['title_selector'])
            link_elem = article.select_one(config['link_selector'])
            
            if not title_elem or not link_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = link_elem['href']
            
            # 处理相对链接
            if not link.startswith('http'):
                from urllib.parse import urljoin
                link = urljoin(config['url'], link)
            
            # 日期（可选）
            date = ''
            if config.get('date_selector'):
                date_elem = article.select_one(config['date_selector'])
                if date_elem:
                    date = date_elem.get_text(strip=True)
            
            items.append({
                'title': title,
                'url': link,
                'source': site_name,
                'published': date,
                'tags': ['exam', site_name.lower()],
                'priority': 9,
                'collected_at': datetime.now(timezone.utc).isoformat()
            })
        
        except Exception as e:
            print(f"  ⚠️  解析条目失败: {e}")
            continue
    
    print(f"  ✅ 发现 {len(items)} 条更新")
    return items

def main():
    """主流程"""
    all_items = []
    
    for site_name, config in EXAM_SITES.items():
        items = scrape_site(site_name, config)
        all_items.extend(items)
    
    if all_items:
        # 追加到队列
        queue_file = Path("ai_poadcast_main/news_queue.json")
        
        if queue_file.exists():
            with open(queue_file) as f:
                queue = json.load(f)
        else:
            queue = {'items': []}
        
        queue['items'].extend(all_items)
        queue['updated_at'] = datetime.now(timezone.utc).isoformat()
        queue['total'] = len(queue['items'])
        
        with open(queue_file, 'w', encoding='utf-8') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 已添加 {len(all_items)} 条到队列")
    else:
        print("\n⚠️  未发现新内容")

if __name__ == "__main__":
    main()