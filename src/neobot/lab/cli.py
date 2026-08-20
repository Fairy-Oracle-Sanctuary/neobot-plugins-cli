"""
neobot-lab —— NeoBot 插件快速原型测试 CLI。

用法:
    neobot-lab <插件目录或 .py 文件> [--once "命令"] [--platform qq]

交互模式:
    /echo 你好         触发 /echo 指令
    echo 你好          触发普通消息处理器(on_message)
    /help              查看已注册指令
    /quit              退出
"""

from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys
from typing import List, Optional

from neobot.plugin_api import registry

BANNER = r"""
   _  _     _        _                 _
  | \| |___| |___ __| |_ __  ___ _ _  | |__ _  _
  | .` / _ \ / -_) _|  _/ _ \/ _ \ '_| | '_ \ || |
  |_|\_\___/_\___\__| \__\___\___/_|   |_.__/\_, |
NeoBot 插件原型实验室                    |__/
"""


def load_plugin(path: str) -> None:
    """加载插件文件或目录(包式插件取 __init__.py)。"""
    p = pathlib.Path(path).resolve()
    if p.is_dir():
        entry = p / "__init__.py"
        if not entry.exists():
            entry = p / "plugin.py"
        if not entry.exists():
            sys.exit(f"❌ 目录 {p} 下没有 __init__.py 或 plugin.py")
        sys.path.insert(0, str(p.parent))
        module_name = p.name
    elif p.is_file():
        entry = p
        sys.path.insert(0, str(p.parent))
        module_name = p.stem
    else:
        sys.exit(f"❌ 找不到插件: {p}")

    spec = importlib.util.spec_from_file_location(module_name, entry)
    if spec is None or spec.loader is None:
        sys.exit(f"❌ 无法加载插件: {entry}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    print(f"✅ 插件已加载: {module_name}")


def show_commands() -> None:
    """打印所有已注册指令。"""
    cmds = registry.list_commands()
    if not cmds:
        print("  (无已注册指令)")
        return
    print(f"  已注册 {len(cmds)} 个指令:")
    for c in cmds:
        print(f"    /{c}")


def run_once(text: str, platform: str) -> int:
    """单次执行一条输入,返回 0。"""
    return run_input(text, platform)


def run_input(text: str, platform: str) -> int:
    """处理一行输入,返回是否继续(0=继续,1=退出)。"""
    text = text.strip()
    if not text:
        return 0

    if text in ("/quit", "/exit", "quit", "exit"):
        print("再见 👋")
        return 1

    if text in ("/help", "help", "?"):
        show_commands()
        return 0

    if text.startswith("/"):
        # 指令: /cmd arg1 arg2
        parts = text[1:].split()
        name, args = parts[0], parts[1:]
        replies = registry.trigger_command(name, args, platform=platform)
    else:
        # 普通消息 → on_message 处理器
        replies = registry.trigger_message(text, platform=platform)

    if not replies:
        print("  (无回复)")
    else:
        for r in replies:
            print(f"  ▶ {r}")
    return 0


def repl(plugin_path: str, platform: str) -> None:
    """交互式 REPL。"""
    print(BANNER)
    print(f"平台: {platform} | 插件: {plugin_path}\n输入 /help 查看指令, /quit 退出\n")
    load_plugin(plugin_path)
    print()
    show_commands()
    print()

    while True:
        try:
            line = input("lab> ")
        except (EOFError, KeyboardInterrupt):
            print("\n再见 👋")
            break
        if run_input(line, platform):
            break


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="neobot-lab",
        description="NeoBot 插件快速原型测试工具(无需 Redis/MySQL/NapCat)",
    )
    parser.add_argument("plugin", help="插件目录或 .py 文件路径")
    parser.add_argument("--once", metavar="CMD", help="单次执行一条输入后退出(适合脚本/CI)")
    parser.add_argument("--platform", default="qq", choices=["qq", "discord", "cli", "mcc"], help="模拟平台")
    args = parser.parse_args(argv)

    if args.once:
        load_plugin(args.plugin)
        print()
        show_commands()
        print(f"\n> {args.once}")
        run_input(args.once, args.platform)
        return 0

    repl(args.plugin, args.platform)
    return 0


if __name__ == "__main__":
    sys.exit(main())
