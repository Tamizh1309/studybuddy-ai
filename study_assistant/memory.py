from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple


class ConversationMemory:
    """Stores a lightweight chat history for the assistant."""

    def __init__(self, storage_path: str | Path) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._history: List[Tuple[str, str]] = []
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self._history = [(item["question"], item["answer"]) for item in payload]
        except (json.JSONDecodeError, TypeError, KeyError):
            self._history = []

    def _save(self) -> None:
        serializable = [
            {"question": question, "answer": answer} for question, answer in self._history
        ]
        self.storage_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

    def add_turn(self, question: str, answer: str) -> None:
        self._history.append((question, answer))
        self._save()

    def summary(self) -> str:
        if not self._history:
            return "No prior conversation history."
        lines = [f"Q: {question}\nA: {answer}" for question, answer in self._history[-5:]]
        return "\n\n".join(lines)

    def clear(self) -> None:
        self._history = []
        self._save()


__all__ = ["ConversationMemory"]
