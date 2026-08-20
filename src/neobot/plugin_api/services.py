"""
框架服务 —— plugin-api-v1 stub。

全部为内存占位实现,供原型测试时 import 不报错:
- redis_manager: 内存 dict 读写;
- permission_manager: 全部放行(测试环境无权限墙);
- 其余工具为降级实现。
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any, Callable, Dict, Optional


class _MemoryRedis:
    """内存版 Redis:dict 读写,支持 get/set/delete。"""

    def __init__(self) -> None:
        self._data: Dict[str, str] = {}
        self._lock = threading.Lock()

    async def get(self, key: str) -> Optional[str]:
        with self._lock:
            return self._data.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        with self._lock:
            self._data[key] = value
        return True

    async def delete(self, *keys: str) -> int:
        with self._lock:
            n = sum(1 for k in keys if self._data.pop(k, None) is not None)
        return n


redis_manager = _MemoryRedis()


class _MemoryImageManager:
    """占位 image_manager:记录调用,不渲染。"""

    async def render_template_to_base64(self, template_name: str, data: dict, **kwargs) -> str:
        return f"data:image/png;base64,{template_name}_placeholder"


image_manager = _MemoryImageManager()


class _MemoryBotManager:
    """占位 bot_manager:保存一个模拟 Bot。"""

    def __init__(self) -> None:
        self.bots: Dict[str, Any] = {}

    def register(self, bot: Any) -> None:
        self.bots[bot.self_id] = bot


bot_manager = _MemoryBotManager()


class _MemoryPermissionManager:
    """占位 permission_manager:测试环境全部放行。"""

    async def is_admin(self, user_id: str) -> bool:
        return True

    async def is_op(self, user_id: str) -> bool:
        return True


permission_manager = _MemoryPermissionManager()


def require_admin(func: Callable) -> Callable:
    """占位 require_admin 装饰器:不拦截。"""
    return func


class _MemoryMessageBus:
    """占位 message_bus。"""

    async def publish(self, *args, **kwargs) -> None:
        pass

    async def subscribe(self, *args, **kwargs) -> None:
        pass


message_bus = _MemoryMessageBus()


async def download_to_local(url: str, **kwargs) -> Optional[str]:
    """占位:返回 None(原型测试不真正下载)。"""
    return None


def get_local_file_server() -> None:
    """占位:返回 None。"""
    return None


def run_in_thread_pool(func: Callable, *args, **kwargs) -> Any:
    """同步阻塞函数放入线程池执行。"""
    return asyncio.get_event_loop().run_in_executor(None, lambda: func(*args, **kwargs))


class InputValidator:
    """占位输入校验器。"""

    def sanitize(self, text: str) -> str:
        return text


input_validator = InputValidator()


class _MemoryConfig:
    """占位 global_config:原型测试中所有配置项返回空/False。"""

    def __getattr__(self, name: str) -> Any:
        return _MemoryConfig()


global_config = _MemoryConfig()
