#!/usr/bin/env python3
"""安全路径处理工具"""

from pathlib import Path
from typing import Union


def safe_path(path: Union[str, Path], base_dir: Union[str, Path]) -> Path:
    """
    安全地解析路径，防止目录遍历攻击
    
    Args:
        path: 要验证的路径
        base_dir: 允许的基础目录
        
    Returns:
        解析后的安全路径
        
    Raises:
        ValueError: 如果路径试图逃逸基础目录
    """
    base = Path(base_dir).resolve()
    target = Path(path).resolve()
    
    try:
        target.relative_to(base)
    except ValueError:
        raise ValueError(f"路径 {path} 不在允许的目录 {base_dir} 内")
    
    return target
