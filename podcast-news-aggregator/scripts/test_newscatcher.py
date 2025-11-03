#!/usr/bin/env python3
"""
NewsCatcher API 测试脚本
功能：测试API连接并搜索国际教育相关新闻
"""

import requests
import json
from datetime import datetime, timedelta
import os

class NewsCatcherTester:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.newscatcherapi.com/v2"
        self.headers = {
            "x-api-key": api_key
        }
    
    def test_connection(self):
        """测试API连接"""
        print("=" * 60)
        print("测试 NewsCatcher API 连接...")
        print("=" * 60)
        
        # 使用sources endpoint测试（最简单）
        url = f"{self.base_url}/sources"
        params = {
            "lang": "en",
            "countries": "US"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API连接成功!")
                print(f"📊 可用美国英文新闻源数量: {len(data.get('sources', []))}")
                return True
            elif response.status_code == 401:
                print("❌ API密钥无效，请检查配置")
                return False
            else:
                print(f"❌ API返回错误: {response.status_code}")
                print(f"错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 连接失败: {str(e)}")
            return False
    
    def search_education_news(self, days=30):
        """搜索国际教育新闻"""
        print("\n" + "=" * 60)
        print(f"搜索过去{days}天的国际教育新闻...")
        print("=" * 60)
        
        url = f"{self.base_url}/search"
        
        # 计算时间范围
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
        to_date = datetime.now().strftime('%Y/%m/%d')
        
        params = {
            "q": "(international education) OR (university admission) OR (student visa) OR (study abroad)",
            "lang": "en",
            "from": from_date,
            "to": to_date,
            "page_size": 10,
            "page": 1
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                total_hits = data.get('total_hits', 0)
                
                print(f"\n📈 总共找到 {total_hits} 条相关新闻")
                print(f"📄 显示前 {len(articles)} 条:\n")
                
                results = []
                for i, article in enumerate(articles, 1):
                    result = {
                        'title': article.get('title', 'N/A'),
                        'source': article.get('clean_url', 'N/A'),
                        'published': article.get('published_date', 'N/A'),
                        'url': article.get('link', 'N/A'),
                        'summary': article.get('summary', 'N/A')[:150] + "..."
                    }
                    results.append(result)
                    
                    print(f"{i}. 【{result['source']}】{result['title']}")
                    print(f"   🕒 {result['published']}")
                    print(f"   📝 {result['summary']}")
                    print(f"   🔗 {result['url']}")
                    print()
                
                # 保存结果
                self.save_results(results, "newscatcher_test")
                return results
                
            else:
                print(f"❌ 搜索失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 搜索出错: {str(e)}")
            return []
    
    def search_by_country(self, country_code, topic="education"):
        """按国家搜索教育新闻"""
        print("\n" + "=" * 60)
        print(f"搜索 {country_code} 的{topic}新闻...")
        print("=" * 60)
        
        url = f"{self.base_url}/latest_headlines"
        
        params = {
            "countries": country_code,
            "topic": topic,
            "lang": "en",
            "page_size": 5
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                print(f"\n找到 {len(articles)} 条头条新闻:\n")
                
                for i, article in enumerate(articles, 1):
                    print(f"{i}. {article.get('title', 'N/A')}")
                    print(f"   来源: {article.get('clean_url', 'N/A')}")
                    print(f"   时间: {article.get('published_date', 'N/A')}")
                    print()
                
                return articles
            else:
                print(f"❌ 搜索失败: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 搜索出错: {str(e)}")
            return []
    
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
    # 读取API密钥（临时使用演示密钥）
    # 用户需要在 https://www.newscatcherapi.com/ 注册获取真实密钥
    
    print("=" * 60)
    print("NewsCatcher API 测试工具")
    print("=" * 60)
    print("\n⚠️  注意：请先注册并获取API密钥")
    print("📍 注册地址: https://www.newscatcherapi.com/")
    print("🎁 免费版: 200次调用/月\n")
    
    api_key = os.getenv('NEWSCATCHER_API_KEY', '')
    
    if not api_key or api_key == 'your_newscatcher_key_here':
        print("❌ 未检测到有效的API密钥")
        print("\n请按以下步骤操作:")
        print("1. 访问 https://www.newscatcherapi.com/ 注册账号")
        print("2. 获取API密钥")
        print("3. 设置环境变量:")
        print("   export NEWSCATCHER_API_KEY='你的密钥'")
        print("\n或者直接在下方输入密钥进行测试:\n")
        
        api_key = input("请输入API密钥 (或按Enter跳过): ").strip()
        
        if not api_key:
            print("\n⏭️  跳过NewsCatcher测试，将继续测试GDELT...")
            return False
    
    # 创建测试实例
    tester = NewsCatcherTester(api_key)
    
    # 测试连接
    if not tester.test_connection():
        return False
    
    # 搜索国际教育新闻
    tester.search_education_news(days=30)
    
    # 按国家搜索
    print("\n测试按国家搜索功能...")
    countries = ['GB', 'US', 'CA', 'AU']  # 英美加澳
    for country in countries[:2]:  # 只测试前2个，节省配额
        tester.search_by_country(country, topic="education")
    
    print("\n" + "=" * 60)
    print("✅ NewsCatcher API 测试完成!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    main()