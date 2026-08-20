"""
neobot.plugin_api —— 插件 API 契约 (plugin-api-v1) 轻量 stub。

仅供 neobot-plugins-cli 原型测试使用：插件在无真实 NeoBot 框架
（无 Redis/MySQL/NapCat）的环境下也能 import 并注册命令/事件处理器。

与真实契约的差异：
- 装饰器只做注册,不连接任何后端;
- 命令触发时构造模拟 MessageEvent,回复收集到 reply 列表;
- 服务单例（redis_manager 等）为内存占位,不落盘。
"""

from __future__ import annotations

from neobot.plugin_api.events import (
    EventType,
    FriendAddNoticeEvent,
    FriendRecallNoticeEvent,
    GroupAdminNoticeEvent,
    GroupBanNoticeEvent,
    GroupCardNoticeEvent,
    GroupDecreaseNoticeEvent,
    GroupIncreaseNoticeEvent,
    GroupMessageEvent,
    GroupNoticeEvent,
    GroupRecallNoticeEvent,
    GroupUploadNoticeEvent,
    HeartbeatEvent,
    LifeCycleEvent,
    MessageEvent,
    MetaEvent,
    NoticeEvent,
    NotifyNoticeEvent,
    OneBotEvent,
    PokeNotifyEvent,
    PrivateMessageEvent,
    RequestEvent,
)
from neobot.plugin_api.logger import ModuleLogger, logger
from neobot.plugin_api.manifest import (
    API_VERSION,
    PluginManifest,
    PluginManifestError,
    define_plugin,
)
from neobot.plugin_api.message import MessageSegment, PlatformMessage, PlatformSegment
from neobot.plugin_api.permission import Permission
from neobot.plugin_api.registry import (
    Bot,
    Platform,
    command,
    on_message,
    on_notice,
    on_request,
    platform_command,
    platform_message,
)
from neobot.plugin_api.services import (
    bot_manager,
    download_to_local,
    get_local_file_server,
    global_config,
    image_manager,
    input_validator,
    message_bus,
    permission_manager,
    redis_manager,
    require_admin,
    run_in_thread_pool,
)

__version__ = "0.2.0"

__all__ = [
    "API_VERSION",
    "__version__",
    # manifest
    "PluginManifest",
    "PluginManifestError",
    "define_plugin",
    # 注册装饰器
    "command",
    "platform_command",
    "on_message",
    "platform_message",
    "on_notice",
    "on_request",
    # 模型与消息
    "MessageSegment",
    "PlatformMessage",
    "PlatformSegment",
    "Bot",
    "Permission",
    "Platform",
    # 服务(内存占位)
    "redis_manager",
    "image_manager",
    "bot_manager",
    "permission_manager",
    "require_admin",
    "message_bus",
    "download_to_local",
    "get_local_file_server",
    "run_in_thread_pool",
    "input_validator",
    "global_config",
    # 配置 / 日志
    "logger",
    "ModuleLogger",
    # 事件模型
    "EventType",
    "OneBotEvent",
    "MessageEvent",
    "PrivateMessageEvent",
    "GroupMessageEvent",
    "MetaEvent",
    "HeartbeatEvent",
    "LifeCycleEvent",
    "NoticeEvent",
    "FriendAddNoticeEvent",
    "FriendRecallNoticeEvent",
    "GroupNoticeEvent",
    "GroupRecallNoticeEvent",
    "GroupIncreaseNoticeEvent",
    "GroupDecreaseNoticeEvent",
    "GroupAdminNoticeEvent",
    "GroupBanNoticeEvent",
    "GroupUploadNoticeEvent",
    "NotifyNoticeEvent",
    "PokeNotifyEvent",
    "GroupCardNoticeEvent",
    "RequestEvent",
]
