from pathlib import Path

from jarvis.device_registry import Device, DeviceRegistry
from jarvis.filetools import file_list, file_read
from jarvis.webtools import web_get


def test_file_tools_cannot_escape_workspace(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    secret = tmp_path.parent / "secret.txt"
    secret.write_text("no", encoding="utf-8")
    assert "restricted" in file_read("../secret.txt")
    (tmp_path / "ok.txt").write_text("hello", encoding="utf-8")
    assert "hello" in file_read("ok.txt")
    assert "FILE ok.txt" in file_list()


def test_web_tool_requires_http_url() -> None:
    assert "Use:" in web_get("example.com")


def test_device_registry_keeps_identity_separate_from_transport() -> None:
    registry = DeviceRegistry()
    registry.register(Device("pc", "Main PC", "computer", "windows", "online", ("system",)))
    assert registry.get("pc").name == "Main PC"
    assert "Main PC" in registry.summary()
