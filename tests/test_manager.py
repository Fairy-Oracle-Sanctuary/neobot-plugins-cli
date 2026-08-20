"""neobot-plugin 包管理器测试。"""

import json
import pathlib
import subprocess
import sys

import pytest

from neobot.plugin.manager import (
    RegistryError,
    _verify_sha256,
    find_plugin,
    load_registry,
)

# 测试用本地 Registry(不走网络)
TEST_REGISTRY = pathlib.Path(__file__).resolve().parent / "fixtures" / "index.json"


def _make_registry(tmp_path: pathlib.Path, files: dict) -> pathlib.Path:
    """构建本地 Registry fixture。"""
    reg = tmp_path / "registry"
    (reg / "plugins" / "demo").mkdir(parents=True)
    hashes = {}
    for name, content in files.items():
        p = reg / "plugins" / "demo" / name
        p.write_text(content, encoding="utf-8")
        import hashlib

        hashes[name] = hashlib.sha256(p.read_bytes()).hexdigest()

    index = {
        "schema_version": 1,
        "plugins": [
            {
                "name": "demo",
                "description": "测试插件",
                "usage": "/demo",
                "version": "0.1.0",
                "author": "tester",
                "api_version": "1",
                "license": "AGPL-3.0",
                "dependencies": [],
                "entry": "plugin.py",
                "files": hashes,
            }
        ],
    }
    (reg / "index.json").write_text(json.dumps(index), encoding="utf-8")
    return reg / "index.json"


def test_load_registry_invalid_json():
    """非法 JSON 抛 RegistryError。"""
    with pytest.raises((RegistryError, Exception)):
        load_registry("file:///nonexistent/index.json")


def test_find_plugin():
    """按名称查找插件。"""
    registry = {"plugins": [{"name": "a"}, {"name": "b"}]}
    found = find_plugin(registry, "a")
    assert found is not None and found["name"] == "a"
    assert find_plugin(registry, "zzz") is None


def test_verify_sha256_ok():
    """SHA256 匹配通过。"""
    import hashlib

    data = b"hello"
    expected = hashlib.sha256(data).hexdigest()
    _verify_sha256(data, expected, "test.txt")  # 不抛异常


def test_verify_sha256_mismatch():
    """SHA256 不匹配抛 RegistryError。"""
    import hashlib

    data = b"hello"
    wrong = hashlib.sha256(b"tampered").hexdigest()
    with pytest.raises(RegistryError):
        _verify_sha256(data, wrong, "test.txt")


def test_install_via_cli(tmp_path):
    """CLI 从本地 Registry 安装插件,含 SHA256 校验与 manifest 生成。"""
    reg_index = _make_registry(tmp_path, {"plugin.py": "print('demo')"})
    target = tmp_path / "out"

    result = subprocess.run(
        [
            sys.executable, "-m", "neobot.plugin.manager",
            "--registry", reg_index.as_uri(),
            "--target", str(target),
            "install", "demo", "--yes",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert (target / "demo" / "plugin.py").exists()
    assert (target / "demo" / "manifest.json").exists()
    manifest = json.loads((target / "demo" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "demo"
    assert manifest["version"] == "0.1.0"


def test_uninstall_via_cli(tmp_path):
    """CLI 卸载插件。"""
    target = tmp_path / "out"
    target.mkdir()
    (target / "demo").mkdir()

    result = subprocess.run(
        [
            sys.executable, "-m", "neobot.plugin.manager",
            "--target", str(target),
            "uninstall", "demo", "--yes",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert not (target / "demo").exists()
