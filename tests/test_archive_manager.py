"""档案管理器测试"""

import pytest
import json
import sys
from pathlib import Path
from datetime import date
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_poadcast.core.archive import ArchiveManager


class TestArchiveManagerInitialization:
    """测试ArchiveManager初始化"""

    def test_initialization_creates_directory(self):
        """测试初始化时创建目录"""
        with TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir) / "test_archive"
            manager = ArchiveManager(archive_dir)

            assert archive_dir.exists()
            assert archive_dir.is_dir()
            assert manager.archive_dir == archive_dir

    def test_initialization_with_existing_directory(self):
        """测试使用已存在的目录初始化"""
        with TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir) / "existing_archive"
            archive_dir.mkdir()

            manager = ArchiveManager(archive_dir)
            assert manager.archive_dir == archive_dir


class TestSaveArticle:
    """测试保存文章功能"""

    def test_save_article_basic(self):
        """测试基本文章保存"""
        with TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir) / "archive"
            manager = ArchiveManager(archive_dir)

            slug = "test-article"
            archive_date = date(2025, 1, 15)
            metadata = {
                "title": "Test Article",
                "url": "https://example.com/test",
                "source": "Test Source"
            }
            content = "This is the article content."

            md_path, html_path = manager.save_article(
                slug=slug,
                archive_date=archive_date,
                metadata=metadata,
                content=content
            )

            # 验证文件创建
            assert md_path.exists()
            assert html_path is None  # 没有提供HTML

            # 验证路径结构
            expected_path = archive_dir / "2025-01-15" / "test-article.md"
            assert md_path == expected_path

    def test_save_article_with_html(self):
        """测试保存包含HTML的文章"""
        with TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir) / "archive"
            manager = ArchiveManager(archive_dir)

            slug = "article-with-html"
            archive_date = date(2025, 1, 15)
            metadata = {"title": "Test"}
            content = "Content"
            html = "<html><body>HTML Content</body></html>"

            md_path, html_path = manager.save_article(
                slug=slug,
                archive_date=archive_date,
                metadata=metadata,
                content=content,
                html=html
            )

            # 验证两个文件都创建了
            assert md_path.exists()
            assert html_path is not None
            assert html_path.exists()

            # 验证HTML内容
            saved_html = html_path.read_text(encoding='utf-8')
            assert saved_html == html

    def test_save_article_metadata_format(self):
        """测试元数据格式"""
        with TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir) / "archive"
            manager = ArchiveManager(archive_dir)

            metadata = {
                "title": "文章标题",
                "url": "https://example.com",
                "tags": ["教育", "国际"],
                "priority": 9
            }
            content = "文章内容"

            md_path, _ = manager.save_article(
                slug="test",
                archive_date=date.today(),
                metadata=metadata,
                content=content
            )

            # 读取并验证文件格式
            saved_content = md_path.read_text(encoding='utf-8')

            # 应该包含YAML前置内容
            assert saved_content.startswith("---\n")
            assert "文章标题" in saved_content
            assert "文章内容" in saved_content

            # 验证JSON格式
            lines = saved_content.split('\n')
            assert lines[0] == "---"
            # 找到第二个 ---
            second_marker = lines.index("---", 1)
            json_content = '\n'.join(lines[1:second_marker])
            parsed_meta = json.loads(json_content)

            assert parsed_meta['title'] == "文章标题"
            assert parsed_meta['url'] == "https://example.com"
            assert parsed_meta['priority'] == 9

    def test_save_article_filters_empty_metadata(self):
        """测试过滤空元数据"""
        with TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir) / "archive"
            manager = ArchiveManager(archive_dir)

            metadata = {
                "title": "Test",
                "url": "https://example.com",
                "tags": [],  # 空列表应该被过滤
                "description": None,  # None应该被过滤
                "content": ""  # 空字符串应该被过滤
            }

            md_path, _ = manager.save_article(
                slug="test",
                archive_date=date.today(),
                metadata=metadata,
                content="Content"
            )

            saved_content = md_path.read_text(encoding='utf-8')
            # 提取JSON部分
            lines = saved_content.split('\n')
            second_marker = lines.index("---", 1)
            json_content = '\n'.join(lines[1:second_marker])
            parsed_meta = json.loads(json_content)

            # 空值不应该出现在保存的元数据中
            assert 'tags' not in parsed_meta
            assert 'description' not in parsed_meta
            assert 'content' not in parsed_meta
            assert 'title' in parsed_meta
            assert 'url' in parsed_meta

    def test_save_article_creates_date_subdirectory(self):
        """测试为每个日期创建子目录"""
        with TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir) / "archive"
            manager = ArchiveManager(archive_dir)

            dates = [
                date(2025, 1, 15),
                date(2025, 1, 16),
                date(2025, 2, 1)
            ]

            for d in dates:
                manager.save_article(
                    slug=f"article-{d}",
                    archive_date=d,
                    metadata={"title": f"Article {d}"},
                    content="Content"
                )

            # 验证目录结构
            for d in dates:
                date_dir = archive_dir / d.isoformat()
                assert date_dir.exists()
                assert date_dir.is_dir()

    def test_save_multiple_articles_same_date(self):
        """测试同一天保存多篇文章"""
        with TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir) / "archive"
            manager = ArchiveManager(archive_dir)

            archive_date = date(2025, 1, 15)

            articles = [
                ("article-1", "Article 1", "Content 1"),
                ("article-2", "Article 2", "Content 2"),
                ("article-3", "Article 3", "Content 3"),
            ]

            paths = []
            for slug, title, content in articles:
                md_path, _ = manager.save_article(
                    slug=slug,
                    archive_date=archive_date,
                    metadata={"title": title},
                    content=content
                )
                paths.append(md_path)

            # 验证所有文件都创建了
            for path in paths:
                assert path.exists()

            # 验证它们在同一个目录
            date_dir = archive_dir / "2025-01-15"
            files = list(date_dir.glob("*.md"))
            assert len(files) == 3


class TestArchiveManagerEdgeCases:
    """测试边界情况"""

    def test_save_article_with_special_characters(self):
        """测试包含特殊字符的内容"""
        with TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir) / "archive"
            manager = ArchiveManager(archive_dir)

            metadata = {
                "title": "文章标题 with émojis 🎉",
                "url": "https://example.com/测试"
            }
            content = "内容包含特殊字符：\n\n- 中文\n- Émojis 🚀\n- Symbols: © ® ™"

            md_path, _ = manager.save_article(
                slug="special-chars",
                archive_date=date.today(),
                metadata=metadata,
                content=content
            )

            # 验证能正确读回
            saved_content = md_path.read_text(encoding='utf-8')
            assert "🎉" in saved_content
            assert "🚀" in saved_content
            assert "中文" in saved_content

    def test_save_article_with_very_long_content(self):
        """测试保存大量内容"""
        with TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir) / "archive"
            manager = ArchiveManager(archive_dir)

            # 生成大量内容
            content = "Lorem ipsum " * 10000  # 约120KB

            md_path, _ = manager.save_article(
                slug="long-article",
                archive_date=date.today(),
                metadata={"title": "Long Article"},
                content=content
            )

            assert md_path.exists()
            saved_content = md_path.read_text(encoding='utf-8')
            assert len(saved_content) > 100000

    def test_save_article_overwrites_existing(self):
        """测试覆盖已存在的文章"""
        with TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir) / "archive"
            manager = ArchiveManager(archive_dir)

            slug = "duplicate-article"
            archive_date = date.today()

            # 第一次保存
            manager.save_article(
                slug=slug,
                archive_date=archive_date,
                metadata={"title": "Version 1"},
                content="Content 1"
            )

            # 第二次保存（覆盖）
            md_path, _ = manager.save_article(
                slug=slug,
                archive_date=archive_date,
                metadata={"title": "Version 2"},
                content="Content 2"
            )

            # 验证被覆盖
            saved_content = md_path.read_text(encoding='utf-8')
            assert "Version 2" in saved_content
            assert "Version 1" not in saved_content
            assert "Content 2" in saved_content


class TestArchiveManagerIntegration:
    """集成测试"""

    def test_realistic_workflow(self):
        """测试真实工作流程"""
        with TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir) / "source_archive"
            manager = ArchiveManager(archive_dir)

            # 模拟一天的新闻采集
            today = date(2025, 1, 15)
            articles = [
                {
                    "slug": "uk-visa-policy-change",
                    "metadata": {
                        "title": "UK Announces New Visa Policy",
                        "url": "https://gov.uk/news/visa-policy",
                        "source": "GOV.UK",
                        "tags": ["visa", "uk", "immigration"],
                        "priority": 9
                    },
                    "content": "The UK government announced...",
                    "html": "<article>...</article>"
                },
                {
                    "slug": "us-university-rankings",
                    "metadata": {
                        "title": "New US University Rankings Released",
                        "url": "https://usnews.com/rankings",
                        "source": "US News",
                        "tags": ["rankings", "university", "us"],
                        "priority": 7
                    },
                    "content": "The latest university rankings...",
                    "html": None
                }
            ]

            # 保存所有文章
            saved_files = []
            for article in articles:
                md_path, html_path = manager.save_article(
                    slug=article["slug"],
                    archive_date=today,
                    metadata=article["metadata"],
                    content=article["content"],
                    html=article.get("html")
                )
                saved_files.append((md_path, html_path))

            # 验证档案结构
            date_dir = archive_dir / "2025-01-15"
            assert date_dir.exists()

            md_files = list(date_dir.glob("*.md"))
            assert len(md_files) == 2

            html_files = list(date_dir.glob("*.html"))
            assert len(html_files) == 1  # 只有第一篇有HTML


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
