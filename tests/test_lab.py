"""neobot-plugin-lab 测试套件。"""

import pathlib
import subprocess
import sys

import pytest

PLUGIN_DIR = pathlib.Path(__file__).resolve().parent.parent / "example_plugin"
CLI = [sys.executable, "-m", "neobot.lab"]


@pytest.fixture(autouse=True)
def _reset():
    """每个测试前清空注册表。"""
    from neobot.plugin_api import registry

    registry.reset_registry()
    yield
    registry.reset_registry()


def test_import_plugin_api():
    """plugin_api stub 可导入且导出核心符号。"""
    import neobot.plugin_api as api

    for name in ("command", "platform_command", "on_message", "define_plugin", "MessageSegment",
                 "MessageEvent", "Bot", "Permission", "ModuleLogger"):
        assert hasattr(api, name), f"缺少导出: {name}"


def test_define_plugin_validates():
    """define_plugin 校验非法名称。"""
    from neobot.plugin_api import PluginManifestError, define_plugin

    with pytest.raises(PluginManifestError):
        define_plugin(name="中文名")


def test_command_registration():
    """command 装饰器注册到 registry。"""
    from neobot.plugin_api import command
    from neobot.plugin_api import registry

    @command("ping")
    async def handle_ping(bot, event, args):
        await event.reply("pong")

    assert "ping" in registry.list_commands()


def test_trigger_command_replies():
    """触发命令收集回复。"""
    from neobot.plugin_api import command
    from neobot.plugin_api import registry

    @command("hello")
    async def handle_hello(bot, event, args):
        await event.reply(f"你好, {' '.join(args)}")

    replies = registry.trigger_command("hello", ["世界"])
    assert replies == ["你好, 世界"]


def test_trigger_command_override_permission():
    """override_permission_check 传入 permission_granted。"""
    from neobot.plugin_api import command
    from neobot.plugin_api import registry

    @command("secret", override_permission_check=True)
    async def handle_secret(bot, event, permission_granted):
        await event.reply(f"granted={permission_granted}")

    replies = registry.trigger_command("secret", [])
    assert replies == ["granted=True"]


def test_trigger_message_handlers():
    """on_message 处理器接收普通消息。"""
    from neobot.plugin_api import on_message
    from neobot.plugin_api import registry

    @on_message()
    async def handle_all(event):
        await event.reply(f"收到: {event.raw_message}")

    replies = registry.trigger_message("在吗")
    assert replies == ["收到: 在吗"]


def test_cli_loads_plugin():
    """CLI --once 加载示例插件并触发命令。"""
    result = subprocess.run(
        [*CLI, str(PLUGIN_DIR), "--once", "/ping"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "pong" in result.stdout
