from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GroqClient:
    """Minimal Groq chat-completions client using an environment-provided key."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.timeout = float(os.getenv("GROQ_TIMEOUT", "15"))

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(
        self,
        prompt: str,
        context: str = "",
        subject: str = "Any subject",
        mode: str = "Explain",
    ) -> str:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        instructions = (
            "You are StudyBuddy AI, a versatile AI tutor and general question-answering assistant. "
            "Answer academic, technical, planning, writing, and everyday questions accurately. "
            "Use course context as the primary source when relevant, but answer general questions "
            "when context is unavailable. Be structured, practical, and honest about uncertainty. "
            f"The selected subject is {subject}. The requested response style is {mode}."
        )
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": instructions},
                    {
                        "role": "user",
                        "content": f"Course context:\n{context or 'No course context was retrieved.'}\n\n"
                        f"Student question:\n{prompt}",
                    },
                ],
                "temperature": 0.3,
            }
        ).encode("utf-8")
        request = Request(
            self.base_url,
            data=payload,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Groq is unavailable: {exc}") from exc

        try:
            answer = result["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise RuntimeError("Groq returned an empty or invalid response.") from exc
        if not answer:
            raise RuntimeError("Groq returned an empty response.")
        return answer


__all__ = ["GroqClient"]
