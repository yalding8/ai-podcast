"""索引管理"""

import json
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse, urlunparse


class IndexManager:
    """管理文章索引"""
    
    def __init__(self, index_path: Path):
        self.index_path = index_path
    
    def load(self) -> List[dict]:
        """加载索引"""
        if not self.index_path.exists():
            return []
        try:
            return json.loads(self.index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    
    def save(self, entries: List[dict]) -> None:
        """保存索引"""
        sorted_entries = sorted(
            entries,
            key=lambda x: x.get("imported_at", ""),
            reverse=True
        )
        self.index_path.write_text(
            json.dumps(sorted_entries, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    def add_entry(self, entry: dict) -> None:
        """添加新条目"""
        entries = self.load()
        entries.append(entry)
        self.save(entries)
    
    def is_duplicate(self, url: str) -> bool:
        """检查URL是否重复"""
        canonical = self._canonicalize_url(url)
        entries = self.load()
        
        for entry in entries:
            existing = entry.get("url_canonical") or entry.get("url")
            if existing and self._canonicalize_url(existing) == canonical:
                return True
        return False
    
    @staticmethod
    def _canonicalize_url(url: str) -> str:
        """标准化URL"""
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip("/") or "/"
        canonical = parsed._replace(netloc=netloc, path=path, fragment="", params="")
        return urlunparse(canonical)
