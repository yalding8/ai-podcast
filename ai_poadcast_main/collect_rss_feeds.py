#!/usr/bin/env python3
"""
RSS 批量采集器
每天自动拉取所有RSS源，去重后保存到待处理队列
"""

import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import feedparser
import requests

# 导入配置
try:
    from feeds_config import TIER_1_SOURCES, TIER_2_SOURCES, TIER_3_SOURCES
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from config import RSS_SOURCES
        TIER_1_SOURCES = {k: v for k, v in RSS_SOURCES.items() if v.get('priority', 0) >= 9}
        TIER_2_SOURCES = {k: v for k, v in RSS_SOURCES.items() if 7 <= v.get('priority', 0) < 9}
        TIER_3_SOURCES = {k: v for k, v in RSS_SOURCES.items() if v.get('priority', 0) < 7}
    except ImportError:
        TIER_1_SOURCES = {}
        TIER_2_SOURCES = {}
        TIER_3_SOURCES = {}


BASE_DIR = Path(__file__).resolve().parent
FAIL_LOG_DIR = BASE_DIR / "logs"
FAIL_LOG_PATH = FAIL_LOG_DIR / "rss_failures.log"
FAILURE_RECORDS = []
RUN_SUMMARY: dict[str, dict] = {}

def normalize_url(url):
    """标准化URL，去除查询参数"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

# 在 collect_rss_feeds.py 中添加
from difflib import SequenceMatcher

def similar(a, b):
    """计算标题相似度"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def deduplicate_by_title(items, threshold=0.85):
    """按标题去重"""
    unique = []
    seen_titles = []
    
    for item in items:
        is_duplicate = False
        for seen in seen_titles:
            if similar(item['title'], seen) > threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique.append(item)
            seen_titles.append(item['title'])
    
    return unique

def generate_slug(title):
    """生成URL友好的slug"""
    import re
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:50]

def load_seen_urls():
    """加载已采集的URL列表"""
    from path_utils import safe_path
    from error_utils import safe_json_read
    
    index_file = safe_path("source_archive/_index.json", Path.cwd())
    data = safe_json_read(index_file, default=[])
    
    if isinstance(data, dict):
        sources = data.get('sources', [])
    elif isinstance(data, list):
        sources = data
    else:
        sources = []
    
    return {item['url'] for item in sources if isinstance(item, dict) and item.get('url')}

def _record_failure(source: str, rss_url: str, stage: str, error: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    FAILURE_RECORDS.append({
        "timestamp": timestamp,
        "source": source,
        "rss": rss_url,
        "stage": stage,
        "error": error,
    })
    summary = RUN_SUMMARY.setdefault(source, {
        "status": "error",
        "rss": rss_url,
        "raw_new_items": 0,
        "final_items": 0,
        "priority": None,
    })
    summary.update({
        "status": "error",
        "reason": error,
    })


def _request_feed(source: str, rss_url: str, retries: int = 3, backoff: float = 3.0) -> Optional[requests.Response]:
    from error_utils import safe_http_get
    
    headers = {
        "User-Agent": "Mozilla/5.0 (RSS Collector)",
        "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.1",
    }
    
    response = safe_http_get(rss_url, timeout=20, max_retries=retries, headers=headers)
    if response is None:
        error_text = f"RSS请求失败，已重试{retries}次"
        print(f"  ❌ {error_text}")
        _record_failure(source, rss_url, "request", error_text)
    
    return response


def _clean_html(text: str) -> str:
    """移除常见的非法 XML 字符并修复未闭合实体。"""
    cleaned = text.replace("&nbsp;", " ")
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", cleaned)
    return cleaned


def parse_feed_with_fallback(source: str, rss_url: str) -> Optional[feedparser.FeedParserDict]:
    response = _request_feed(source, rss_url)
    if not response:
        return None

    candidates = [response.content]
    # 尝试在忽略非法字符后的文本上重新解析
    cleaned_text = _clean_html(response.text)
    candidates.append(cleaned_text.encode(response.encoding or "utf-8", errors="ignore"))

    last_error = None
    for data in candidates:
        parsed = feedparser.parse(data)
        if not parsed.bozo:
            return parsed
        last_error = parsed.bozo_exception

    snippet = cleaned_text[:200].replace("\n", " ")
    error_text = f"{last_error} | 片段: {snippet}..."
    print(f"  ❌ RSS解析失败: {last_error} | 片段: {snippet}...")
    _record_failure(source, rss_url, "parse", error_text)
    return None


def fetch_rss(source_name, config, seen_urls, min_age_hours=0):
    """
    拉取单个RSS源
    
    Args:
        min_age_hours: 只采集N小时内的新闻（0=不限制）
    """
    print(f"\n📡 正在拉取: {source_name}")

    summary = RUN_SUMMARY.setdefault(source_name, {
        "status": "pending",
        "rss": config.get('rss', ''),
        "raw_new_items": 0,
        "final_items": 0,
        "priority": config.get('priority', 5),
    })

    if config.get('method') == 'scrape':
        print("  ⚠️  需要爬虫，跳过（稍后手动处理）")
        summary.update({
            "status": "skipped",
            "reason": "requires scraper",
        })
        return []

    rss_url = config.get('rss')
    if not rss_url:
        print("  ❌ 未配置RSS")
        summary.update({
            "status": "error",
            "reason": "rss url missing",
        })
        return []

    feed = parse_feed_with_fallback(source_name, rss_url)
    if feed is None:
        summary.update({
            "status": "error",
            "reason": "fetch/parse failed",
        })
        return []
    
    new_items = []
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=min_age_hours) if min_age_hours > 0 else None
    
    if config.get('max_items') is not None:
        max_items = int(config['max_items'])
    else:
        max_items = 10 if 'Google News' in source_name else 20
    
    collected = 0
    for entry in feed.entries:
        if collected >= max_items:
            break

        # 标准化URL
        link = getattr(entry, 'link', None)
        if not link:
            continue
        url = normalize_url(link)
        
        # 去重检查
        if url in seen_urls:
            continue
        
        # 检查发布时间
        if cutoff_time and hasattr(entry, 'published_parsed'):
            pub_time = datetime(*entry.published_parsed[:6])
            if pub_time < cutoff_time:
                continue
        
        new_items.append({
            'title': entry.title,
            'url': url,
            'source': source_name,
            'published': entry.get('published', ''),
            'summary': entry.get('summary', '')[:200],
            'tags': config.get('tags', []),
            'priority': config.get('priority', 5),
            'collected_at': datetime.now(timezone.utc).isoformat()
        })
        collected += 1
    
    print(f"  ✅ 发现 {len(new_items)} 条新内容")
    summary.update({
        "status": "success",
        "raw_new_items": len(new_items),
    })
    return new_items

def save_queue(items, output_file="ai_poadcast_main/news_queue.json"):
    """保存到待处理队列"""
    from path_utils import safe_path
    from error_utils import safe_json_write
    
    output_path = safe_path(output_file, Path.cwd())
    
    # 按优先级排序
    items.sort(key=lambda x: x['priority'], reverse=True)
    
    data = {
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'total': len(items),
        'items': items
    }
    
    if safe_json_write(output_path, data):
        print(f"\n💾 已保存 {len(items)} 条新闻到队列: {output_path}")
    else:
        print(f"\n❌ 保存队列失败: {output_path}")

def main():
    """主流程"""
    print("🚀 开始采集RSS新闻源...\n")
    
    # 加载已见URL
    seen_urls = load_seen_urls()
    print(f"📚 已有 {len(seen_urls)} 条历史记录")
    
    # 合并所有源
    all_sources = {**TIER_1_SOURCES, **TIER_2_SOURCES, **TIER_3_SOURCES}
    
    # 采集
    all_items = []
    for name, config in all_sources.items():
        items = fetch_rss(name, config, seen_urls, min_age_hours=0)  # 不限制时间
        all_items.extend(items)
    
    if all_items:
        before = len(all_items)
        all_items = deduplicate_by_title(all_items)
        if len(all_items) != before:
            print(f"\n🧹 标题去重：从 {before} 条缩减到 {len(all_items)} 条")

    final_counts = {}
    for item in all_items:
        source = item['source']
        final_counts[source] = final_counts.get(source, 0) + 1

    for source, data in RUN_SUMMARY.items():
        data['final_items'] = final_counts.get(source, 0)
        if data.get('status') == 'pending':
            data['status'] = 'success'
    for source, count in final_counts.items():
        if source not in RUN_SUMMARY:
            RUN_SUMMARY[source] = {
                "status": "success",
                "rss": all_sources.get(source, {}).get('rss', ''),
                "raw_new_items": count,
                "final_items": count,
                "priority": all_sources.get(source, {}).get('priority', 5),
            }
    
    # 保存
    if all_items:
        save_queue(all_items)
        
        # 生成可读报告
        print("\n" + "="*60)
        print("📊 采集汇总:")
        print("="*60)
        
        by_source = {}
        for item in all_items:
            source = item['source']
            by_source[source] = by_source.get(source, 0) + 1
        
        for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count} 条")
        
        print(f"\n✅ 总计: {len(all_items)} 条新内容")
    else:
        print("\n⚠️  没有发现新内容")

    summary_payload = {
        "run_at": datetime.now(timezone.utc).isoformat(timespec='seconds'),
        "total_items": len(all_items),
        "sources": RUN_SUMMARY,
    }
    FAIL_LOG_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = FAIL_LOG_DIR / "rss_run_summary.json"
    summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n📝 RSS 汇总写入: {summary_path}")

    if FAILURE_RECORDS:
        with FAIL_LOG_PATH.open('a', encoding='utf-8') as logf:
            logf.write("\n" + "=" * 80 + "\n")
            logf.write(f"Run at {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n")
            for record in FAILURE_RECORDS:
                logf.write(
                    f"[{record['timestamp']}] stage={record['stage']} | source={record['source']}\n"
                    f"  rss: {record['rss']}\n"
                    f"  error: {record['error']}\n"
                )
        print(f"\n⚠️  {len(FAILURE_RECORDS)} 个 RSS 源失败，详情见 {FAIL_LOG_PATH}")

if __name__ == "__main__":
    main()
