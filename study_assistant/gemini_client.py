from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GeminiClient:
    """Minimal Gemini REST client using an environment-provided API key."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, prompt: str, context: str = "", subject: str = "Any subject", mode: str = "Explain") -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        instructions = (
            "You are StudyBuddy AI, a versatile AI tutor and general question-answering assistant. "
            "Answer academic, technical, planning, writing, and everyday questions accurately. "
            "Use the course context as the primary source when relevant, but answer general questions "
            "when context is unavailable. Be structured, practical, and honest about uncertainty. "
            f"The selected subject is {subject}. The requested response style is {mode}.\n\n"
            f"Course context:\n{context or 'No course context was retrieved.'}\n\n"
            f"Student question:\n{prompt}"
        )
        payload = json.dumps(
            {"contents": [{"parts": [{"text": instructions}]}]}
        ).encode("utf-8")
        request = Request(
            f"{self.base_url}/{self.model}:generateContent?key={self.api_key}",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Gemini is unavailable: {exc}") from exc

        try:
            answer = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise RuntimeError("Gemini returned an empty or invalid response.") from exc
        if not answer:
            raise RuntimeError("Gemini returned an empty response.")
        return answer


__all__ = ["GeminiClient"]
