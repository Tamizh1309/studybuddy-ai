from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OllamaClient:
    """Small standard-library client for a local Ollama server."""

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "nemotron-3-nano:30b")

    def is_available(self) -> bool:
        try:
            with urlopen(f"{self.base_url}/api/tags", timeout=2):
                return True
        except (HTTPError, URLError, TimeoutError):
            return False

    def chat(self, prompt: str, context: str = "", subject: str = "Any subject", mode: str = "Explain") -> str:
        instructions = (
            "You are StudyBuddy AI, a versatile AI tutor and general question-answering assistant. "
            "Answer questions about academics, coding, science, planning, writing, and everyday topics. "
            "Use the supplied course context as the primary source when it is relevant, but answer general "
            "questions from your own knowledge when the context is missing. Be accurate, structured, and "
            "honest about uncertainty. Use concise explanations, examples, and steps when useful. "
            f"The selected subject is {subject}. The requested response style is {mode}.\n\n"
            f"Course context:\n{context or 'No course context was retrieved.'}\n\n"
            f"Student question:\n{prompt}"
        )
        payload = json.dumps(
            {"model": self.model, "prompt": instructions, "stream": False}
        ).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers=self._headers(),
            method="POST",
        )
        try:
            with urlopen(request, timeout=90) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Ollama is unavailable: {exc}") from exc

        answer = result.get("response", "").strip()
        if not answer:
            raise RuntimeError("Ollama returned an empty response.")
        return answer

    @staticmethod
    def _headers() -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        api_key = os.getenv("OLLAMA_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers


__all__ = ["OllamaClient"]
