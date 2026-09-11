"""Provider abstraction for the J.A.R.V.I.S. brain.

Providers are deliberately small: the brain decides what context to send,
while a provider decides how to generate a response. External providers can be
added later without changing the router or Home Base contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class BrainRequest:
    """Provider-neutral request sent by the brain."""

    text: str
    system_context: str = ""


@dataclass(frozen=True)
class BrainResponse:
    """Provider-neutral response returned to the runtime."""

    text: str
    provider: str
    model: str = ""


class AIProvider(ABC):
    """Contract implemented by every AI provider."""

    name = "unknown"

    @abstractmethod
    def generate(self, request: BrainRequest) -> BrainResponse:
        raise NotImplementedError


class DeterministicProvider(AIProvider):
    """Safe local provider used until a real model provider is configured."""

    name = "deterministic"

    def generate(self, request: BrainRequest) -> BrainResponse:
        return BrainResponse(
            text=request.text.strip(),
            provider=self.name,
            model="rule-based",
        )
