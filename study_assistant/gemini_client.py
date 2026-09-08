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
        self.timeout = float(os.getenv("GEMINI_TIMEOUT", "35"))

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
            raise RuntimeError("GEMINI_API_KEY is not configured.")

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
            f"The selected subject is {subject}. The requested response style is {mode}.\n\n"
            f"Course context:\n{context or 'No course context was retrieved.'}\n\n"
            f"Student question:\n{prompt}"
        )
        payload = json.dumps(
            {"contents": [{"parts": [{"text": instructions}]}]}
        ).encode("utf-8")

        models_to_try = [self.model]
        for fallback in ("gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"):
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_error = None
        for model_name in models_to_try:
            for attempt in range(2):
                request = Request(
                    f"{self.base_url}/{model_name}:generateContent?key={self.api_key}",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                try:
                    with urlopen(request, timeout=self.timeout) as response:
                        result = json.loads(response.read().decode("utf-8"))
                        answer = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if answer:
                            return answer
                except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError) as exc:
                    last_error = exc
                    continue

        raise RuntimeError(f"Gemini is unavailable: {last_error}")


__all__ = ["GeminiClient"]
