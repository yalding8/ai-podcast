#!/usr/bin/env python3
"""
Quick lookup utility for `source_archive/_index.json`.

Examples:
    python ai_poadcast_main/search_source_index.py --date 2025-10-28
    python ai_poadcast_main/search_source_index.py --source "The PIE" --limit 5
    python ai_poadcast_main/search_source_index.py --tag policy --tag visa
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = PROJECT_ROOT / "source_archive" / "_index.json"


def main() -> None:
    args = parse_args()
    index = load_index()
    if not index:
        sys.stderr.write("⚠️ 索引为空，尚未导入任何原文。\n")
        return

    results = apply_filters(index, args)
    total = len(results)
    if args.count_only:
        print(total)
        return

    if args.json_output:
        print(json.dumps(results[: args.limit], ensure_ascii=False, indent=2))
        if total > args.limit:
            sys.stderr.write(f"⚠️ 仅显示前 {args.limit} 条，共 {total} 条结果。\n")
        return

    if not results:
        print("（未找到匹配项）")
        return

    print(f"共匹配 {total} 条记录，显示前 {min(args.limit, total)} 条：\n")
    for entry in results[: args.limit]:
        print(format_entry(entry))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search and filter entries stored in source_archive/_index.json",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--date", help="过滤归档日期（YYYY-MM-DD，可只写年份或年月前缀）。")
    parser.add_argument("--source", help="按来源名称模糊匹配。")
    parser.add_argument("--title", help="按标题模糊匹配。")
    parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        help="按标签过滤（可重复使用，需全部匹配）。",
    )
    parser.add_argument("--url", help="按 URL 精确匹配。")
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="限制输出条数。",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="以 JSON 形式输出结果。",
    )
    parser.add_argument(
        "--count",
        dest="count_only",
        action="store_true",
        help="仅输出匹配数量。",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="忽略其它筛选项，仅查看最近一条。",
    )
    return parser.parse_args()


def load_index() -> List[dict]:
    if not INDEX_PATH.exists():
        sys.stderr.write(f"❌ 未找到索引文件：{INDEX_PATH}\n")
        return []
    try:
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"❌ 索引文件解析失败：{exc}\n")
        return []


def apply_filters(index: Iterable[dict], args: argparse.Namespace) -> List[dict]:
    entries = list(index)
    if args.latest:
        return entries[:1] if entries else []

    def match(entry: dict) -> bool:
        if args.url and entry.get("url") != args.url and entry.get("url_canonical") != args.url:
            return False
        if args.date:
            archive_date = entry.get("archive_date") or ""
            if not archive_date.startswith(args.date):
                return False
        if args.source:
            source = (entry.get("source") or "").lower()
            if args.source.lower() not in source:
                return False
        if args.title:
            title = (entry.get("title") or "").lower()
            if args.title.lower() not in title:
                return False
        if args.tags:
            entry_tags = {tag.lower() for tag in entry.get("tags") or []}
            query_tags = {tag.lower() for tag in args.tags if tag}
            if not query_tags.issubset(entry_tags):
                return False
        return True

    return [entry for entry in entries if match(entry)]


def format_entry(entry: dict) -> str:
    archive_date = entry.get("archive_date") or "未知日期"
    title = entry.get("title") or "（无标题）"
    source = entry.get("source") or "（来源未填写）"
    url = entry.get("url") or "（无链接）"
    tags = ", ".join(entry.get("tags") or [])
    word_count = entry.get("word_count")
    fetched = "✅" if entry.get("fetched_from_url") else "✂️"
    lines = [
        f"- {archive_date} | {source} | {title}",
        f"  URL: {url}",
        f"  记录编号: {entry.get('slug')} | 词数: {word_count or '未知'} | 抓取: {fetched}",
    ]
    if tags:
        lines.append(f"  标签: {tags}")
    prompt_path = entry.get("prompt_path")
    if prompt_path:
        lines.append(f"  Prompt: {prompt_path}")
    raw_path = entry.get("raw_path")
    if raw_path:
        lines.append(f"  原文: {raw_path}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
