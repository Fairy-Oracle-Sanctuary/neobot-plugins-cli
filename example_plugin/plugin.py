# -*- coding: utf-8 -*-
"""
示例插件 —— 供 neobot-lab 测试。

展示契约写法的三种注册方式:模块级 command、platform_command、
on_message 消息处理器。
"""
from neobot.plugin_api import (
    Bot,
    MessageEvent,
    ModuleLogger,
    command,
    define_plugin,
    on_message,
    platform_command,
)

logger = ModuleLogger("Example")

plugin_manifest = define_plugin(
    name="example",
    description="示例插件(neobot-lab 测试用)",
    usage="/ping - 回复 pong\n/hello <名字> - 打招呼",
    version="0.1.0",
    author="镀铬酸钾",
)


@command("ping")
async def handle_ping(bot: Bot, event: MessageEvent, args: list[str]):
    """/ping 回复 pong。"""
    await event.reply("pong")


@command("hello")
async def handle_hello(bot: Bot, event: MessageEvent, args: list[str]):
    """/hello <名字> 打招呼。"""
    name = " ".join(args) if args else "世界"
    await event.reply(f"你好, {name}!")


@platform_command(["qq", "discord"], "赞")
async def handle_like(bot: Bot, event: MessageEvent, args: list[str]):
    """/赞 点赞。"""
    await bot.send_like(event.user_id)
    await event.reply("已点赞 👍")


@on_message()
async def handle_message(event: MessageEvent):
    """普通消息处理器:复读。"""
    text = (event.raw_message or "").strip()
    if text and not text.startswith("/"):
        await event.reply(f"你说了: {text}")
