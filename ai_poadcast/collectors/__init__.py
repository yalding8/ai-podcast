"""新闻采集模块"""

from .rss import RSSCollector
from .web import WebFetcher

__all__ = ["RSSCollector", "WebFetcher"]
