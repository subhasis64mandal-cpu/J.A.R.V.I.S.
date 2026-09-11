import pytest

from jarvis.devices import Device, DeviceKind, DeviceRegistry


def test_register_and_lookup_device() -> None:
    registry = DeviceRegistry()
    device = Device("phone-01", "Primary Phone", DeviceKind.PHONE, online=True, capabilities=("display", "audio"))

    registry.register(device)

    assert registry.get("phone-01") == device
    assert registry.list_devices() == (device,)


def test_duplicate_device_id_is_rejected() -> None:
    registry = DeviceRegistry()
    registry.register(Device("pc-01", "Desktop", DeviceKind.DESKTOP))

    with pytest.raises(ValueError):
        registry.register(Device("pc-01", "Desktop 2", DeviceKind.DESKTOP))
