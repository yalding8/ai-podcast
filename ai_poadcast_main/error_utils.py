#!/usr/bin/env python3
"""统一错误处理和重试工具"""

import json
import logging
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, Union

import requests

logger = logging.getLogger(__name__)

T = TypeVar('T')


def safe_file_read(path: Union[str, Path], default: Any = None, encoding: str = 'utf-8') -> Any:
    """
    安全读取文件，带异常处理
    
    Args:
        path: 文件路径
        default: 读取失败时的默认值
        encoding: 文件编码
        
    Returns:
        文件内容或默认值
    """
    try:
        file_path = Path(path)
        if not file_path.exists():
            logger.warning(f"文件不存在: {path}")
            return default
        
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except PermissionError:
        logger.error(f"无权限读取文件: {path}")
        return default
    except UnicodeDecodeError as e:
        logger.error(f"文件编码错误 {path}: {e}")
        return default
    except Exception as e:
        logger.error(f"读取文件失败 {path}: {e}")
        return default


def safe_json_read(path: Union[str, Path], default: Any = None) -> Any:
    """
    安全读取JSON文件
    
    Args:
        path: JSON文件路径
        default: 读取失败时的默认值
        
    Returns:
        解析后的JSON对象或默认值
    """
    try:
        file_path = Path(path)
        if not file_path.exists():
            logger.warning(f"JSON文件不存在: {path}")
            return default
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败 {path}: {e}")
        return default
    except Exception as e:
        logger.error(f"读取JSON失败 {path}: {e}")
        return default


def safe_file_write(path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """
    安全写入文件
    
    Args:
        path: 文件路径
        content: 文件内容
        encoding: 文件编码
        
    Returns:
        是否成功
    """
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except PermissionError:
        logger.error(f"无权限写入文件: {path}")
        return False
    except OSError as e:
        logger.error(f"写入文件失败 {path}: {e}")
        return False
    except Exception as e:
        logger.error(f"写入文件异常 {path}: {e}")
        return False


def safe_json_write(path: Union[str, Path], data: Any, indent: int = 2) -> bool:
    """
    安全写入JSON文件
    
    Args:
        path: JSON文件路径
        data: 要写入的数据
        indent: 缩进空格数
        
    Returns:
        是否成功
    """
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except TypeError as e:
        logger.error(f"JSON序列化失败 {path}: {e}")
        return False
    except Exception as e:
        logger.error(f"写入JSON失败 {path}: {e}")
        return False


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 延迟倍数
        exceptions: 需要重试的异常类型
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"{func.__name__} 失败 (第{attempt + 1}次)，"
                            f"{current_delay:.1f}秒后重试: {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} 失败，已达最大重试次数 ({max_retries}): {e}"
                        )
            
            return None
        return wrapper
    return decorator


def safe_http_get(
    url: str,
    timeout: int = 30,
    max_retries: int = 3,
    headers: Optional[dict] = None,
    **kwargs
) -> Optional[requests.Response]:
    """
    安全的HTTP GET请求，带重试
    
    Args:
        url: 请求URL
        timeout: 超时时间（秒）
        max_retries: 最大重试次数
        headers: 请求头
        **kwargs: 其他requests参数
        
    Returns:
        Response对象或None
    """
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/120.0.0.0 Safari/537.36'
        }
    
    @retry_on_failure(
        max_retries=max_retries,
        delay=1.0,
        backoff=2.0,
        exceptions=(requests.RequestException,)
    )
    def _request():
        response = requests.get(url, headers=headers, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    
    return _request()


def safe_http_post(
    url: str,
    data: Optional[dict] = None,
    json_data: Optional[dict] = None,
    timeout: int = 30,
    max_retries: int = 3,
    headers: Optional[dict] = None,
    **kwargs
) -> Optional[requests.Response]:
    """
    安全的HTTP POST请求，带重试
    
    Args:
        url: 请求URL
        data: 表单数据
        json_data: JSON数据
        timeout: 超时时间（秒）
        max_retries: 最大重试次数
        headers: 请求头
        **kwargs: 其他requests参数
        
    Returns:
        Response对象或None
    """
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    @retry_on_failure(
        max_retries=max_retries,
        delay=1.0,
        backoff=2.0,
        exceptions=(requests.RequestException,)
    )
    def _request():
        response = requests.post(
            url,
            data=data,
            json=json_data,
            headers=headers,
            timeout=timeout,
            **kwargs
        )
        response.raise_for_status()
        return response
    
    return _request()


class FileOperationError(Exception):
    """文件操作异常"""
    pass


class NetworkError(Exception):
    """网络请求异常"""
    pass
