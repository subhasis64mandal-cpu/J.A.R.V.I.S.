import json
import tempfile
import unittest
from pathlib import Path

from jarvis.homebase import HomeBase
from jarvis.router import Router


class HomeBaseTests(unittest.TestCase):
    def make_homebase(self, computer_control: bool = False) -> HomeBase:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        config = {
            "home_base_version": "1.0",
            "assistant": {"name": "J.A.R.V.I.S.", "mode": "local-first", "status": "test"},
            "capabilities": {
                "voice": True,
                "ai_brain": True,
                "computer_control": computer_control,
            },
            "safety": {
                "allow_arbitrary_shell": False,
                "require_confirmation_for_control_tools": True,
                "allowlisted_apps_only": True,
                "secrets_in_repository": False,
            },
            "planned_modules": ["computer"],
        }
        (root / "config.json").write_text(json.dumps(config), encoding="utf-8")
        return HomeBase.load(root)

    def test_loads_home_base(self) -> None:
        homebase = self.make_homebase()
        self.assertEqual(homebase.assistant_name(), "J.A.R.V.I.S.")
        self.assertTrue(homebase.capability_enabled("ai_brain"))
        self.assertFalse(homebase.allows_arbitrary_shell())

    def test_router_blocks_disabled_capability(self) -> None:
        homebase = self.make_homebase(computer_control=False)
        router = Router(homebase)
        router.register(
            "computer",
            "Computer control test",
            lambda _: "ran",
            capability="computer_control",
        )
        self.assertIn("disabled in Home Base", router.route("computer"))

    def test_router_allows_enabled_capability(self) -> None:
        homebase = self.make_homebase(computer_control=True)
        router = Router(homebase)
        router.register(
            "computer",
            "Computer control test",
            lambda _: "ran",
            capability="computer_control",
        )
        self.assertEqual(router.route("computer"), "ran")


if __name__ == "__main__":
    unittest.main()
