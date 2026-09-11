from jarvis.brain import Brain
from jarvis.decision import DecisionEngine
from jarvis.router import Router


def build_router() -> Router:
    router = Router()
    router.register("status", "status", lambda _: "ok", aliases=("health",))
    router.register("time", "time", lambda _: "now")
    return router


def test_explicit_route_is_proposed_without_execution() -> None:
    decision = DecisionEngine(Brain(), build_router()).decide("health")
    assert decision.action == "ROUTE"
    assert decision.target == "status"
    assert decision.confidence == 0.98


def test_natural_language_intent_is_normalized() -> None:
    decision = DecisionEngine(Brain(), build_router()).decide("what time is it")
    assert decision.action == "ROUTE"
    assert decision.target == "time"


def test_unknown_request_is_not_executable() -> None:
    decision = DecisionEngine(Brain(), build_router()).decide("open my computer")
    assert decision.action == "RESPOND"
    assert decision.target is None
