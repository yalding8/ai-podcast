"""内容校验器"""

import re


class ContentValidator:
    """内容质量校验"""
    
    @staticmethod
    def count_words(text: str) -> int:
        """统计词数"""
        return len(re.findall(r"\b\w+\b", text))
    
    @staticmethod
    def is_too_short(text: str, min_words: int = 80) -> bool:
        """检查文本是否过短"""
        return ContentValidator.count_words(text) < min_words
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """验证URL格式"""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
        except ValueError:
            return False
