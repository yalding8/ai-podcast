"""文本处理工具"""

import re
import unicodedata


def slugify(text: str) -> str:
    """将文本转换为URL友好的slug"""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-").lower()
    return text


def clean_markdown(text: str) -> str:
    """清理Markdown标记"""
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text
