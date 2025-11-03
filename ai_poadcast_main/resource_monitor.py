#!/usr/bin/env python3
"""资源使用监控工具（可选）"""

import atexit
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil 未安装，资源监控功能受限")


class ResourceMonitor:
    """资源使用监控器"""
    
    def __init__(self, enable_exit_check: bool = True):
        """
        初始化资源监控器
        
        Args:
            enable_exit_check: 是否在程序退出时检查资源
        """
        self.pid = os.getpid()
        self.process = None
        
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process(self.pid)
            if enable_exit_check:
                atexit.register(self.log_on_exit)
    
    def get_open_files_count(self) -> Optional[int]:
        """获取打开的文件数"""
        if not self.process:
            return None
        try:
            return len(self.process.open_files())
        except Exception as e:
            logger.error(f"获取文件句柄数失败: {e}")
            return None
    
    def get_memory_usage(self) -> Optional[float]:
        """获取内存使用（MB）"""
        if not self.process:
            return None
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except Exception as e:
            logger.error(f"获取内存使用失败: {e}")
            return None
    
    def get_connections_count(self) -> Optional[int]:
        """获取网络连接数"""
        if not self.process:
            return None
        try:
            return len(self.process.connections())
        except Exception as e:
            logger.error(f"获取连接数失败: {e}")
            return None
    
    def check_file_handles(self, threshold: float = 0.8) -> bool:
        """
        检查文件句柄使用率
        
        Args:
            threshold: 警告阈值（0-1）
            
        Returns:
            是否超过阈值
        """
        if not self.process:
            return False
        
        try:
            import resource
            soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            current = self.get_open_files_count() or 0
            
            usage_rate = current / soft
            if usage_rate > threshold:
                logger.warning(
                    f"文件句柄使用率过高: {current}/{soft} ({usage_rate:.1%})"
                )
                return True
            return False
        except Exception as e:
            logger.error(f"检查文件句柄失败: {e}")
            return False
    
    def log_resource_status(self):
        """记录当前资源使用状态"""
        if not self.process:
            logger.info("资源监控不可用（需要安装 psutil）")
            return
        
        files = self.get_open_files_count()
        memory = self.get_memory_usage()
        connections = self.get_connections_count()
        
        logger.info(
            f"资源使用状态 - "
            f"文件: {files}, "
            f"内存: {memory:.2f}MB, "
            f"连接: {connections}"
        )
    
    def log_on_exit(self):
        """程序退出时记录资源状态"""
        files = self.get_open_files_count()
        if files and files > 10:
            logger.warning(f"程序退出时仍有 {files} 个文件打开")
        else:
            logger.info(f"程序正常退出，打开文件数: {files}")


def cleanup_temp_files(temp_dirs: Optional[list] = None):
    """
    清理临时文件
    
    Args:
        temp_dirs: 临时目录列表
    """
    if temp_dirs is None:
        temp_dirs = [
            'audio_parts/temp',
            'script_chunks/temp',
        ]
    
    cleaned = 0
    for temp_dir in temp_dirs:
        path = Path(temp_dir)
        if path.exists():
            for file in path.glob('*'):
                if file.is_file():
                    try:
                        file.unlink()
                        cleaned += 1
                    except Exception as e:
                        logger.error(f"删除临时文件失败 {file}: {e}")
    
    if cleaned > 0:
        logger.info(f"已清理 {cleaned} 个临时文件")


# 全局监控器实例（可选使用）
_monitor = None


def get_monitor() -> ResourceMonitor:
    """获取全局监控器实例"""
    global _monitor
    if _monitor is None:
        _monitor = ResourceMonitor()
    return _monitor


if __name__ == "__main__":
    # 测试监控功能
    logging.basicConfig(level=logging.INFO)
    
    monitor = ResourceMonitor()
    
    print("📊 资源使用监控测试\n")
    
    if PSUTIL_AVAILABLE:
        print(f"打开的文件数: {monitor.get_open_files_count()}")
        print(f"内存使用: {monitor.get_memory_usage():.2f} MB")
        print(f"网络连接数: {monitor.get_connections_count()}")
        print(f"\n文件句柄检查: {'⚠️ 超过阈值' if monitor.check_file_handles() else '✅ 正常'}")
        
        print("\n完整状态:")
        monitor.log_resource_status()
    else:
        print("⚠️ 需要安装 psutil 才能使用监控功能")
        print("安装命令: pip install psutil")
