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
        render_hosted = os.getenv("RENDER", "").lower() == "true"
        configured_enabled = os.getenv("OLLAMA_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
        self.enabled = configured_enabled and not render_hosted

    def is_available(self) -> bool:
        if not self.enabled:
            return False
        try:
            with urlopen(f"{self.base_url}/api/tags", timeout=2):
                return True
        except (HTTPError, URLError, TimeoutError):
            return False

    def chat(
        self,
        prompt: str,
        context: str = "",
        subject: str = "Any subject",
        mode: str = "Explain",
        rag_mode: str = "hybrid",
    ) -> str:
        if not self.enabled:
            raise RuntimeError("Ollama is disabled.")

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
