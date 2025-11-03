"""日期处理工具"""

from datetime import date, datetime
from typing import Optional


def parse_date(value: Optional[str]) -> Optional[date]:
    """解析日期字符串"""
    if not value:
        return None
    
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    
    return None
