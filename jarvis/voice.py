"""Optional voice input/output adapters for J.A.R.V.I.S.

Voice dependencies are intentionally optional during the foundation phase.
The assistant remains usable from the terminal when they are not installed.
"""

from __future__ import annotations


class VoiceUnavailable(RuntimeError):
    """Raised when the optional voice stack is not installed or usable."""


class VoiceInterface:
    """Small adapter around SpeechRecognition and pyttsx3.

    Imports happen lazily so importing J.A.R.V.I.S. never requires audio packages.
    """

    def __init__(self) -> None:
        try:
            import pyttsx3  # type: ignore
            import speech_recognition as sr  # type: ignore
        except ImportError as exc:
            raise VoiceUnavailable(
                "Voice mode needs SpeechRecognition and pyttsx3. "
                "Install the optional voice dependencies first."
            ) from exc

        self._sr = sr
        self._recognizer = sr.Recognizer()
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", 175)

    def speak(self, text: str) -> None:
        self._engine.say(text)
        self._engine.runAndWait()

    def listen(self) -> str:
        with self._sr.Microphone() as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self._recognizer.listen(source)

        try:
            return self._recognizer.recognize_google(audio, language="en-IN")
        except self._sr.UnknownValueError:
            return ""
        except self._sr.RequestError as exc:
            raise VoiceUnavailable(f"Speech recognition service error: {exc}") from exc
