"""Provider abstraction for the J.A.R.V.I.S. brain.

The runtime can stay deterministic and local by default. A real Gemini
provider is available when the operator explicitly selects it and supplies an
API key through the environment.
"""

from __future__ import annotations

import os
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
        return BrainResponse(text=request.text.strip(), provider=self.name, model="rule-based")


class GeminiProvider(AIProvider):
    """Optional Gemini text provider using Google's current GenAI SDK."""

    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-3.8-flash") -> None:
        self.api_key = api_key.strip()
        self.model = model.strip() or "gemini-3.8-flash"
        if not self.api_key:
            raise ValueError("Gemini API key cannot be empty.")

    def generate(self, request: BrainRequest) -> BrainResponse:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError("The google-genai package is not installed.") from exc

        client = genai.Client(api_key=self.api_key)
        system_instruction = (
            "You are J.A.R.V.I.S., a calm, concise personal AI assistant. "
            "Answer helpfully and naturally. Do not claim you performed an action "
            "unless the runtime explicitly reports that action as completed. "
            "Never invent tools, permissions, files, devices, or results.\n\n"
        )
        if request.system_context:
            system_instruction += request.system_context

        response = client.models.generate_content(
            model=self.model,
            contents=request.text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.4,
                max_output_tokens=512,
            ),
        )
        text = (getattr(response, "text", None) or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return BrainResponse(text=text[:8_000], provider=self.name, model=self.model)


def provider_from_environment() -> AIProvider:
    """Select Gemini only when explicitly configured; otherwise stay local."""

    provider = os.getenv("JARVIS_BRAIN_PROVIDER", "deterministic").strip().lower()
    if provider != "gemini":
        return DeterministicProvider()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return DeterministicProvider()
    return GeminiProvider(api_key, os.getenv("JARVIS_GEMINI_MODEL", "gemini-3.8-flash"))
