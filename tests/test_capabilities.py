def test_capability_catalog_loads_repository_manifest() -> None:
    from jarvis.capabilities import CapabilityCatalog

    catalog = CapabilityCatalog.load()
    ids = {item.capability_id for item in catalog.capabilities}

    assert {"computer", "web", "browser", "files", "devices", "system"} <= ids
    assert catalog.policy["arbitrary_shell"] is False
    assert catalog.policy["third_party_automation_installed"] is False
