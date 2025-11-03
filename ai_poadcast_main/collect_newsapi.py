#!/usr/bin/env python3
"""
使用NewsAPI采集高质量国际教育新闻
注册免费API: https://newsapi.org (每天100次请求)
"""
import os
import json
import requests
from datetime import datetime, timedelta, timezone

API_KEY = os.getenv("NEWSAPI_KEY", "")
BASE_URL = "https://newsapi.org/v2/everything"

QUALITY_QUERIES = [
    "international students visa",
    "university admission policy",
    "study abroad scholarship",
    "IELTS TOEFL exam",
    "university ranking QS THE",
]

QUALITY_DOMAINS = [
    "thepienews.com",
    "monitor.icef.com",
    "insidehighered.com",
    "timeshighereducation.com",
    "universityworldnews.com",
]

def fetch_quality_news():
    if not API_KEY:
        print("❌ 请设置 NEWSAPI_KEY 环境变量")
        return []
    
    all_articles = []
    from_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")  # 扩展到30天
    
    for query in QUALITY_QUERIES:
        params = {
            "q": query,
            "from": from_date,
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 10,
            "apiKey": API_KEY
        }
        
        try:
            resp = requests.get(BASE_URL, params=params, timeout=10)
            data = resp.json()
            
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                for article in articles:
                    if any(domain in article.get("url", "") for domain in QUALITY_DOMAINS):
                        all_articles.append({
                            "title": article["title"],
                            "url": article["url"],
                            "source": article["source"]["name"],
                            "published": article["publishedAt"],
                            "summary": article.get("description", "")[:200],
                            "priority": 9,
                            "tags": ["newsapi", query.split()[0]]
                        })
                print(f"✅ {query}: {len(articles)} 条")
        except Exception as e:
            print(f"⚠️ {query}: {e}")
    
    # 去重并保存
    unique = {item["url"]: item for item in all_articles}.values()
    
    with open("ai_poadcast_main/newsapi_queue.json", "w") as f:
        json.dump({"items": list(unique), "total": len(unique)}, f, indent=2)
    
    print(f"💾 保存 {len(unique)} 条高质量新闻")
    return list(unique)

if __name__ == "__main__":
    fetch_quality_news()
