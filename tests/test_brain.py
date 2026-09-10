import unittest

from jarvis.brain import Brain


class BrainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.brain = Brain()

    def test_natural_language_time(self) -> None:
        self.assertEqual(self.brain.normalize("What time is it?"), "time")

    def test_natural_language_date(self) -> None:
        self.assertEqual(self.brain.normalize("tell me the date"), "date")

    def test_unknown_text_is_preserved(self) -> None:
        self.assertEqual(self.brain.normalize("open something"), "open something")

    def test_empty_text_has_no_intent(self) -> None:
        self.assertIsNone(self.brain.understand("   "))


if __name__ == "__main__":
    unittest.main()
