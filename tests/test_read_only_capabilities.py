import json
from pathlib import Path


def test_catalog_marks_first_read_only_capabilities_available() -> None:
    payload = json.loads((Path("homebase") / "tool_catalog.json").read_text(encoding="utf-8"))
    states = {item["id"]: item["status"] for item in payload["capabilities"]}
    assert states["system"] == "available"
    assert states["files"] == "available"
    assert states["web"] == "available"
    assert states["computer"] == "planned"
    assert states["browser"] == "planned"
    assert states["devices"] == "planned"
