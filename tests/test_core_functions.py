#!/usr/bin/env python3
"""核心函数单元测试"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_poadcast_main.collect_rss_feeds import normalize_url, deduplicate_by_title, similar


class TestURLNormalization:
    def test_normalize_url_removes_query_params(self):
        url = "https://example.com/news?utm_source=rss&id=123"
        result = normalize_url(url)
        assert result == "https://example.com/news"
    
    def test_normalize_url_preserves_path(self):
        url = "https://example.com/news/article/2025"
        result = normalize_url(url)
        assert result == "https://example.com/news/article/2025"


class TestTitleSimilarity:
    def test_similar_identical_titles(self):
        result = similar("Breaking News", "Breaking News")
        assert result == 1.0
    
    def test_similar_case_insensitive(self):
        result = similar("Breaking News", "breaking news")
        assert result == 1.0


class TestDeduplication:
    def test_deduplicate_removes_similar_titles(self):
        items = [
            {"title": "UK announces new visa policy", "url": "url1"},
            {"title": "UK announces new visa policy changes", "url": "url2"},
            {"title": "Completely different news", "url": "url3"}
        ]
        result = deduplicate_by_title(items, threshold=0.85)
        assert len(result) == 2
    
    def test_deduplicate_empty_list(self):
        result = deduplicate_by_title([])
        assert result == []


class TestConfiguration:
    def test_config_imports(self):
        import config
        assert hasattr(config, 'RSS_SOURCES')
        assert hasattr(config, 'PRIORITY_KEYWORDS')
    
    def test_config_rss_sources_structure(self):
        import config
        for name, source in config.RSS_SOURCES.items():
            assert 'rss' in source or 'url' in source
            assert 'priority' in source
            assert isinstance(source['priority'], int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
