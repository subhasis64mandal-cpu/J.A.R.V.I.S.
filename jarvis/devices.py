"""Device identity and capability metadata for multi-device orchestration."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path


class DeviceKind(StrEnum):
    DESKTOP = "desktop"
    PHONE = "phone"
    TABLET = "tablet"
    OTHER = "other"


@dataclass(frozen=True)
class Device:
    """Known device identity; credentials are intentionally not stored here."""

    device_id: str
    name: str
    kind: DeviceKind
    online: bool = False
    capabilities: tuple[str, ...] = ()


class DeviceRegistry:
    """Persistent inventory used by orchestration; transport remains separate."""

    def __init__(self, path: str | Path = ".jarvis/devices.json") -> None:
        self.path = Path(path)
        self._devices: dict[str, Device] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            self._devices = {}
            return
        devices = raw.get("devices", []) if isinstance(raw, dict) else []
        self._devices = {}
        for value in devices:
            if not isinstance(value, dict):
                continue
            try:
                kind = DeviceKind(str(value.get("kind", DeviceKind.OTHER)))
                device = Device(
                    device_id=str(value["device_id"]).strip(),
                    name=str(value["name"]).strip(),
                    kind=kind,
                    online=bool(value.get("online", False)),
                    capabilities=tuple(str(item) for item in value.get("capabilities", [])),
                )
            except (KeyError, ValueError, TypeError):
                continue
            if device.device_id and device.name:
                self._devices[device.device_id] = device

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "devices": [asdict(item) for item in self._devices.values()]}
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def register(self, device: Device) -> Device:
        key = device.device_id.strip()
        if not key:
            raise ValueError("device_id cannot be empty")
        if not device.name.strip():
            raise ValueError("device name cannot be empty")
        if key in self._devices:
            raise ValueError(f"Device already registered: {key}")
        self._devices[key] = device
        self.save()
        return device

    def upsert(self, device: Device) -> Device:
        key = device.device_id.strip()
        if not key or not device.name.strip():
            raise ValueError("device identity is incomplete")
        self._devices[key] = device
        self.save()
        return device

    def set_online(self, device_id: str, online: bool) -> Device:
        current = self.get(device_id)
        if current is None:
            raise ValueError(f"Unknown device: {device_id}")
        updated = Device(current.device_id, current.name, current.kind, online, current.capabilities)
        self._devices[current.device_id] = updated
        self.save()
        return updated

    def remove(self, device_id: str) -> bool:
        removed = self._devices.pop(device_id.strip(), None) is not None
        if removed:
            self.save()
        return removed

    def get(self, device_id: str) -> Device | None:
        return self._devices.get(device_id.strip())

    def list_devices(self) -> tuple[Device, ...]:
        return tuple(sorted(self._devices.values(), key=lambda item: item.name.lower()))

    def list_text(self) -> str:
        devices = self.list_devices()
        if not devices:
            return "No devices are paired."
        lines = ["Paired devices:"]
        for device in devices:
            state = "ONLINE" if device.online else "OFFLINE"
            caps = ", ".join(device.capabilities) if device.capabilities else "no advertised capabilities"
            lines.append(f"  {device.name} [{device.kind}] — {state} — {caps}")
        return "\n".join(lines)
