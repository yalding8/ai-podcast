#!/usr/bin/env python3

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
BATCH_SCRIPT = THIS_DIR / 'batch_extract.py'
QUEUE_SCRIPT = THIS_DIR / 'process_queue.py'
COLLECT_SCRIPT = THIS_DIR / 'collect_rss_feeds.py'
SCRAPE_SCRIPT = THIS_DIR / 'scrape_exam_sites.py'
NEWS_QUEUE_PATH = THIS_DIR / 'news_queue.json'
DAILY_REVIEW_PATH = THIS_DIR / 'daily_review.txt'
STAGE3_PROMPT_SCRIPT = THIS_DIR / 'prepare_stage3_prompt.py'
STAGE3_GENERATOR_SCRIPT = THIS_DIR / 'generate_stage3_script.py'
RSS_SUMMARY_PATH = THIS_DIR / 'logs' / 'rss_run_summary.json'


def load_queue_items() -> dict:
    if NEWS_QUEUE_PATH.exists():
        try:
            return json.loads(NEWS_QUEUE_PATH.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            pass
    return {'updated_at': None, 'total': 0, 'items': []}


def save_queue_items(data: dict) -> None:
    items = data.get('items', [])
    items.sort(key=lambda x: x.get('priority', 0), reverse=True)
    data['items'] = items
    data['total'] = len(items)
    data['updated_at'] = datetime.now(timezone.utc).isoformat()
    NEWS_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    NEWS_QUEUE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def merge_integrated_demo() -> int:
    spec_path = PROJECT_ROOT / 'podcast-news-aggregator' / 'scripts' / 'integrated_demo.py'
    if not spec_path.exists():
        print(f"  ⚠️ 找不到 demo 脚本：{spec_path}")
        return 0

    spec = importlib.util.spec_from_file_location('integrated_demo', spec_path)
    if spec is None or spec.loader is None:
        print("  ⚠️ 无法加载 demo 模块")
        return 0

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore
    except Exception as exc:  # pragma: no cover
        print(f"  ⚠️ 导入 demo 模块失败：{exc}")
        return 0

    if not hasattr(module, 'NewsAggregator'):
        print("  ⚠️ demo 模块缺少 NewsAggregator")
        return 0

    try:
        aggregator = module.NewsAggregator()  # type: ignore[attr-defined]
        articles = aggregator.collect_demo_data()
        articles = aggregator.deduplicate(articles)
        articles = aggregator.categorize_and_score(articles)
    except Exception as exc:  # pragma: no cover
        print(f"  ⚠️ 获取 demo 数据失败：{exc}")
        return 0

    now_iso = datetime.now(timezone.utc).isoformat()
    demo_items = []
    for article in articles:
        url = article.get('url')
        title = article.get('title')
        if not url or not title:
            continue
        score = article.get('priority_score', 70)
        priority = max(5, min(10, int(score / 10)))
        demo_items.append({
            'title': title,
            'url': url,
            'source': f"Demo · {article.get('source', 'Unknown')}",
            'published': article.get('published_date', ''),
            'summary': article.get('summary', '')[:200],
            'tags': article.get('tags', []),
            'priority': priority,
            'collected_at': now_iso,
        })

    if not demo_items:
        return 0

    queue_data = load_queue_items()
    existing_by_url = {item.get('url'): item for item in queue_data.get('items', []) if item.get('url')}

    merged = 0
    for item in demo_items:
        url = item['url']
        if url in existing_by_url:
            existing = existing_by_url[url]
            existing['priority'] = max(existing.get('priority', 0), item['priority'])
            existing_tags = set(existing.get('tags', []))
            new_tags = set(item.get('tags', []))
            existing['tags'] = sorted(existing_tags | new_tags)
            if not existing.get('summary') and item.get('summary'):
                existing['summary'] = item['summary']
        else:
            queue_data.setdefault('items', []).append(item)
            existing_by_url[url] = item
            merged += 1

    save_queue_items(queue_data)

    summary_payload = {}
    if RSS_SUMMARY_PATH.exists():
        try:
            summary_payload = json.loads(RSS_SUMMARY_PATH.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            summary_payload = {}
    if not isinstance(summary_payload, dict):
        summary_payload = {}
    sources_summary = summary_payload.setdefault('sources', {})
    sources_summary['Integrated Demo'] = {
        'status': 'success' if merged > 0 else 'skipped',
        'rss': 'demo',
        'raw_new_items': len(demo_items),
        'final_items': merged,
        'priority': 10,
        'reason': None if merged > 0 else 'no new items',
    }
    summary_payload['run_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    summary_payload['total_items'] = summary_payload.get('total_items', 0)
    RSS_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    RSS_SUMMARY_PATH.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding='utf-8')

    return merged
def run_command(cmd, env=None):
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env, text=True)
    return result.returncode


def generate_daily_review(priority: int = 8) -> None:
    review_sections: list[str] = []

    queue_items = []
    if NEWS_QUEUE_PATH.exists():
        try:
            payload = json.loads(NEWS_QUEUE_PATH.read_text(encoding='utf-8'))
            queue_items = payload.get('items', [])
        except json.JSONDecodeError as exc:
            print(f"⚠️ 无法解析队列 JSON：{exc}")
    else:
        print(f"⚠️ 找不到队列文件：{NEWS_QUEUE_PATH}")

    filtered = []
    for item in queue_items:
        if priority is not None and item.get('priority') != priority:
            continue
        filtered.append(item)

    review_sections.append(f"=== 优先级 {priority} 待审列表 ===")
    if filtered:
        for item in filtered:
            title = item.get('title', '未命名新闻')
            source = item.get('source', '未知来源')
            url = item.get('url', '')
            review_sections.append(f"[{source}] {title}\n  → {url}")
    else:
        review_sections.append("（无匹配条目）")

    summary_lines = []
    if RSS_SUMMARY_PATH.exists():
        try:
            summary_data = json.loads(RSS_SUMMARY_PATH.read_text(encoding='utf-8'))
            run_at = summary_data.get('run_at', '未知时间')
            sources = summary_data.get('sources', {})
            status_order = {'error': 0, 'success': 1, 'skipped': 2, 'pending': 3}
            summary_lines.append("=== RSS 采集概况 ===")
            summary_lines.append(f"运行时间：{run_at}")
            for source, data in sorted(
                sources.items(),
                key=lambda item: (
                    status_order.get(item[1].get('status', 'success'), 9),
                    -item[1].get('final_items', 0),
                    item[0],
                ),
            ):
                status = data.get('status', 'unknown')
                icon = {
                    'success': '✅',
                    'error': '❌',
                    'skipped': '⏭️',
                    'pending': '⚪️',
                }.get(status, '⚪️')
                raw_new = data.get('raw_new_items', 0)
                final_items = data.get('final_items', 0)
                priority_val = data.get('priority', '-')
                reason = data.get('reason')
                line = f"{icon} {source} | 新增: {raw_new} | 去重后: {final_items} | 优先级: {priority_val}"
                if reason:
                    line += f" | 备注: {reason}"
                summary_lines.append(line)
        except json.JSONDecodeError as exc:
            print(f"⚠️ 无法解析 RSS 汇总文件：{exc}")

    content_parts = ["\n".join(review_sections)]
    if summary_lines:
        content_parts.append("\n".join(summary_lines))

    DAILY_REVIEW_PATH.write_text("\n\n".join(content_parts).strip() + "\n", encoding='utf-8')
    print(f"🗒️ 已更新 {DAILY_REVIEW_PATH}（筛选优先级 {priority}）")

def main():
    parser = argparse.ArgumentParser(description='Run daily workflow tasks (Stage 0-3).')
    parser.add_argument('--collect', action='store_true', help='Run Stage 0: collect RSS feeds.')
    parser.add_argument('--scrape', action='store_true', help='After collection, run scrape_exam_sites.py.')
    parser.add_argument('--auto-import', type=int, help='Auto import top N items after collection (0 表示跳过)。')
    parser.add_argument('--auto-min-priority', type=int, default=9, help='Minimum priority for auto import (默认 9)。')
    parser.add_argument('--review-file-priority', type=int, default=8, help='Priority to include when writing daily_review.txt（默认8）。')
    parser.add_argument('--skip-review-file', action='store_true', help='Skip generating daily_review.txt。')
    parser.add_argument('--demo', action='store_true', help='Include integrated demo articles from podcast-news-aggregator.')
    parser.add_argument('--no-demo', action='store_true', help='Skip integrated demo articles even在默认模式下。')

    parser.add_argument('--extract', action='store_true', help='Run Stage 2: batch_extract to generate summaries.')
    parser.add_argument('--review', action='store_true', help='Run Stage 2: process_queue for interactive review.')
    parser.add_argument('--stage3', action='store_true', help='Run Stage 3 automation (prompt + script).')

    parser.add_argument('--provider', help='Override provider for batch extraction.')
    parser.add_argument('--model', help='Override model for batch extraction.')
    parser.add_argument('--auto', type=int, help='Pass through --auto to process_queue review step.')
    parser.add_argument('--min-priority', type=int, help='Override minimum priority for process_queue review.')
    parser.add_argument('--no-filter', action='store_true', help='Disable keyword filter in process_queue.')

    parser.add_argument('--stage3-count', type=int, help='News count for Stage 3 prompt (pass to prepare_stage3_prompt).')
    parser.add_argument('--stage3-min-priority', type=int, help='Minimum priority for Stage 3 prompt selection.')
    parser.add_argument('--stage3-select', nargs='*', type=int, help='Explicit indexes for Stage 3 prompt selection.')
    parser.add_argument('--stage3-date', help='Override Stage 3 episode date (YYYY-MM-DD).')

    parser.add_argument('--dry-run', action='store_true', help='Show commands without executing.')
    args = parser.parse_args()

    if args.no_demo:
        args.demo = False

    if not any([args.collect, args.extract, args.review, args.stage3]):
        args.collect = True
        args.extract = True
        args.review = True
        args.stage3 = True
        args.demo = False  # 默认禁用Demo
    elif args.collect and not args.demo and not args.no_demo:
        args.demo = False  # 默认禁用Demo

    env = os.environ.copy()

    if args.collect:
        print("\n📡 运行 Stage 0：采集 RSS")
        cmd = [sys.executable, str(COLLECT_SCRIPT)]
        if args.dry_run:
            print('DRY RUN: {}'.format(' '.join(cmd)))
        else:
            code = run_command(cmd, env=env)
            if code != 0:
                sys.exit(code)

        if args.scrape:
            print("\n🕷️ 运行 scrape_exam_sites.py")
            cmd = [sys.executable, str(SCRAPE_SCRIPT)]
            if args.dry_run:
                print('DRY RUN: {}'.format(' '.join(cmd)))
            else:
                code = run_command(cmd, env=env)
                if code != 0:
                    sys.exit(code)

        if args.demo and not args.dry_run:
            print("\n🎛️ 合并 Demo 新闻集 (podcast-news-aggregator)")
            added = merge_integrated_demo()
            if added:
                print(f"  ✅ 已加入 {added} 条 Demo 新闻")
            else:
                print("  ⚠️ Demo 新闻未加入或返回为空")
        elif args.demo and args.dry_run:
            print("DRY RUN: merge demo articles")

        auto_import = args.auto_import
        if auto_import is None:
            auto_import = 3
        if auto_import and auto_import > 0:
            print(f"\n🤖 自动导入前 {auto_import} 条（优先级 ≥ {args.auto_min_priority}）")
            cmd = [
                sys.executable,
                str(QUEUE_SCRIPT),
                '--auto', str(auto_import),
                '--min-priority', str(args.auto_min_priority),
            ]
            if args.dry_run:
                print('DRY RUN: {}'.format(' '.join(cmd)))
            else:
                code = run_command(cmd, env=env)
                if code != 0:
                    sys.exit(code)

        if not args.skip_review_file:
            generate_daily_review(args.review_file_priority)

    if args.extract:
        cmd = [sys.executable, str(BATCH_SCRIPT)]
        if args.provider:
            cmd.extend(['--provider', args.provider])
        if args.model:
            cmd.extend(['--model', args.model])
        if args.dry_run:
            print('DRY RUN: {}'.format(' '.join(cmd)))
        else:
            code = run_command(cmd, env=env)
            if code != 0:
                sys.exit(code)

    if args.review:
        cmd = [sys.executable, str(QUEUE_SCRIPT)]
        if args.auto is not None:
            cmd.extend(['--auto', str(args.auto)])
        if args.min_priority is not None:
            cmd.extend(['--min-priority', str(args.min_priority)])
        if args.no_filter:
            cmd.append('--no-filter')
        if args.dry_run:
            print('DRY RUN: {}'.format(' '.join(cmd)))
        else:
            code = run_command(cmd, env=env)
            if code != 0:
                sys.exit(code)

    if args.stage3:
        cmd = [sys.executable, str(STAGE3_PROMPT_SCRIPT)]
        if args.stage3_date:
            cmd.extend(['--date', args.stage3_date])
        if args.stage3_count is not None:
            cmd.extend(['--count', str(args.stage3_count)])
        if args.stage3_min_priority is not None:
            cmd.extend(['--min-priority', str(args.stage3_min_priority)])
        if args.stage3_select:
            cmd.append('--select')
            cmd.extend(str(i) for i in args.stage3_select)
        if args.dry_run:
            print('DRY RUN: {}'.format(' '.join(cmd)))
        else:
            code = run_command(cmd, env=env)
            if code != 0:
                sys.exit(code)

        cmd = [sys.executable, str(STAGE3_GENERATOR_SCRIPT)]
        if args.stage3_date:
            cmd.extend(['--date', args.stage3_date])
        if args.provider:
            cmd.extend(['--provider', args.provider])
        if args.model:
            cmd.extend(['--model', args.model])
        if args.dry_run:
            print('DRY RUN: {}'.format(' '.join(cmd)))
        else:
            code = run_command(cmd, env=env)
            if code != 0:
                sys.exit(code)

if __name__ == '__main__':
    main()
