import json
import tempfile
import unittest
from pathlib import Path

from jarvis.homebase import HomeBase
from jarvis.modules import ModuleManager


class ModuleManagerTests(unittest.TestCase):
    def make_homebase(self, computer_control: bool = False) -> HomeBase:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        config = {
            "home_base_version": "1.0",
            "assistant": {"name": "J.A.R.V.I.S.", "mode": "local-first", "status": "test"},
            "capabilities": {"computer_control": computer_control},
            "safety": {
                "allow_arbitrary_shell": False,
                "require_confirmation_for_control_tools": True,
                "allowlisted_apps_only": True,
                "secrets_in_repository": False,
            },
            "planned_modules": ["computer"],
        }
        manifest = {
            "version": "1.0",
            "modules": {
                "computer": {
                    "description": "Desktop tools",
                    "capability": "computer_control",
                    "enabled": True,
                    "entrypoint": "jarvis.adapters.computer",
                }
            },
        }
        (root / "config.json").write_text(json.dumps(config), encoding="utf-8")
        (root / "modules.json").write_text(json.dumps(manifest), encoding="utf-8")
        return HomeBase.load(root)

    def test_enabled_module_requires_capability(self) -> None:
        self.assertFalse(ModuleManager(self.make_homebase(False)).is_available("computer"))
        self.assertTrue(ModuleManager(self.make_homebase(True)).is_available("computer"))

    def test_unknown_module_is_unavailable(self) -> None:
        manager = ModuleManager(self.make_homebase())
        self.assertFalse(manager.is_available("unknown"))

    def test_manifest_does_not_execute_entrypoint(self) -> None:
        manager = ModuleManager(self.make_homebase())
        module = manager.get("computer")
        self.assertIsNotNone(module)
        self.assertEqual(module.entrypoint, "jarvis.adapters.computer")


if __name__ == "__main__":
    unittest.main()
