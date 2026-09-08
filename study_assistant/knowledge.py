from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class CourseChunk:
    title: str
    text: str
    source: str
    score: float = 0.0


class KnowledgeBase:
    """A lightweight retrieval system that indexes course material files."""

    def __init__(self, materials_dir: str | Path) -> None:
        self.materials_dir = Path(materials_dir)
        self.chunks: List[CourseChunk] = []
        self._index_materials()

    def _index_materials(self) -> None:
        if not self.materials_dir.exists():
            return

        for file_path in sorted(self.materials_dir.rglob("*")):
            if not file_path.is_file() or file_path.suffix.lower() not in {".txt", ".md"}:
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            title = file_path.stem.replace("_", " ").replace("-", " ").title()
            chunks = self._split_text(text)
            for chunk in chunks:
                self.chunks.append(CourseChunk(title=title, text=chunk, source=str(file_path.name)))

    @staticmethod
    def _split_text(text: str, chunk_size: int = 400) -> List[str]:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []

        paragraphs = [part.strip() for part in re.split(r"\n+|(?<!\.)\.(?=\s+[A-Z])", normalized) if part.strip()]
        chunks: List[str] = []
        current = ""
        for paragraph in paragraphs:
            if len(current) + len(paragraph) < chunk_size:
                current = f"{current} {paragraph}".strip()
            else:
                if current:
                    chunks.append(current)
                current = paragraph
        if current:
            chunks.append(current)
        return chunks or [normalized[:chunk_size]]

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"[a-zA-Z0-9_]+", text.lower())

    def search(self, query: str, limit: int = 3) -> List[CourseChunk]:
        if not self.chunks:
            return []

        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return self.chunks[:limit]

        scored: List[CourseChunk] = []
        for chunk in self.chunks:
            tokens = self._tokenize(chunk.text)
            overlap = len(set(tokens).intersection(query_tokens))
            if not overlap:
                continue
            score = overlap + 0.1 * sum(1 for token in query_tokens if token in chunk.text.lower())
            chunk.score = score
            scored.append(chunk)

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]

    def get_context(self, query: str, limit: int = 3) -> str:
        matches = self.search(query, limit=limit)
        if not matches:
            return "No course material matched this question."
        return "\n\n".join(f"[{chunk.source}] {chunk.text}" for chunk in matches)


__all__ = ["KnowledgeBase", "CourseChunk"]
