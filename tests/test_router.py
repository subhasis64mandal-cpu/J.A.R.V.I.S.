import unittest

from jarvis.router import Router


class RouterTests(unittest.TestCase):
    def test_dispatches_tool_and_alias(self) -> None:
        router = Router()
        router.register("echo", "Echo text", lambda value: value or "empty", aliases=("repeat",))

        self.assertEqual(router.route("echo hello"), "hello")
        self.assertEqual(router.route("repeat hello"), "hello")

    def test_unknown_tool_is_safe(self) -> None:
        router = Router()
        self.assertEqual(router.route("delete everything"), "I don't have a tool for that yet.")

    def test_help_lists_registered_tools(self) -> None:
        router = Router()
        router.register("echo", "Echo text", lambda value: value)
        self.assertIn("echo", router.help_text())


if __name__ == "__main__":
    unittest.main()
