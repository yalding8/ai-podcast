"""命令行接口"""

import argparse
import sys
from datetime import date
from pathlib import Path

from .core import ArchiveManager, IndexManager
from .collectors import WebFetcher
from .processors import ContentValidator
from .utils import slugify, parse_date


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ARCHIVE_DIR = PROJECT_ROOT / "source_archive"
INDEX_PATH = SOURCE_ARCHIVE_DIR / "_index.json"


def import_article(args: argparse.Namespace) -> None:
    """导入文章到档案"""
    # 初始化管理器
    archive_mgr = ArchiveManager(SOURCE_ARCHIVE_DIR)
    index_mgr = IndexManager(INDEX_PATH)
    
    # 读取内容
    if args.text_source == "-":
        if sys.stdin.isatty():
            content = ""
        else:
            content = sys.stdin.read()
    else:
        content = Path(args.text_source).read_text(encoding="utf-8")
    
    # 抓取网页
    html = None
    if not content.strip() and args.fetch:
        fetcher = WebFetcher(args.user_agent)
        content, html = fetcher.fetch(args.url)
    
    if not content.strip():
        sys.stderr.write("❌ 内容为空\n")
        sys.exit(1)
    
    # 校验
    validator = ContentValidator()
    if validator.is_too_short(content):
        sys.stderr.write("⚠️ 内容少于80词\n")
    
    # 检查重复
    if not args.force and index_mgr.is_duplicate(args.url):
        sys.stderr.write("⚠️ URL已存在，使用--force强制导入\n")
        sys.exit(1)
    
    # 生成slug和日期
    published = parse_date(args.published_date)
    archive_date = parse_date(args.archive_date) or published or date.today()
    slug = args.slug or slugify(args.title)
    
    # 保存档案
    metadata = {
        "title": args.title,
        "source": args.source,
        "url": args.url,
        "published_date": published.isoformat() if published else None,
        "language": args.language,
        "tags": args.tags,
        "word_count": validator.count_words(content),
    }
    
    md_path, html_path = archive_mgr.save_article(
        slug, archive_date, metadata, content, html if args.store_html else None
    )
    
    # 更新索引
    entry = {
        "slug": slug,
        "title": args.title,
        "url": args.url,
        "archive_date": archive_date.isoformat(),
        "raw_path": str(md_path.relative_to(PROJECT_ROOT)),
    }
    index_mgr.add_entry(entry)
    
    print(f"✅ 已导入: {entry['raw_path']}")


def main() -> None:
    """主入口"""
    parser = argparse.ArgumentParser(description="AI Podcast CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # import子命令
    import_parser = subparsers.add_parser("import", help="导入文章")
    import_parser.add_argument("--title", required=True)
    import_parser.add_argument("--url", required=True)
    import_parser.add_argument("--source", default="")
    import_parser.add_argument("--published-date")
    import_parser.add_argument("--archive-date")
    import_parser.add_argument("--text-source", default="-")
    import_parser.add_argument("--language", default="en")
    import_parser.add_argument("--tags", nargs="*")
    import_parser.add_argument("--slug")
    import_parser.add_argument("--force", action="store_true")
    import_parser.add_argument("--fetch", action="store_true")
    import_parser.add_argument("--user-agent")
    import_parser.add_argument("--store-html", action="store_true")
    
    args = parser.parse_args()
    
    if args.command == "import":
        import_article(args)


if __name__ == "__main__":
    main()
