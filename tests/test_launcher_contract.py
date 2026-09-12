from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_launcher_contract() -> None:
    source = (ROOT / "launch_jarvis.py").read_text(encoding="utf-8")
    assert "127.0.0.1:8766" in source
    assert "127.0.0.1:8787" in source
    assert "jarvis.agent" in source
    assert "main.py" in source


def test_batch_launcher_points_to_python_launcher() -> None:
    source = (ROOT / "Start-JARVIS.bat").read_text(encoding="utf-8")
    assert "launch_jarvis.py" in source
