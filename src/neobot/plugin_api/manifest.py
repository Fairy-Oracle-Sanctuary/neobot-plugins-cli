"""
插件清单 —— plugin-api-v1 stub 实现。

与真实契约一致:define_plugin() 声明插件元信息并做字段校验。
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

API_VERSION = "1"

_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{0,63}$")
_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


class PluginManifestError(ValueError):
    """manifest 声明不合法。"""


@dataclass
class PluginManifest:
    """插件清单。字段对齐 docs/plugin-api.md 中定义的契约。"""

    name: str
    description: str = ""
    usage: str = ""
    version: str = "0.1.0"
    author: str = ""
    api_version: str = API_VERSION
    license: str = "AGPL-3.0"
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def define_plugin(
    name: str,
    description: str = "",
    usage: str = "",
    version: str = "0.1.0",
    author: str = "",
    api_version: str = API_VERSION,
    license: str = "AGPL-3.0",
    dependencies: Optional[List[str]] = None,
) -> PluginManifest:
    """声明插件清单,校验关键字段。"""
    if not _NAME_RE.match(name):
        raise PluginManifestError(
            f"插件名不合法: {name!r} (需为 1-64 位字母/数字/下划线/连字符,以字母开头)"
        )
    if not _VERSION_RE.match(version):
        raise PluginManifestError(
            f"插件版本不合法: {version!r} (需为 semver 格式,如 0.1.0)"
        )
    if api_version != API_VERSION:
        raise PluginManifestError(
            f"不支持的插件 API 契约版本: {api_version!r} (当前支持 {API_VERSION!r})"
        )
    return PluginManifest(
        name=name,
        description=description,
        usage=usage,
        version=version,
        author=author,
        api_version=api_version,
        license=license,
        dependencies=list(dependencies or []),
    )
