"""
注册装饰器与模拟对象 —— plugin-api-v1 stub 核心。

装饰器将命令/事件处理器注册到内存 registry,供 CLI REPL 触发。
模拟 MessageEvent 的 reply() 把回复收集到列表,便于测试断言。
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

# ── 注册表 ──────────────────────────────────────────────────────

# 命令注册表: 命令名 -> (handler, kwargs)
_COMMANDS: Dict[str, Callable] = {}
_COMMAND_META: Dict[str, Dict[str, Any]] = {}
# 平台感知命令: (platform, 命令名) -> handler
_PLATFORM_COMMANDS: Dict[tuple, Callable] = {}
# 消息/事件处理器
_MESSAGE_HANDLERS: List[Callable] = []
_PLATFORM_MESSAGE_HANDLERS: Dict[str, List[Callable]] = {}
_NOTICE_HANDLERS: List[Callable] = []
_REQUEST_HANDLERS: List[Callable] = []

# 模拟回复收集: 最近一次触发的回复列表
last_replies: List[Any] = []


def _is_async(func: Callable) -> bool:
    return inspect.iscoroutinefunction(func)


def _run(handler: Callable, *args, **kwargs) -> Any:
    """同步/异步统一调用。"""
    result = handler(*args, **kwargs)
    if inspect.isawaitable(result):
        import asyncio
        from typing import cast

        coro = cast("Any", result)
        return asyncio.run(coro)
    return result


# ── 装饰器 ──────────────────────────────────────────────────────


def command(
    *names: str,
    permission: Optional[Any] = None,
    override_permission_check: bool = False,
) -> Callable:
    """注册消息指令。``/指令名`` 触发。"""

    def decorator(func: Callable) -> Callable:
        for name in names:
            _COMMANDS[name] = func
            _COMMAND_META[name] = {
                "permission": permission,
                "override_permission_check": override_permission_check,
                "handler": func,
            }
        return func

    return decorator


def platform_command(
    platforms,
    *names: str,
    permission: Optional[Any] = None,
    override_permission_check: bool = False,
) -> Callable:
    """注册平台感知指令(仅对指定平台生效)。"""

    def decorator(func: Callable) -> Callable:
        for name in names:
            for p in platforms:
                _PLATFORM_COMMANDS[(p, name)] = func
            _COMMAND_META[name] = {
                "permission": permission,
                "override_permission_check": override_permission_check,
                "handler": func,
                "platforms": list(platforms),
            }
        return func

    return decorator


def on_message(**kwargs) -> Callable:
    """注册通用消息处理器。"""

    def decorator(func: Callable) -> Callable:
        _MESSAGE_HANDLERS.append(func)
        return func

    return decorator


def platform_message(platforms, **kwargs) -> Callable:
    """注册平台感知的通用消息处理器。"""

    def decorator(func: Callable) -> Callable:
        for p in platforms:
            _PLATFORM_MESSAGE_HANDLERS.setdefault(p, []).append(func)
        return func

    return decorator


def on_notice(notice_type: Optional[str] = None) -> Callable:
    """注册通知事件处理器。"""

    def decorator(func: Callable) -> Callable:
        _NOTICE_HANDLERS.append(func)
        return func

    return decorator


def on_request(request_type: Optional[str] = None) -> Callable:
    """注册请求事件处理器。"""

    def decorator(func: Callable) -> Callable:
        _REQUEST_HANDLERS.append(func)
        return func

    return decorator


# ── 查询接口(CLI 使用) ──────────────────────────────────────────


def list_commands() -> List[str]:
    """列出所有注册的指令名。"""
    names = set(_COMMANDS.keys())
    names.update(name for _, name in _PLATFORM_COMMANDS.keys())
    return sorted(names)


def resolve_command(name: str, platform: str = "qq") -> Optional[Callable]:
    """按平台优先查找指令处理器。"""
    handler = _PLATFORM_COMMANDS.get((platform, name))
    if handler:
        return handler
    return _COMMANDS.get(name)


# ── 模拟对象 ────────────────────────────────────────────────────


class Platform:
    """平台名常量(与真实框架一致)。"""

    QQ = "qq"
    DISCORD = "discord"
    CLI = "cli"
    MCC = "mcc"


@dataclass
class Bot:
    """模拟 Bot 对象:记录 call_api 调用。"""

    self_id: str = "lab-bot"
    api_calls: List[Dict[str, Any]] = field(default_factory=list)

    async def call_api(self, action: str, **params) -> Dict[str, Any]:
        """记录 API 调用,返回空结果。"""
        self.api_calls.append({"action": action, "params": params})
        return {"status": "ok", "action": action}

    async def send_like(self, user_id: str, times: int = 1) -> Dict[str, Any]:
        """模拟点赞:记录调用。"""
        return await self.call_api("send_like", user_id=user_id, times=times)

    async def send_group_msg(self, group_id: str, message: Any) -> Dict[str, Any]:
        """模拟发群消息:记录调用,并把文本也收集到回复。"""
        self.api_calls.append({"action": "send_group_msg", "group_id": group_id, "message": message})
        return {"status": "ok", "message_id": 9998}

    async def send_private_msg(self, user_id: str, message: Any) -> Dict[str, Any]:
        """模拟发私聊消息。"""
        self.api_calls.append({"action": "send_private_msg", "user_id": user_id, "message": message})
        return {"status": "ok", "message_id": 9997}

    def build_forward_node(self, user_id: str, nickname: str, message: Any) -> Dict[str, Any]:
        return {"type": "node", "user_id": user_id, "nickname": nickname, "message": message}


@dataclass
class MessageEvent:
    """模拟消息事件。reply() 收集到全局 last_replies。"""

    bot: Bot = field(default_factory=Bot)
    message_id: int = 1
    user_id: str = "10001"
    group_id: Optional[str] = None
    raw_message: str = ""
    message: Any = None
    message_type: str = "group"
    self_id: str = "lab-bot"
    platform: str = Platform.QQ

    async def reply(self, message: Union[str, Any]):
        """收集回复到 last_replies。"""
        global last_replies
        if isinstance(message, list):
            parts = [seg.plain_text if hasattr(seg, "plain_text") else str(seg) for seg in message]
            text = " ".join(p for p in parts if p)
        else:
            text = str(message)
        last_replies.append(text)
        return {"status": "ok", "message_id": 9999}


# ── 触发接口(CLI 使用) ──────────────────────────────────────────


def trigger_command(
    name: str,
    args: List[str],
    platform: str = Platform.QQ,
    group_id: Optional[str] = "10000",
    user_id: str = "10001",
) -> List[str]:
    """触发一条指令,返回收集到的回复列表。"""
    global last_replies
    last_replies = []
    handler = resolve_command(name, platform)
    if handler is None:
        last_replies.append(f"[未注册] 指令 /{name} 不存在")
        return last_replies

    meta = _COMMAND_META.get(name, {})
    event = MessageEvent(
        platform=platform,
        group_id=group_id,
        user_id=user_id,
        raw_message="/" + name + (" " + " ".join(args) if args else ""),
        message=[__import__("neobot.plugin_api", fromlist=["MessageSegment"]).MessageSegment.text(
            " ".join(args)
        )],
    )

    kwargs = {"bot": event.bot, "event": event}
    if meta.get("override_permission_check"):
        # 测试环境权限全部放行
        kwargs["permission_granted"] = True

    # 按 handler 签名传参:兼容 (bot, event, args) / (bot, event, permission_granted)
    # / (bot, event) / (event, args) 等常见形态
    import inspect as _inspect

    sig = _inspect.signature(handler)
    param_names = list(sig.parameters.keys())

    if "args" in param_names:
        kwargs["args"] = args

    try:
        _run(handler, **kwargs)
    except TypeError:
        # 兜底: (event, args) 签名
        _run(handler, event, args)
    return last_replies


def trigger_message(text: str, platform: str = Platform.QQ) -> List[str]:
    """触发一条普通消息处理器(on_message),返回收集到的回复。"""
    global last_replies
    last_replies = []
    event = MessageEvent(
        platform=platform,
        raw_message=text,
        message=[__import__("neobot.plugin_api", fromlist=["MessageSegment"]).MessageSegment.text(text)],
    )
    for handler in _MESSAGE_HANDLERS:
        _run(handler, event)
    for handler in _PLATFORM_MESSAGE_HANDLERS.get(platform, []):
        _run(handler, event)
    return last_replies


def reset_registry() -> None:
    """清空注册表(测试隔离用)。"""
    _COMMANDS.clear()
    _COMMAND_META.clear()
    _PLATFORM_COMMANDS.clear()
    _MESSAGE_HANDLERS.clear()
    _PLATFORM_MESSAGE_HANDLERS.clear()
    _NOTICE_HANDLERS.clear()
    _REQUEST_HANDLERS.clear()
    global last_replies
    last_replies = []
