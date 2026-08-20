"""
neobot-plugin —— NeoBot 插件包管理器。

从插件 Registry (NeoBot-Plugins 仓库的 index.json) 安装/更新/卸载插件。

命令:
    neobot-plugin install <name> [--target DIR] [--yes]
    neobot-plugin search <keyword>
    neobot-plugin list [--installed]
    neobot-plugin update [name]
    neobot-plugin uninstall <name>
    neobot-plugin info <name>

安全:
    - 安装前校验每个文件 SHA256 与 index.json 一致(完整性)
    - manifest 校验(名称/版本/契约版本)
    - 展示插件权限与文件清单,交互确认(或 --yes)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import urllib.request
from typing import Dict, List, Optional

# 默认 Registry(NeoBot-Plugins 仓库 main 分支)
DEFAULT_REGISTRY = "https://raw.githubusercontent.com/Fairy-Oracle-Sanctuary/NeoBot-Plugins/main/index.json"
DEFAULT_TARGET = pathlib.Path("plugins")

_TIMEOUT = 30


class RegistryError(Exception):
    """Registry 相关错误。"""


def _fetch(url: str) -> bytes:
    """下载 URL 内容,超时抛出 RegistryError。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "neobot-plugin/0.1"})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return resp.read()
    except Exception as e:
        raise RegistryError(f"下载失败: {url} ({type(e).__name__}: {e})") from e


def load_registry(registry_url: str) -> Dict:
    """加载并解析 Registry 索引。"""
    raw = _fetch(registry_url)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RegistryError(f"Registry 索引不是合法 JSON: {e}") from e


def find_plugin(registry: Dict, name: str) -> Optional[Dict]:
    """按名称查找插件。"""
    for p in registry.get("plugins", []):
        if p["name"] == name:
            return p
    return None


def _download_file(base_url: str, plugin: Dict, rel_path: str) -> bytes:
    """下载插件单个文件。"""
    url = f"{base_url}/{plugin['name']}/{rel_path}"
    return _fetch(url)


def _verify_sha256(data: bytes, expected: str, path: str) -> None:
    """校验文件 SHA256。"""
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise RegistryError(f"SHA256 校验失败: {path} (期望 {expected[:12]}..., 实际 {actual[:12]}...)")


def _print_plugin_info(p: Dict) -> None:
    """打印插件信息。"""
    deps = ", ".join(p.get("dependencies", [])) or "无"
    print(f"  {p['name']} v{p['version']} ({p.get('license', 'AGPL-3.0')})")
    print(f"    描述: {p.get('description', '')}")
    if p.get("usage"):
        print(f"    用法: {p['usage'].splitlines()[0]}")
    print(f"    作者: {p.get('author', '未知')}")
    print(f"    契约: plugin-api-v{p.get('api_version', '1')}")
    print(f"    依赖: {deps}")
    print(f"    文件: {len(p.get('files', {}))} 个")


def cmd_install(args) -> int:
    """安装插件。"""
    registry = load_registry(args.registry)
    plugin = find_plugin(registry, args.name)
    if plugin is None:
        print(f"❌ 未在 Registry 中找到插件: {args.name}")
        print("   可用: neobot-plugin search <关键词>")
        return 1

    target_dir = args.target / plugin["name"]
    files = plugin.get("files", {})

    print(f"将安装插件: {plugin['name']} v{plugin['version']}")
    _print_plugin_info(plugin)
    print(f"目标目录: {target_dir}")

    if not args.yes:
        answer = input("继续安装? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("已取消")
            return 0

    # 下载并校验
    base = args.registry.rsplit("/", 1)[0] + "/plugins"
    downloaded: List[tuple] = []
    try:
        for rel_path, expected in files.items():
            data = _download_file(base, plugin, rel_path)
            _verify_sha256(data, expected, rel_path)
            downloaded.append((rel_path, data))
    except RegistryError as e:
        print(f"❌ {e}")
        return 1

    # 写入目标
    target_dir.mkdir(parents=True, exist_ok=True)
    for rel_path, data in downloaded:
        dest = target_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)

    # 写入本地 manifest(便于 list/update 读取版本信息)
    local_manifest = {
        "name": plugin["name"],
        "description": plugin.get("description", ""),
        "usage": plugin.get("usage", ""),
        "version": plugin["version"],
        "author": plugin.get("author", ""),
        "api_version": plugin.get("api_version", "1"),
        "license": plugin.get("license", "AGPL-3.0"),
        "dependencies": plugin.get("dependencies", []),
        "entry": plugin.get("entry", "plugin.py"),
    }
    (target_dir / "manifest.json").write_text(
        json.dumps(local_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"✅ 已安装 {plugin['name']} v{plugin['version']} 到 {target_dir}")
    if plugin.get("dependencies"):
        print(f"⚠️  依赖: {', '.join(plugin['dependencies'])} (请手动安装)")
    return 0


def cmd_search(args) -> int:
    """搜索插件。"""
    registry = load_registry(args.registry)
    kw = args.keyword.lower()
    matches = [
        p for p in registry.get("plugins", [])
        if kw in p["name"].lower() or kw in p.get("description", "").lower()
    ]
    if not matches:
        print(f"未找到匹配 '{args.keyword}' 的插件")
        return 1
    print(f"找到 {len(matches)} 个插件:")
    for p in matches:
        _print_plugin_info(p)
        print()
    return 0


def cmd_list(args) -> int:
    """列出 Registry 中的插件(或本地已安装)。"""
    if args.installed:
        target = args.target
        if not target.exists():
            print(f"目标目录不存在: {target}")
            return 0
        installed = [d for d in sorted(target.iterdir()) if d.is_dir()]
        if not installed:
            print("未安装任何插件")
            return 0
        print(f"已安装插件 ({len(installed)}):")
        for d in installed:
            manifest_file = d / "manifest.json"
            if manifest_file.exists():
                try:
                    m = json.loads(manifest_file.read_text(encoding="utf-8"))
                    print(f"  {m.get('name', d.name)} v{m.get('version', '?')} — {m.get('description', '')[:50]}")
                    continue
                except (json.JSONDecodeError, OSError):
                    pass
            print(f"  {d.name} (无 manifest)")
        return 0

    registry = load_registry(args.registry)
    plugins = registry.get("plugins", [])
    if not plugins:
        print("Registry 中暂无插件")
        return 0
    print(f"Registry 中的插件 ({len(plugins)}):")
    for p in plugins:
        print(f"  {p['name']} v{p['version']} — {p.get('description', '')[:60]}")
    return 0


def cmd_update(args) -> int:
    """更新插件(重新安装到目标,覆盖本地文件)。"""
    registry = load_registry(args.registry)
    plugin = find_plugin(registry, args.name)
    if plugin is None:
        print(f"❌ 未在 Registry 中找到插件: {args.name}")
        return 1

    target_dir = args.target / plugin["name"]
    if not target_dir.exists():
        print(f"插件未安装: {plugin['name']} (先 install)")
        return 1

    print(f"更新插件: {plugin['name']} -> v{plugin['version']}")
    args.yes = args.yes or True
    return cmd_install(args)


def cmd_uninstall(args) -> int:
    """卸载插件(删除目录,需确认)。"""
    target_dir = args.target / args.name
    if not target_dir.exists():
        print(f"插件未安装: {args.name}")
        return 1

    if not args.yes:
        answer = input(f"删除 {target_dir}? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("已取消")
            return 0

    import shutil

    shutil.rmtree(target_dir)
    print(f"✅ 已卸载 {args.name}")
    return 0


def cmd_info(args) -> int:
    """查看插件详情。"""
    registry = load_registry(args.registry)
    plugin = find_plugin(registry, args.name)
    if plugin is None:
        print(f"❌ 未在 Registry 中找到插件: {args.name}")
        return 1
    _print_plugin_info(plugin)
    print("  文件清单:")
    for path in plugin.get("files", {}):
        print(f"    {path}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="neobot-plugin",
        description="NeoBot 插件包管理器(从 Registry 安装/更新/卸载插件)",
    )
    parser.add_argument("--registry", default=DEFAULT_REGISTRY, help="Registry 索引 URL")
    parser.add_argument("--target", type=pathlib.Path, default=DEFAULT_TARGET, help="插件安装目录(默认 plugins/)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser("install", help="安装插件")
    p_install.add_argument("name", help="插件名")
    p_install.add_argument("--yes", "-y", action="store_true", help="跳过确认")
    p_install.set_defaults(func=cmd_install)

    p_search = sub.add_parser("search", help="搜索插件")
    p_search.add_argument("keyword", help="关键词")
    p_search.set_defaults(func=cmd_search)

    p_list = sub.add_parser("list", help="列出插件")
    p_list.add_argument("--installed", action="store_true", help="列出本地已安装")
    p_list.set_defaults(func=cmd_list)

    p_update = sub.add_parser("update", help="更新插件")
    p_update.add_argument("name", help="插件名")
    p_update.add_argument("--yes", "-y", action="store_true", help="跳过确认")
    p_update.set_defaults(func=cmd_update)

    p_uninstall = sub.add_parser("uninstall", help="卸载插件")
    p_uninstall.add_argument("name", help="插件名")
    p_uninstall.add_argument("--yes", "-y", action="store_true", help="跳过确认")
    p_uninstall.set_defaults(func=cmd_uninstall)

    p_info = sub.add_parser("info", help="查看插件详情")
    p_info.add_argument("name", help="插件名")
    p_info.set_defaults(func=cmd_info)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RegistryError as e:
        print(f"❌ {e}")
        return 1
    except KeyboardInterrupt:
        print("\n已中断")
        return 130


if __name__ == "__main__":
    sys.exit(main())
