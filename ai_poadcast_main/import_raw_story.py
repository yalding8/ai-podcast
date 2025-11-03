#!/usr/bin/env python3
"""
Utility script to archive raw news articles into source_archive and keep the index updated.

Example:
    pbpaste | python ai_poadcast_main/import_raw_story.py \
        --title "UK Government Announces New Graduate Visa Route Changes" \
        --source "ICEF Monitor" \
        --url https://monitor.icef.com/2025/01/uk-graduate-visa-changes/ \
        --published-date 2025-01-28
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from html import unescape
from pathlib import Path
from typing import Iterable, List, Optional, Tuple
import unicodedata
import urllib.error
import urllib.request
from urllib.parse import urlparse, urlunparse


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ARCHIVE_DIR = PROJECT_ROOT / "source_archive"
INDEX_PATH = SOURCE_ARCHIVE_DIR / "_index.json"


def main() -> None:
    args = parse_args()
    validate_arguments(args)
    raw_text = read_text(args.text_source)
    fetched_html: Optional[str] = None
    if (not raw_text.strip()) and args.fetch:
        fetched_text, fetched_html = fetch_article_content(args.url, args.user_agent)
        raw_text = fetched_text
    raw_text = raw_text.strip()
    if not raw_text:
        sys.stderr.write("❌ 原始文本为空，请检查输入或使用 --fetch。\n")
        sys.exit(1)
    warn_if_short(raw_text)

    published = parse_date(args.published_date, "published-date")
    archive_date = parse_date(args.archive_date, "archive-date") or published or date.today()
    archive_date_str = archive_date.isoformat()
    published_str = published.isoformat() if published else None

    SOURCE_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    slug = determine_slug(args.slug, args.title, archive_date_str)
    raw_archive_dir = SOURCE_ARCHIVE_DIR / archive_date_str
    raw_archive_dir.mkdir(parents=True, exist_ok=True)

    raw_path = raw_archive_dir / f"{slug}.md"
    canonical_url = canonicalize_url(args.url)

    index_data = load_index()
    if not args.force and is_duplicate(index_data, canonical_url, args.url):
        sys.stderr.write("⚠️ 该 URL 已经存档。如需重复导入，请添加 --force。\n")
        sys.exit(1)

    timestamp = (
        datetime.now(timezone.utc)
        .replace(microsecond=False)
        .isoformat()
        .replace("+00:00", "Z")
    )

    metadata = {
        "title": args.title,
        "source": args.source,
        "url": args.url,
        "url_canonical": canonical_url,
        "published_date": published_str,
        "language": args.language,
        "tags": args.tags or None,
        "archive_date": archive_date_str,
        "imported_at": timestamp,
        "notes": args.notes or None,
        "fetched_from_url": bool(fetched_html),
        "word_count": count_words(raw_text),
        "char_count": len(raw_text),
    }

    write_raw_archive(raw_path, metadata, raw_text)
    html_path = None
    if fetched_html and args.store_html:
        html_path = raw_archive_dir / f"{slug}.html"
        html_path.write_text(fetched_html, encoding="utf-8")

    entry = {
        "slug": slug,
        "title": args.title,
        "source": args.source,
        "url": args.url,
        "url_canonical": canonical_url,
        "published_date": published_str,
        "archive_date": archive_date_str,
        "imported_at": timestamp,
        "raw_path": str(raw_path.relative_to(PROJECT_ROOT)),
        "language": args.language,
        "tags": args.tags,
        "notes": args.notes,
        "fetched_from_url": bool(fetched_html),
        "html_path": str(html_path.relative_to(PROJECT_ROOT)) if html_path else None,
        "word_count": count_words(raw_text),
        "char_count": len(raw_text),
    }
    update_index(index_data, entry)

    print("📦 已完成导入：")
    print(f"   • 原文档案：{entry['raw_path']}")
    if entry["html_path"]:
        print(f"   • 原始 HTML：{entry['html_path']}")
    print(f"   • 记录编号：{slug}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Archive a raw article into source_archive and update the index.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--title", required=True, help="News headline or working title.")
    parser.add_argument("--url", required=True, help="Canonical source URL.")
    parser.add_argument("--source", default="", help="Publisher or outlet name.")
    parser.add_argument(
        "--published-date",
        dest="published_date",
        help="Article publish date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--archive-date",
        dest="archive_date",
        help="Folder date for archiving (defaults to published-date or today).",
    )
    parser.add_argument(
        "--text-source",
        default="-",
        help="Path to the raw text file; use '-' to read from STDIN.",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Original article language (used for metadata only).",
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        help="Optional tags for quick lookup (space separated).",
    )
    parser.add_argument(
        "--slug",
        help="Manual slug override (otherwise derived from title).",
    )
    parser.add_argument(
        "--notes",
        help="Optional notes to store alongside the metadata.",
    )
    parser.add_argument("--force", action="store_true", help="Allow importing duplicate URLs.")
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch article content from --url when no text is provided. Requires network access when executed.",
    )
    parser.add_argument(
        "--user-agent",
        default="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0 Safari/537.36",
        help="Custom User-Agent header used when fetching article content.",
    )
    parser.add_argument(
        "--store-html",
        action="store_true",
        help="Store raw HTML response alongside the markdown archive when fetching content.",
    )
    return parser.parse_args()


def read_text(source: str) -> str:
    if source == "-":
        if sys.stdin.isatty():
            return ""
        return sys.stdin.read()
    from path_utils import safe_path
    path = safe_path(source, PROJECT_ROOT)
    if not path.exists():
        sys.stderr.write(f"❌ 找不到文本文件：{source}\n")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def fetch_article_content(url: str, user_agent: str) -> Tuple[str, Optional[str]]:
    if not url:
        sys.stderr.write("❌ 未提供 URL，无法抓取原文。\n")
        sys.exit(1)
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            raw_bytes = response.read()
    except urllib.error.HTTPError as exc:
        sys.stderr.write(f"❌ 抓取失败（HTTP {exc.code}）：{exc.reason}\n")
        sys.exit(1)
    except urllib.error.URLError as exc:
        sys.stderr.write(f"❌ 抓取失败（网络错误）：{exc.reason}\n")
        sys.exit(1)
    raw_html = raw_bytes.decode(charset, errors="replace")
    text = extract_readable_text(raw_html)
    if not text.strip():
        sys.stderr.write("⚠️ 成功抓取页面，但未能解析正文，请检查页面结构或手动粘贴。\n")
        sys.exit(1)
    return text, raw_html


def extract_readable_text(html: str) -> str:
    # 优先使用可用的第三方解析器，保证效果最佳。
    # 若环境未安装依赖，则回退到内置的朴素解析逻辑。
    try:
        from bs4 import BeautifulSoup  # type: ignore

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "header", "footer", "aside", "nav"]):
            tag.decompose()
        preferred_selectors = [
            "div.single-content",
            "div.post-content",
            "div.article-content",
            "div.entry-content",
            "section.article__body",
            "section.article-body",
            "article",
            "main",
        ]
        article = None
        for selector in preferred_selectors:
            article = soup.select_one(selector)
            if article and article.get_text(strip=True):
                break
        if article is None:
            article = soup.body or soup
        text = article.get_text("\n", strip=True)
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line)
    except ModuleNotFoundError:
        cleaned = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", "", html)
        cleaned = re.sub(r"(?s)<[^>]+>", "\n", cleaned)
        cleaned = unescape(cleaned)
        lines = [line.strip() for line in cleaned.splitlines()]
        return "\n".join(line for line in lines if line)


def parse_date(value: Optional[str], field_name: str) -> Optional[date]:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    sys.stderr.write(f"⚠️ 无法解析 {field_name}: {value}，将按原样存储。\n")
    return None


def determine_slug(custom_slug: Optional[str], title: str, archive_date: str) -> str:
    from path_utils import safe_path
    base = custom_slug or slugify(title)
    if not base:
        base = f"article-{archive_date}"
    raw_dir = safe_path(SOURCE_ARCHIVE_DIR / archive_date, PROJECT_ROOT)
    raw_dir.mkdir(parents=True, exist_ok=True)
    slug = base
    counter = 2
    while (raw_dir / f"{slug}.md").exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-").lower()
    return value


def write_raw_archive(path: Path, metadata: dict, raw_text: str) -> None:
    metadata_clean = {k: v for k, v in metadata.items() if v not in (None, [], "")}
    payload = [
        "---",
        json.dumps(metadata_clean, ensure_ascii=False, indent=2),
        "---",
        "",
        raw_text,
        "",
    ]
    path.write_text("\n".join(payload), encoding="utf-8")


def load_index() -> List[dict]:
    if not INDEX_PATH.exists():
        return []
    try:
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        sys.stderr.write("⚠️ 索引文件损坏，已忽略。\n")
        return []


def update_index(current: Iterable[dict], entry: dict) -> None:
    entries = list(current)
    entries.append(entry)
    # Keep the index ordered by import time (newest first).
    entries.sort(key=lambda item: item.get("imported_at") or "", reverse=True)
    INDEX_PATH.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def validate_arguments(args: argparse.Namespace) -> None:
    errors: List[str] = []
    title = (args.title or "").strip()
    if not title:
        errors.append("标题不能为空。")
    url_error = validate_url(args.url)
    if url_error:
        errors.append(url_error)
    if errors:
        for err in errors:
            sys.stderr.write(f"❌ {err}\n")
        sys.exit(1)
    if not args.source.strip():
        sys.stderr.write("⚠️ 来源（--source）为空，将在索引中记录为空值。\n")
    if not args.published_date:
        sys.stderr.write("⚠️ 未提供发布日期（--published-date）。建议补充以方便检索。\n")
    if args.tags:
        cleaned = sorted({tag.strip() for tag in args.tags if tag.strip()})
        args.tags = cleaned or None


def validate_url(url: str) -> Optional[str]:
    try:
        parsed = urlparse(url)
    except ValueError:
        return "URL 无法解析，请确认格式是否正确。"
    if parsed.scheme not in {"http", "https"}:
        return "URL 必须以 http:// 或 https:// 开头。"
    if not parsed.netloc:
        return "URL 缺少域名部分，请检查。"
    return None


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") or "/"
    canonical = parsed._replace(netloc=netloc, path=path, fragment="", params="")
    return urlunparse(canonical)


def is_duplicate(index_data: Iterable[dict], canonical_url: str, original_url: str) -> bool:
    original_canonical = canonicalize_url(original_url)
    for entry in index_data:
        existing = entry.get("url_canonical") or entry.get("url")
        if not existing:
            continue
        existing_canonical = canonicalize_url(existing)
        if existing_canonical in {canonical_url, original_canonical}:
            return True
    return False


def warn_if_short(raw_text: str) -> None:
    if count_words(raw_text) < 80:
        sys.stderr.write("⚠️ 原文少于80词，可能不是完整新闻，请确认输入是否正确。\n")


def count_words(raw_text: str) -> int:
    return len(re.findall(r"\b\w+\b", raw_text))


if __name__ == "__main__":
    main()
