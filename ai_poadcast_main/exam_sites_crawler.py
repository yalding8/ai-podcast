#!/usr/bin/env python3
"""
考试官网自动爬虫
监控IELTS、TOEFL、GRE、GMAT等考试官网的最新动态
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import json
import hashlib
from pathlib import Path
from typing import List, Dict
import time

class ExamSiteCrawler:
    def __init__(self, output_dir="ai_poadcast_main/exam_updates"):
        from path_utils import safe_path
        self.output_dir = safe_path(output_dir, Path.cwd())
        self.output_dir.mkdir(exist_ok=True)
        self.cache_file = self.output_dir / "content_cache.json"
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        if self.cache_file.exists():
            return json.loads(self.cache_file.read_text())
        return {}
    
    def _save_cache(self):
        self.cache_file.write_text(json.dumps(self.cache, indent=2))
    
    def _get_content_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_new_content(self, site_key: str, content: str) -> bool:
        content_hash = self._get_content_hash(content)
        if site_key not in self.cache or self.cache[site_key] != content_hash:
            self.cache[site_key] = content_hash
            self._save_cache()
            return True
        return False
    
    def crawl_ielts(self) -> List[Dict]:
        """爬取IELTS官网新闻"""
        results = []
        try:
            url = "https://www.ielts.org/news"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            articles = soup.select('.news-item')[:5]
            for article in articles:
                title_elem = article.select_one('.news-title')
                link_elem = article.select_one('a')
                date_elem = article.select_one('.news-date')
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get('href', '')
                    if not link.startswith('http'):
                        link = f"https://www.ielts.org{link}"
                    
                    content_key = f"ielts_{link}"
                    if self._is_new_content(content_key, title):
                        results.append({
                            'source': 'IELTS Official',
                            'title': title,
                            'url': link,
                            'date': date_elem.get_text(strip=True) if date_elem else '',
                            'exam_type': 'IELTS',
                            'priority': 9
                        })
        except Exception as e:
            print(f"IELTS爬取失败: {e}")
        
        return results
    
    def crawl_toefl(self) -> List[Dict]:
        """爬取TOEFL官网新闻"""
        results = []
        try:
            url = "https://www.ets.org/toefl/test-takers/ibt/news.html"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            articles = soup.select('.article-item')[:5]
            for article in articles:
                title_elem = article.select_one('h3')
                link_elem = article.select_one('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get('href', '')
                    if not link.startswith('http'):
                        link = f"https://www.ets.org{link}"
                    
                    content_key = f"toefl_{link}"
                    if self._is_new_content(content_key, title):
                        results.append({
                            'source': 'ETS TOEFL',
                            'title': title,
                            'url': link,
                            'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                            'exam_type': 'TOEFL',
                            'priority': 9
                        })
        except Exception as e:
            print(f"TOEFL爬取失败: {e}")
        
        return results
    
    def crawl_gre(self) -> List[Dict]:
        """爬取GRE官网新闻"""
        results = []
        try:
            url = "https://www.ets.org/gre/test-takers/general-test/news.html"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            articles = soup.select('.news-article')[:5]
            for article in articles:
                title_elem = article.select_one('h3')
                link_elem = article.select_one('a')
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    link = link_elem.get('href', '')
                    if not link.startswith('http'):
                        link = f"https://www.ets.org{link}"
                    
                    content_key = f"gre_{link}"
                    if self._is_new_content(content_key, title):
                        results.append({
                            'source': 'ETS GRE',
                            'title': title,
                            'url': link,
                            'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                            'exam_type': 'GRE',
                            'priority': 8
                        })
        except Exception as e:
            print(f"GRE爬取失败: {e}")
        
        return results
    
    def crawl_all(self) -> List[Dict]:
        """爬取所有考试网站"""
        all_results = []
        
        print("🔍 开始爬取考试官网...")
        
        print("  → IELTS...")
        all_results.extend(self.crawl_ielts())
        time.sleep(1)
        
        print("  → TOEFL...")
        all_results.extend(self.crawl_toefl())
        time.sleep(1)
        
        print("  → GRE...")
        all_results.extend(self.crawl_gre())
        
        # 保存结果
        if all_results:
            output_file = self.output_dir / f"exam_updates_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
            output_file.write_text(json.dumps(all_results, indent=2, ensure_ascii=False))
            print(f"\n✅ 发现 {len(all_results)} 条新动态，已保存到: {output_file}")
        else:
            print("\n📭 未发现新动态")
        
        return all_results

if __name__ == "__main__":
    crawler = ExamSiteCrawler()
    results = crawler.crawl_all()
    
    # 输出摘要
    if results:
        print("\n📊 新动态摘要:")
        for item in results:
            print(f"  [{item['exam_type']}] {item['title']}")
            print(f"      {item['url']}")
