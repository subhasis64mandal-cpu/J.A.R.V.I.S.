"""Device identity and capability metadata for future multi-device control."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DeviceKind(StrEnum):
    DESKTOP = "desktop"
    PHONE = "phone"
    TABLET = "tablet"
    OTHER = "other"


@dataclass(frozen=True)
class Device:
    """A known device; this object contains identity, not credentials."""

    device_id: str
    name: str
    kind: DeviceKind
    online: bool = False
    capabilities: tuple[str, ...] = ()


class DeviceRegistry:
    """In-memory inventory used by orchestration and the future device layer."""

    def __init__(self) -> None:
        self._devices: dict[str, Device] = {}

    def register(self, device: Device) -> None:
        key = device.device_id.strip()
        if not key:
            raise ValueError("device_id cannot be empty")
        if key in self._devices:
            raise ValueError(f"Device already registered: {key}")
        self._devices[key] = device

    def get(self, device_id: str) -> Device | None:
        return self._devices.get(device_id.strip())

    def list_devices(self) -> tuple[Device, ...]:
        return tuple(sorted(self._devices.values(), key=lambda item: item.name.lower()))
