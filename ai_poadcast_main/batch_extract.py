#!/usr/bin/env python3
"""
批量提炼新闻要点
先一次性处理所有新闻，生成中文摘要，然后再人工审核
"""

import argparse
import json
from process_queue import fetch_article_text, extract_key_points

def batch_extract(queue_file="ai_poadcast_main/news_queue.json", min_priority=8,
                  provider=None, model=None):
    """批量提炼"""
    with open(queue_file) as f:
        queue = json.load(f)
    
    items = [item for item in queue['items'] if item['priority'] >= min_priority]
    
    print(f"📥 准备提炼 {len(items)} 条新闻...")
    
    results = []
    
    for i, item in enumerate(items, 1):
        print(f"\n[{i}/{len(items)}] {item['title'][:50]}...")
        
        # 抓取正文
        text = fetch_article_text(item['url'])
        
        if text:
            # 提炼要点
            summary = extract_key_points(item['title'], item['url'], text,
                                         provider=provider, model=model)
            
            results.append({
                **item,
                'chinese_summary': summary,
                'article_length': len(text)
            })
        else:
            results.append({
                **item,
                'chinese_summary': '⚠️ 无法抓取正文',
                'article_length': 0
            })
    
    # 保存结果
    output_file = "ai_poadcast_main/news_queue_with_summaries.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(results),
            'items': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存到: {output_file}")
    
    # 生成可读报告
    report_file = "ai_poadcast_main/daily_review_cn.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 每日新闻审核（中文摘要）\n\n")
        
        for i, item in enumerate(results, 1):
            f.write(f"## [{i}] {item['title']}\n\n")
            f.write(f"**来源：** {item['source']} | **优先级：** {item['priority']}\n\n")
            f.write(f"**URL：** {item['url']}\n\n")
            f.write(f"### 中文提炼\n\n")
            f.write(f"{item['chinese_summary']}\n\n")
            f.write("---\n\n")
    
    print(f"✅ 可读报告: {report_file}")
    print(f"\n💡 现在可以打开Markdown文件慢慢看，决定哪些值得导入")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量提炼新闻要点")
    parser.add_argument("--queue-file", default="ai_poadcast_main/news_queue.json",
                        help="待处理新闻队列文件路径")
    parser.add_argument("--min-priority", type=int, default=8,
                        help="最低优先级")
    parser.add_argument("--provider", help="要点生成模型提供方（如 openai、anthropic）")
    parser.add_argument("--model", help="要点生成模型名称")
    args = parser.parse_args()
    batch_extract(args.queue_file, args.min_priority, args.provider, args.model)
