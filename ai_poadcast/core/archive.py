"""原文档案管理"""

import json
from datetime import date
from pathlib import Path
from typing import Optional


class ArchiveManager:
    """管理原文档案的存储和检索"""
    
    def __init__(self, archive_dir: Path):
        self.archive_dir = archive_dir
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def save_article(
        self,
        slug: str,
        archive_date: date,
        metadata: dict,
        content: str,
        html: Optional[str] = None
    ) -> tuple[Path, Optional[Path]]:
        """保存文章到档案"""
        date_dir = self.archive_dir / archive_date.isoformat()
        date_dir.mkdir(parents=True, exist_ok=True)
        
        md_path = date_dir / f"{slug}.md"
        self._write_markdown(md_path, metadata, content)
        
        html_path = None
        if html:
            html_path = date_dir / f"{slug}.html"
            html_path.write_text(html, encoding="utf-8")
        
        return md_path, html_path
    
    def _write_markdown(self, path: Path, metadata: dict, content: str) -> None:
        """写入带元数据的Markdown文件"""
        clean_meta = {k: v for k, v in metadata.items() if v not in (None, [], "")}
        lines = [
            "---",
            json.dumps(clean_meta, ensure_ascii=False, indent=2),
            "---",
            "",
            content,
            ""
        ]
        path.write_text("\n".join(lines), encoding="utf-8")
