#!/usr/bin/env python3
"""
播客新闻采集系统 - 集成测试脚本
演示从采集到处理的完整流程
"""

import json
import os
from datetime import datetime
from typing import List, Dict

class NewsAggregator:
    """新闻聚合器 - 核心引擎"""
    
    def __init__(self):
        # 使用相对路径，自动适配任何操作系统
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        self.data_dir = os.path.join(project_root, "data")
        self.sources = self.load_source_config()
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_source_config(self) -> Dict:
        """加载信息源配置"""
        return {
            "tier1": [
                {"name": "ICEF Monitor", "url": "https://monitor.icef.com/feed/", "priority": 95},
                {"name": "The PIE News", "url": "https://thepienews.com/feed/", "priority": 95},
                {"name": "Inside Higher Ed", "url": "https://www.insidehighered.com/rss/all", "priority": 90},
            ],
            "tier2": {
                "newscatcher": {
                    "enabled": False,
                    "queries": ["international education", "student visa"],
                    "countries": ["US", "GB", "CA", "AU"]
                },
                "gdelt": {
                    "enabled": True,
                    "queries": [
                        "international student OR study abroad",
                        "university admission OR college admission",
                        "student visa policy"
                    ],
                    "timespan": "3d"
                }
            },
            "tier3": {
                "rsshub": {
                    "enabled": True,
                    "routes": [
                        "https://www.ielts.org/news-and-insights",
                        "ets/news",
                        "gov/uk/visas-immigration"
                    ]
                }
            }
        }
    
    def collect_demo_data(self) -> List[Dict]:
        """生成演示数据（模拟真实采集结果）"""
        print("=" * 70)
        print("🔍 新闻采集系统 - 演示模式")
        print("=" * 70)
        print("\n正在模拟从多个来源采集新闻...\n")
        
        demo_articles = [
            {
                "id": "demo_001",
                "source": "ICEF Monitor",
                "source_tier": 1,
                "title": "UK Government Announces New Graduate Visa Route Changes",
                "url": "https://monitor.icef.com/2025/01/uk-graduate-visa-changes/",
                "published_date": "2025-01-28T09:00:00Z",
                "language": "en",
                "country": "GB",
                "category": "policy",
                "tags": ["visa", "UK", "graduate", "policy_change"],
                "priority_score": 95,
                "summary": "英国政府宣布对毕业生签证路径进行重大调整，影响2025年后的国际学生。新政策要求更高的薪资门槛和更严格的担保要求。",
                "key_points": [
                    "新的薪资门槛提高至£28,000",
                    "担保要求更严格",
                    "2025年4月生效"
                ],
                "entities": {
                    "organizations": ["UK Home Office", "UKVI"],
                    "locations": ["United Kingdom"]
                }
            },
            {
                "id": "demo_002",
                "source": "The PIE News",
                "source_tier": 1,
                "title": "US Universities Report 12% Increase in International Applications",
                "url": "https://thepienews.com/2025/01/us-intl-applications-surge/",
                "published_date": "2025-01-27T14:30:00Z",
                "language": "en",
                "country": "US",
                "category": "admission",
                "tags": ["USA", "applications", "statistics"],
                "priority_score": 90,
                "summary": "美国大学国际学生申请量同比增长12%，其中来自中国和印度的申请增长最为显著。工程和计算机科学专业最受欢迎。",
                "key_points": [
                    "国际申请总量增长12%",
                    "中国、印度学生申请增长最快",
                    "STEM专业持续热门"
                ],
                "entities": {
                    "organizations": ["Common App", "NAFSA"],
                    "locations": ["United States", "China", "India"]
                }
            },
            {
                "id": "demo_003",
                "source": "GDELT",
                "source_tier": 2,
                "title": "Australia Extends Post-Study Work Rights for Master's Graduates",
                "url": "https://www.homeaffairs.gov.au/news/post-study-work-extension",
                "published_date": "2025-01-26T08:15:00Z",
                "language": "en",
                "country": "AU",
                "category": "policy",
                "tags": ["Australia", "PSW", "visa", "masters"],
                "priority_score": 88,
                "summary": "澳大利亚政府宣布延长硕士毕业生的毕业后工作权利至3年，以吸引更多高技能国际学生。此举被视为与加拿大和英国竞争人才的重要举措。",
                "key_points": [
                    "硕士毕业生PSW延长至3年",
                    "博士生延长至4年",
                    "立即生效"
                ],
                "entities": {
                    "organizations": ["Dept of Home Affairs"],
                    "locations": ["Australia"]
                }
            },
            {
                "id": "demo_004",
                "source": "Times Higher Education",
                "source_tier": 1,
                "title": "QS World University Rankings 2026: Major Shifts Expected",
                "url": "https://www.timeshighereducation.com/qs-2026-preview",
                "published_date": "2025-01-25T11:00:00Z",
                "language": "en",
                "country": "GB",
                "category": "rankings",
                "tags": ["rankings", "QS", "universities"],
                "priority_score": 85,
                "summary": "QS将于6月发布2026年世界大学排名，预计评估方法将有重大调整，更加重视就业能力和可持续发展指标。",
                "key_points": [
                    "新增就业能力权重",
                    "可持续发展成为新指标",
                    "6月6日正式发布"
                ],
                "entities": {
                    "organizations": ["QS", "THE"],
                    "locations": []
                }
            },
            {
                "id": "demo_005",
                "source": "IELTS官网",
                "source_tier": 3,
                "title": "IELTS Launches New Computer-Delivered Test Format in 50 Cities",
                "url": "https://www.ielts.org/news/computer-delivered-expansion",
                "published_date": "2025-01-24T10:00:00Z",
                "language": "en",
                "country": "Global",
                "category": "exam",
                "tags": ["IELTS", "exam", "computer-based"],
                "priority_score": 82,
                "summary": "雅思宣布在全球50个城市推出新的机考格式，提供更灵活的考试日期和更快的成绩发布（3天内）。新格式包括改进的用户界面和辅助功能。",
                "key_points": [
                    "50个新城市推出机考",
                    "3天内出成绩",
                    "改进的用户界面"
                ],
                "entities": {
                    "organizations": ["IELTS", "British Council"],
                    "locations": []
                }
            }
        ]
        
        print(f"✅ 成功模拟采集 {len(demo_articles)} 条新闻\n")
        
        # 显示采集结果
        for article in demo_articles:
            print(f"📰 [{article['source']}] {article['title']}")
            print(f"   🏷️  {' | '.join(article['tags'])}")
            print(f"   ⭐ 优先级: {article['priority_score']}")
            print()
        
        return demo_articles
    
    def deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """去重处理"""
        print("\n" + "=" * 70)
        print("🔄 去重与聚类...")
        print("=" * 70)
        
        # 简化演示：基于标题相似度
        seen_titles = set()
        unique_articles = []
        duplicates = 0
        
        for article in articles:
            title_lower = article['title'].lower()
            # 简单的重复检测（实际应用中使用向量相似度）
            is_duplicate = any(
                self._similarity(title_lower, seen.lower()) > 0.8 
                for seen in seen_titles
            )
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.add(article['title'])
            else:
                duplicates += 1
        
        print(f"📊 原始新闻: {len(articles)} 条")
        print(f"🗑️  去除重复: {duplicates} 条")
        print(f"✅ 保留唯一: {len(unique_articles)} 条\n")
        
        return unique_articles
    
    def _similarity(self, s1: str, s2: str) -> float:
        """简单的字符串相似度计算"""
        words1 = set(s1.split())
        words2 = set(s2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def categorize_and_score(self, articles: List[Dict]) -> List[Dict]:
        """分类和打分"""
        print("=" * 70)
        print("📊 分类与优先级评分...")
        print("=" * 70)
        
        # 按类别统计
        categories = {}
        for article in articles:
            cat = article.get('category', 'other')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n类别分布:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   {cat:15s}: {count} 条")
        
        # 按优先级排序
        articles.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        print("\n优先级排序（Top 3）:")
        for i, article in enumerate(articles[:3], 1):
            print(f"   {i}. [{article['priority_score']}分] {article['title']}")
        
        print()
        return articles
    
    def generate_summary(self, articles: List[Dict]) -> Dict:
        """生成播客内容摘要"""
        print("=" * 70)
        print("📝 生成播客脚本摘要...")
        print("=" * 70)
        
        # 按类别组织
        categorized = {}
        for article in articles:
            cat = article.get('category', 'other')
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(article)
        
        # 生成脚本结构
        script = {
            "episode_number": 1,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "title": f"国际教育资讯 - {datetime.now().strftime('%Y年%m月%d日')}",
            "sections": []
        }
        
        # 重要政策变化
        if 'policy' in categorized:
            script['sections'].append({
                "title": "本周重要政策",
                "articles": categorized['policy'][:2]
            })
        
        # 院校动态
        if 'admission' in categorized or 'rankings' in categorized:
            admission_articles = categorized.get('admission', [])
            ranking_articles = categorized.get('rankings', [])
            script['sections'].append({
                "title": "院校与排名动态",
                "articles": (admission_articles + ranking_articles)[:2]
            })
        
        # 考试更新
        if 'exam' in categorized:
            script['sections'].append({
                "title": "考试机构更新",
                "articles": categorized['exam'][:2]
            })
        
        # 显示脚本结构
        print(f"\n节目标题: {script['title']}")
        print(f"节目日期: {script['date']}")
        print(f"\n内容结构:")
        
        for i, section in enumerate(script['sections'], 1):
            print(f"\n{i}. {section['title']}")
            for j, article in enumerate(section['articles'], 1):
                print(f"   {i}.{j} {article['title']}")
                print(f"       {article['summary'][:100]}...")
        
        return script
    
    def save_results(self, articles: List[Dict], script: Dict):
        """保存处理结果"""
        print("\n" + "=" * 70)
        print("💾 保存结果...")
        print("=" * 70)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 确保输出目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 保存原始数据
        articles_file = os.path.join(self.data_dir, f"articles_{timestamp}.json")
        with open(articles_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"✅ 新闻数据: {articles_file}")
        
        # 保存脚本
        script_file = os.path.join(self.data_dir, f"script_{timestamp}.json")
        with open(script_file, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)
        print(f"✅ 播客脚本: {script_file}")
        
        # 生成Markdown报告
        report_file = os.path.join(self.data_dir, f"report_{timestamp}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# {script['title']}\n\n")
            f.write(f"**日期**: {script['date']}\n\n")
            f.write(f"**采集新闻数**: {len(articles)}\n\n")
            f.write("---\n\n")
            
            for section in script['sections']:
                f.write(f"## {section['title']}\n\n")
                for article in section['articles']:
                    f.write(f"### {article['title']}\n\n")
                    f.write(f"**来源**: {article['source']} | **国家**: {article['country']}\n\n")
                    f.write(f"{article['summary']}\n\n")
                    f.write(f"**关键要点**:\n")
                    for point in article['key_points']:
                        f.write(f"- {point}\n")
                    f.write(f"\n[阅读原文]({article['url']})\n\n")
                    f.write("---\n\n")
        
        print(f"✅ 报告文档: {report_file}")
    
    def run_full_pipeline(self):
        """运行完整流程"""
        print("\n" + "🚀" * 35)
        print("启动播客新闻采集系统")
        print("🚀" * 35 + "\n")
        
        # 1. 采集
        articles = self.collect_demo_data()
        
        # 2. 去重
        unique_articles = self.deduplicate(articles)
        
        # 3. 分类和打分
        scored_articles = self.categorize_and_score(unique_articles)
        
        # 4. 生成脚本
        script = self.generate_summary(scored_articles)
        
        # 5. 保存结果
        self.save_results(scored_articles, script)
        
        print("\n" + "=" * 70)
        print("✅ 完整流程执行成功!")
        print("=" * 70)
        print("\n📋 下一步:")
        print("1. 查看生成的报告文件了解新闻内容")
        print("2. 根据脚本JSON生成播客音频")
        print("3. 人工审核并调整内容")
        print("4. 使用TTS工具生成最终音频")
        print("\n💡 提示:")
        print("- 实际部署时，替换演示数据为真实API调用")
        print("- 配置NewsCatcher和GDELT API密钥")
        print("- 部署RSSHub服务（docker-compose up -d）")


def main():
    aggregator = NewsAggregator()
    aggregator.run_full_pipeline()


if __name__ == "__main__":
    main()
