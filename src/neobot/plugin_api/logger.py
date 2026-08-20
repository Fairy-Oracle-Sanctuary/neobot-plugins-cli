"""
日志 —— plugin-api-v1 stub。

ModuleLogger 输出带插件名前缀的日志,方便原型测试时区分来源。
"""

from __future__ import annotations

import sys


class ModuleLogger:
    """模块级日志器:输出到 stderr,便于 REPL 里与命令回复区分。"""

    def __init__(self, name: str = ""):
        self.name = name or "NeoBot"

    def _log(self, level: str, msg: str) -> None:
        print(f"[{self.name}] {level}: {msg}", file=sys.stderr)

    def debug(self, msg: str) -> None:
        self._log("DEBUG", msg)

    def info(self, msg: str) -> None:
        self._log("INFO", msg)

    def warning(self, msg: str) -> None:
        self._log("WARN", msg)

    def error(self, msg: str) -> None:
        self._log("ERROR", msg)

    def success(self, msg: str) -> None:
        self._log("OK", msg)


logger = ModuleLogger("lab")
