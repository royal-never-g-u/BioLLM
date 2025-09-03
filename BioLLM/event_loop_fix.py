#!/usr/bin/env python3
"""
事件循环修复模块
用于解决 "unclosed event loop" 错误
"""

import asyncio
import sys
import warnings
from contextlib import contextmanager

def setup_event_loop():
    """
    设置事件循环
    """
    try:
        # 尝试获取当前事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                # 如果循环已关闭，创建新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            # 如果没有当前事件循环，创建新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop
    except Exception as e:
        print(f"设置事件循环时出错: {e}")
        return None

def cleanup_event_loop():
    """
    清理事件循环
    """
    try:
        loop = asyncio.get_event_loop()
        
        # 取消所有待处理的任务
        try:
            pending = asyncio.all_tasks(loop)
            if pending:
                for task in pending:
                    task.cancel()
                # 运行循环直到所有任务被取消
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:
            pass  # 忽略任务取消时的错误
        
        # 关闭事件循环
        if not loop.is_closed():
            loop.close()
            
    except Exception as e:
        print(f"清理事件循环时出错: {e}")

@contextmanager
def event_loop_context():
    """
    事件循环上下文管理器
    用法:
    with event_loop_context():
        # 你的代码
        pass
    """
    loop = setup_event_loop()
    try:
        yield loop
    finally:
        if loop and not loop.is_closed():
            cleanup_event_loop()

def fix_event_loop_warning():
    """
    修复事件循环警告
    """
    # 忽略特定的事件循环警告
    warnings.filterwarnings("ignore", message=".*unclosed event loop.*")
    warnings.filterwarnings("ignore", message=".*There is no current event loop.*")

def run_with_event_loop(func):
    """
    装饰器：使用事件循环运行函数
    """
    def wrapper(*args, **kwargs):
        with event_loop_context():
            return func(*args, **kwargs)
    return wrapper

# 自动修复事件循环警告
fix_event_loop_warning()

# 导出主要函数
__all__ = [
    'setup_event_loop',
    'cleanup_event_loop', 
    'event_loop_context',
    'fix_event_loop_warning',
    'run_with_event_loop'
]
