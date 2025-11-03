"""网页内容抓取"""

import re
import urllib.request
from html import unescape
from typing import Optional, Tuple


class WebFetcher:
    """网页内容抓取器"""
    
    def __init__(self, user_agent: Optional[str] = None):
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36"
        )
    
    def fetch(self, url: str, timeout: int = 30) -> Tuple[str, str]:
        """抓取URL内容，返回(文本, HTML)"""
        request = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            raw_html = response.read().decode(charset, errors="replace")
        
        text = self._extract_text(raw_html)
        return text, raw_html
    
    def _extract_text(self, html: str) -> str:
        """从HTML提取可读文本"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "noscript", "header", "footer", "aside", "nav"]):
                tag.decompose()
            
            selectors = [
                "div.single-content", "div.post-content", "div.article-content",
                "div.entry-content", "section.article__body", "article", "main"
            ]
            
            article = None
            for selector in selectors:
                article = soup.select_one(selector)
                if article and article.get_text(strip=True):
                    break
            
            if not article:
                article = soup.body or soup
            
            text = article.get_text("\n", strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return "\n".join(lines)
            
        except ModuleNotFoundError:
            cleaned = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", "", html)
            cleaned = re.sub(r"(?s)<[^>]+>", "\n", cleaned)
            cleaned = unescape(cleaned)
            lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
            return "\n".join(lines)
