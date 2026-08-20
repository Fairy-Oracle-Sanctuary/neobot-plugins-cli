"""
消息段模型 —— plugin-api-v1 stub。

与真实契约一致的 MessageSegment 构造器;PlatformMessage/PlatformSegment
为跨平台消息载体占位。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class MessageSegment:
    """表示一个 OneBot v11 消息段。"""

    type: str
    data: Dict[str, Any]

    @property
    def plain_text(self) -> str:
        """当消息段类型为 'text' 时,快速获取其文本内容。"""
        return self.data.get("text", "") if self.type == "text" else ""

    @staticmethod
    def text(text: str) -> "MessageSegment":
        return MessageSegment(type="text", data={"text": text})

    @staticmethod
    def image(file: str) -> "MessageSegment":
        return MessageSegment(type="image", data={"file": file})

    @staticmethod
    def at(qq: str) -> "MessageSegment":
        return MessageSegment(type="at", data={"qq": qq})

    @staticmethod
    def face(id_: int) -> "MessageSegment":
        return MessageSegment(type="face", data={"id": id_})

    @staticmethod
    def reply(id_: int) -> "MessageSegment":
        return MessageSegment(type="reply", data={"id": id_})

    def __str__(self) -> str:
        if self.type == "text":
            return self.data.get("text", "")
        return f"[{self.type}:{self.data}]"


@dataclass
class PlatformSegment:
    """跨平台消息段。"""

    platform: str
    type: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlatformMessage:
    """跨平台消息载体。"""

    platform: str = "qq"
    segments: List[PlatformSegment] = field(default_factory=list)
    raw: str = ""
