#!/usr/bin/env python3
"""
GDELT API 测试脚本
功能：测试GDELT DOC 2.0 API并搜索国际教育新闻
特点：完全免费，无需API密钥，支持65种语言
"""

import json
import os
from datetime import datetime
from typing import Dict
from urllib.parse import urlencode

import requests

COUNTRY_CODE_MAP: Dict[str, str] = {
    "united kingdom": "GB",
    "united states": "US",
    "united states of america": "US",
    "usa": "US",
    "uk": "GB",
    "great britain": "GB",
    "england": "GB",
    "australia": "AU",
    "canada": "CA",
    "china": "CN",
    "india": "IN",
    "new zealand": "NZ",
    "ireland": "IE",
    "germany": "DE",
    "france": "FR",
}

class GDELTTester:
    def __init__(self):
        self.doc_api_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        self.geo_api_url = "https://api.gdeltproject.org/api/v2/geo/geo"
    
    def test_connection(self):
        """测试GDELT API连接"""
        print("=" * 60)
        print("测试 GDELT API 连接...")
        print("=" * 60)
        
        params = {
            "query": "education",
            "mode": "artlist",
            "maxrecords": 1,
            "format": "json"
        }
        
        try:
            response = requests.get(self.doc_api_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ GDELT API连接成功!")
                print("🌍 GDELT监测全球100+语言的新闻媒体")
                print("⚡ 每15分钟更新一次")
                print("🎁 完全免费，无API密钥要求\n")
                return True
            else:
                print(f"❌ API返回错误: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 连接失败: {str(e)}")
            return False
    
    def search_education_news(self, timespan="3d"):
        """搜索国际教育新闻
        
        Args:
            timespan: 时间范围，如 "1d"(1天), "3d"(3天), "1w"(1周)
        """
        print("\n" + "=" * 60)
        print(f"搜索过去{timespan}的国际教育新闻...")
        print("=" * 60)
        
        # GDELT查询语法
        query = "(international student OR university admission OR student visa OR study abroad OR international education)"
        
        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": 250,  # 最多返回250条
            "timespan": timespan,
            "format": "json",
            "sort": "datedesc"  # 按日期降序
        }
        
        try:
            print(f"🔍 查询参数: {query}")
            print(f"⏰ 时间范围: {timespan}\n")
            
            response = requests.get(self.doc_api_url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                print(f"📈 找到 {len(articles)} 条相关新闻\n")
                
                if len(articles) == 0:
                    print("⚠️  未找到相关新闻，尝试扩大时间范围或调整关键词")
                    return []
                
                # 显示前10条
                results = []
                for i, article in enumerate(articles[:10], 1):
                    result = {
                        'title': article.get('title', 'N/A'),
                        'url': article.get('url', 'N/A'),
                        'domain': article.get('domain', 'N/A'),
                        'language': article.get('language', 'N/A'),
                        'seendate': article.get('seendate', 'N/A'),
                        'socialimage': article.get('socialimage', 'N/A')
                    }
                    results.append(result)
                    
                    print(f"{i}. 【{result['domain']}】{result['title']}")
                    print(f"   🌐 语言: {result['language']}")
                    print(f"   🕒 发现时间: {self.format_gdelt_date(result['seendate'])}")
                    print(f"   🔗 {result['url'][:80]}...")
                    print()
                
                # 统计语言分布
                self.print_language_stats(articles)
                
                # 保存结果
                self.save_results(articles, "gdelt_test")
                
                return results
                
            else:
                print(f"❌ 搜索失败: {response.status_code}")
                print(f"错误信息: {response.text[:200]}")
                return []
                
        except Exception as e:
            print(f"❌ 搜索出错: {str(e)}")
            return []
    
    def search_by_country(self, country_name, query="education policy"):
        """按国家搜索新闻"""
        print("\n" + "=" * 60)
        print(f"搜索 {country_name} 的教育新闻...")
        print("=" * 60)
        
        # 组合查询：关键词 + 国家
        country_code = self.get_country_code(country_name)
        combined_query = f"{query} sourcecountry:{country_code}"
        
        params = {
            "query": combined_query,
            "mode": "artlist",
            "maxrecords": 50,
            "timespan": "1d",
            "format": "json"
        }
        
        try:
            response = requests.get(self.doc_api_url, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError:
                    preview = response.text[:200].strip()
                    print("⚠️  响应不是有效的JSON，返回内容示例:")
                    print(f"   {preview}")
                    return []
                articles = data.get('articles', [])
                
                print(f"\n找到 {len(articles)} 条新闻:\n")
                
                for i, article in enumerate(articles[:5], 1):
                    print(f"{i}. {article.get('title', 'N/A')}")
                    print(f"   来源: {article.get('domain', 'N/A')}")
                    print(f"   时间: {self.format_gdelt_date(article.get('seendate', 'N/A'))}")
                    print()
                
                return articles
            else:
                print(f"❌ 搜索失败: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 搜索出错: {str(e)}")
            return []

    def get_country_code(self, country_name: str) -> str:
        """根据国家名称返回GDELT支持的sourcecountry代码"""
        key = (country_name or "").strip().lower()
        if not key:
            return ""
        if key in COUNTRY_CODE_MAP:
            return COUNTRY_CODE_MAP[key]
        fallback = key.replace(" ", "_").replace("-", "_")
        return fallback.upper()
    
    def search_multilingual(self, english_keyword):
        """多语言搜索（GDELT的核心功能）
        
        使用英文关键词搜索65种语言的新闻
        """
        print("\n" + "=" * 60)
        print(f"多语言搜索: '{english_keyword}'")
        print("=" * 60)
        print("🌍 GDELT将自动搜索65种语言的翻译内容\n")
        
        params = {
            "query": english_keyword,
            "mode": "artlist",
            "maxrecords": 100,
            "timespan": "1d",
            "format": "json"
        }
        
        try:
            response = requests.get(self.doc_api_url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # 统计语言分布
                languages = {}
                for article in articles:
                    lang = article.get('language', 'Unknown')
                    languages[lang] = languages.get(lang, 0) + 1
                
                print(f"📊 语言分布统计:")
                for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"   {lang}: {count} 条")
                
                return articles
            else:
                return []
                
        except Exception as e:
            print(f"❌ 搜索出错: {str(e)}")
            return []
    
    def format_gdelt_date(self, datestr):
        """格式化GDELT日期
        
        GDELT格式: 20250128120000 -> 2025-01-28 12:00:00
        """
        if not datestr or datestr == 'N/A':
            return 'N/A'
        
        try:
            # GDELT格式: YYYYMMDDHHmmss
            year = datestr[:4]
            month = datestr[4:6]
            day = datestr[6:8]
            hour = datestr[8:10]
            minute = datestr[10:12]
            
            return f"{year}-{month}-{day} {hour}:{minute}"
        except:
            return datestr
    
    def print_language_stats(self, articles):
        """打印语言统计"""
        print("\n" + "-" * 60)
        print("📊 语言分布统计:")
        
        languages = {}
        for article in articles:
            lang = article.get('language', 'Unknown')
            languages[lang] = languages.get(lang, 0) + 1
        
        # 排序并显示
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        
        for lang, count in sorted_langs[:10]:
            percentage = (count / len(articles)) * 100
            print(f"   {lang:15s}: {count:3d} 条 ({percentage:5.1f}%)")
        
        print("-" * 60)
    
    def save_results(self, results, filename):
        """保存结果到JSON文件"""
        # 使用相对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        output_dir = os.path.join(project_root, "data")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存至: {filepath}")


def main():
    print("=" * 60)
    print("GDELT API 测试工具")
    print("=" * 60)
    print("✨ 特点: 完全免费 | 65种语言 | 15分钟更新")
    print("📚 数据源: 全球100,000+新闻网站\n")
    
    # 创建测试实例
    tester = GDELTTester()
    
    # 测试连接
    if not tester.test_connection():
        return False
    
    # 1. 搜索国际教育新闻（过去3天）
    print("\n🔍 测试1: 搜索国际教育新闻")
    tester.search_education_news(timespan="3d")
    
    # 2. 按国家搜索
    print("\n🔍 测试2: 按国家搜索")
    countries = [
        ("United Kingdom", "university admission"),
        ("United States", "student visa"),
        ("Australia", "international student")
    ]
    
    for country, keyword in countries[:2]:  # 只测试前2个
        tester.search_by_country(country, keyword)
    
    # 3. 多语言搜索演示
    print("\n🔍 测试3: 多语言搜索")
    tester.search_multilingual("international education")
    
    print("\n" + "=" * 60)
    print("✅ GDELT API 测试完成!")
    print("=" * 60)
    print("\n💡 提示:")
    print("   - GDELT完全免费，无调用次数限制")
    print("   - 支持复杂查询语法（AND, OR, NOT）")
    print("   - 每15分钟更新一次数据")
    print("   - 可与NewsCatcher互补使用")
    
    return True


if __name__ == "__main__":
    main()
