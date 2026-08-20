"""
事件模型 —— plugin-api-v1 stub。

所有事件继承 OneBotEvent 基类。CLI 触发命令时使用 MessageEvent;
其余事件类为占位(满足插件类型注解与 isinstance 检查)。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from neobot.plugin_api.permission import Permission  # noqa: F401
from neobot.plugin_api.registry import Bot, MessageEvent, Platform  # noqa: F401


class EventType:
    """事件类型常量。"""

    MESSAGE = "message"
    NOTICE = "notice"
    REQUEST = "request"
    META = "meta"


@dataclass
class OneBotEvent:
    """所有事件的基类。"""

    post_type: str = "message"
    self_id: str = "lab-bot"
    time: int = 0


# ── 消息事件 ────────────────────────────────────────────────────


@dataclass
class PrivateMessageEvent(MessageEvent):
    """私聊消息事件。"""

    message_type: str = "private"
    user_id: str = "10001"


@dataclass
class GroupMessageEvent(MessageEvent):
    """群消息事件。"""

    message_type: str = "group"
    group_id: Optional[str] = "10000"
    user_id: str = "10001"


# ── 元事件 ──────────────────────────────────────────────────────


@dataclass
class MetaEvent(OneBotEvent):
    """元事件基类。"""

    post_type: str = "meta_event"


@dataclass
class HeartbeatEvent(MetaEvent):
    """心跳事件。"""

    meta_event_type: str = "heartbeat"
    status: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LifeCycleEvent(MetaEvent):
    """生命周期事件。"""

    meta_event_type: str = "lifecycle"
    sub_type: str = "connect"


class LifeCycleSubType:
    CONNECT = "connect"
    ENABLE = "enable"
    DISABLE = "disable"


# ── 通知事件 ────────────────────────────────────────────────────


@dataclass
class NoticeEvent(OneBotEvent):
    """通知事件基类。"""

    post_type: str = "notice"
    notice_type: str = ""


@dataclass
class FriendAddNoticeEvent(NoticeEvent):
    """好友添加通知。"""

    notice_type: str = "friend_add"
    user_id: str = "10001"


@dataclass
class FriendRecallNoticeEvent(NoticeEvent):
    """好友消息撤回通知。"""

    notice_type: str = "friend_recall"
    user_id: str = "10001"
    message_id: int = 0


@dataclass
class GroupNoticeEvent(NoticeEvent):
    """群通知基类。"""

    group_id: str = "10000"
    user_id: str = "10001"


@dataclass
class GroupRecallNoticeEvent(GroupNoticeEvent):
    """群消息撤回通知。"""

    notice_type: str = "group_recall"
    operator_id: str = "10001"
    message_id: int = 0


@dataclass
class GroupIncreaseNoticeEvent(GroupNoticeEvent):
    """群成员增加通知。"""

    notice_type: str = "group_increase"
    sub_type: str = "approve"


@dataclass
class GroupDecreaseNoticeEvent(GroupNoticeEvent):
    """群成员减少通知。"""

    notice_type: str = "group_decrease"
    sub_type: str = "leave"


@dataclass
class GroupAdminNoticeEvent(GroupNoticeEvent):
    """群管理员变动通知。"""

    notice_type: str = "group_admin"
    sub_type: str = "set"


@dataclass
class GroupBanNoticeEvent(GroupNoticeEvent):
    """群禁言通知。"""

    notice_type: str = "group_ban"
    sub_type: str = "ban"
    duration: int = 0


@dataclass
class GroupUploadNoticeEvent(GroupNoticeEvent):
    """群文件上传通知。"""

    notice_type: str = "group_upload"
    file: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotifyNoticeEvent(GroupNoticeEvent):
    """群内提醒通知。"""

    notice_type: str = "notify"
    sub_type: str = "poke"


@dataclass
class PokeNotifyEvent(NotifyNoticeEvent):
    """戳一戳通知。"""

    sub_type: str = "poke"
    target_id: str = "10001"


@dataclass
class GroupCardNoticeEvent(GroupNoticeEvent):
    """群名片变更通知。"""

    notice_type: str = "group_card"
    card_new: str = ""
    card_old: str = ""


# ── 请求事件 ────────────────────────────────────────────────────


@dataclass
class RequestEvent(OneBotEvent):
    """请求事件基类。"""

    post_type: str = "request"
    request_type: str = ""
    user_id: str = "10001"
    comment: str = ""


@dataclass
class FriendRequestEvent(RequestEvent):
    """好友请求。"""

    request_type: str = "friend"
    flag: str = ""


@dataclass
class GroupRequestEvent(RequestEvent):
    """群请求。"""

    request_type: str = "group"
    group_id: str = "10000"
    sub_type: str = "add"
    flag: str = ""
