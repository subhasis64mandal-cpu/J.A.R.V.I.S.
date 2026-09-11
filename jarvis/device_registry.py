"""Provider-neutral registry for future J.A.R.V.I.S. devices."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Device:
    device_id: str
    name: str
    kind: str
    platform: str
    status: str = "offline"
    capabilities: tuple[str, ...] = ()


class DeviceRegistry:
    """Keep device identity separate from transport/control implementations."""

    def __init__(self, devices: tuple[Device, ...] = ()) -> None:
        self._devices = {device.device_id: device for device in devices}

    def register(self, device: Device) -> None:
        if device.device_id in self._devices:
            raise ValueError(f"Device already registered: {device.device_id}")
        self._devices[device.device_id] = device

    def get(self, device_id: str) -> Device | None:
        return self._devices.get(device_id)

    def all(self) -> tuple[Device, ...]:
        return tuple(sorted(self._devices.values(), key=lambda item: item.name.lower()))

    def summary(self) -> str:
        if not self._devices:
            return "No devices registered."
        return "\n".join(
            f"{device.name} [{device.kind}/{device.platform}] — {device.status}"
            for device in self.all()
        )
