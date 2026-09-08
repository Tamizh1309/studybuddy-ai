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
        rag_mode: str = "hybrid",
    ) -> str:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        if rag_mode == "strict":
            system_role = (
                "You are StudyBuddy AI operating in STRICT RAG (Retrieval-Augmented Generation) mode. "
                "You must strictly and solely ground your answer in the provided Course Context. "
                "Quote or cite the source file/chunk names (e.g. [Source: filename.pdf]) whenever applicable. "
                "If the provided course context does not contain sufficient details to answer the student's question, "
                "explicitly inform the student that their uploaded course notes do not contain this information, "
                "and do not fabricate or hallucinate answers beyond the provided context."
            )
        else:
            system_role = (
                "You are StudyBuddy AI, an agentic AI tutor and RAG-powered learning assistant. "
                "Always prioritize and cite the provided Course Context as the primary source of truth. "
                "When relevant, cite matching documents using [Source: filename]. If context is partial or absent, "
                "clearly indicate that you are supplementing with general academic knowledge."
            )

        instructions = (
            f"{system_role}\n"
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
