import unittest

from jarvis.brain import Brain
from jarvis.events import EventBus
from jarvis.providers import BrainRequest, BrainResponse, DeterministicProvider


class EchoProvider:
    name = "test"

    def generate(self, request: BrainRequest) -> BrainResponse:
        return BrainResponse(text=f"echo: {request.text}", provider=self.name)


class BrainProviderTests(unittest.TestCase):
    def test_default_provider_is_safe_and_local(self) -> None:
        brain = Brain()
        response = brain.generate("hello")
        self.assertEqual(response, "hello")
        self.assertIsInstance(brain.provider, DeterministicProvider)

    def test_provider_can_be_replaced_without_changing_brain(self) -> None:
        brain = Brain(provider=EchoProvider())
        self.assertEqual(brain.generate("hello"), "echo: hello")


class EventBusTests(unittest.TestCase):
    def test_specific_and_wildcard_handlers_receive_events(self) -> None:
        bus = EventBus()
        received: list[str] = []
        bus.subscribe("assistant.state", lambda event: received.append(event.name))
        bus.subscribe("*", lambda event: received.append(f"*:{event.payload['state']}"))

        bus.publish("assistant.state", state="thinking")

        self.assertEqual(received, ["assistant.state", "*:thinking"])

    def test_unsubscribe_stops_handler(self) -> None:
        bus = EventBus()
        received: list[str] = []
        handler = lambda event: received.append(event.name)
        bus.subscribe("assistant.state", handler)
        bus.unsubscribe("assistant.state", handler)
        bus.publish("assistant.state", state="idle")
        self.assertEqual(received, [])


if __name__ == "__main__":
    unittest.main()
