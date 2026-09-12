from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_one_click_launcher_exists() -> None:
    launcher = ROOT / "launch_jarvis.py"
    assert launcher.is_file()
    source = launcher.read_text(encoding="utf-8")
    assert "127.0.0.1:8766" in source
    assert "127.0.0.1:8787" in source
    assert "jarvis.agent" in source
    assert "main.py" in source


def test_windows_batch_launcher_exists() -> None:
    launcher = ROOT / "Start-JARVIS.bat"
    assert launcher.is_file()
    source = launcher.read_text(encoding="utf-8")
    assert "launch_jarvis.py" in source
