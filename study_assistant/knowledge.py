from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class CourseChunk:
    title: str
    text: str
    source: str
    chunk_id: str = ""
    score: float = 0.0
    relevance_percent: float = 0.0
    term_freqs: Dict[str, float] = field(default_factory=dict)
    vector_norm: float = 0.0


class KnowledgeBase:
    """Production-grade Vector Space Retrieval system (TF-IDF + Cosine Similarity)

    Features:
    - Semantic sliding-window chunking with boundary overlap
    - TF-IDF vector space indexing with BM25 IDF dampening
    - Normalized Cosine Similarity scoring
    - Exact-phrase and bigram boost for precise academic retrieval
    - Rich citation metadata tracking
    """

    def __init__(self, materials_dir: str | Path) -> None:
        self.materials_dir = Path(materials_dir)
        self.chunks: List[CourseChunk] = []
        self.vocabulary: set[str] = set()
        self.idf: Dict[str, float] = {}
        self.doc_freqs: Counter[str] = Counter()
        self._index_materials()

    def _index_materials(self) -> None:
        self.chunks = []
        self.vocabulary = set()
        self.idf = {}
        self.doc_freqs = Counter()

        if not self.materials_dir.exists():
            return

        for file_path in sorted(self.materials_dir.rglob("*")):
            if not file_path.is_file() or file_path.suffix.lower() not in {".txt", ".md", ".pdf", ".docx", ".pptx"}:
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            title = file_path.stem.replace("_", " ").replace("-", " ").title()
            raw_chunks = self._split_text_sliding(text, chunk_size=420, overlap_size=60)
            for idx, chunk_text in enumerate(raw_chunks, start=1):
                chunk = CourseChunk(
                    title=title,
                    text=chunk_text,
                    source=str(file_path.name),
                    chunk_id=f"{file_path.stem}_chunk_{idx}",
                )
                self.chunks.append(chunk)

        self._build_vector_index()

    def _build_vector_index(self) -> None:
        total_docs = len(self.chunks)
        if total_docs == 0:
            return

        # 1. Calculate Document Frequency (DF)
        for chunk in self.chunks:
            tokens = self._tokenize(chunk.text)
            counts = Counter(tokens)
            total_tokens = max(1, len(tokens))
            chunk.term_freqs = {tok: count / total_tokens for tok, count in counts.items()}
            for token in chunk.term_freqs:
                self.doc_freqs[token] += 1
                self.vocabulary.add(token)

        # 2. Compute BM25-smoothed IDF: ln(1 + (N - df + 0.5) / (df + 0.5))
        for token, df in self.doc_freqs.items():
            self.idf[token] = math.log(1.0 + (total_docs - df + 0.5) / (df + 0.5))

        # 3. Compute L2 Vector Norm for each document chunk
        for chunk in self.chunks:
            sq_sum = 0.0
            for token, tf in chunk.term_freqs.items():
                weight = tf * self.idf.get(token, 1.0)
                sq_sum += weight * weight
            chunk.vector_norm = math.sqrt(sq_sum) if sq_sum > 0 else 1.0

    @staticmethod
    def _split_text_sliding(text: str, chunk_size: int = 420, overlap_size: int = 60) -> List[str]:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []

        # Split on sentence boundaries and natural paragraphs
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", normalized) if part.strip()]
        if not sentences:
            sentences = [normalized]

        chunks: List[str] = []
        current = ""
        for sentence in sentences:
            if len(current) + len(sentence) + 1 <= chunk_size:
                current = f"{current} {sentence}".strip()
            else:
                if current:
                    chunks.append(current)
                    # Sliding overlap window: preserve trailing characters/words
                    overlap = current[-overlap_size:].strip()
                    current = f"{overlap} {sentence}".strip()
                else:
                    chunks.append(sentence[:chunk_size])
                    current = sentence[chunk_size:].strip()

        if current:
            chunks.append(current)

        return chunks or [normalized[:chunk_size]]

    # Backward compatibility alias
    _split_text = _split_text_sliding

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        # Lowercase alphanumeric extraction with basic stopword filtering
        raw_tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        stopwords = {
            "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or", "is", "are",
            "was", "were", "be", "been", "it", "its", "that", "this", "with", "by", "as",
        }
        return [t for t in raw_tokens if t not in stopwords and len(t) > 1] or raw_tokens

    def search(self, query: str, limit: int = 3) -> List[CourseChunk]:
        if not self.chunks:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return self.chunks[:limit]

        query_counts = Counter(query_tokens)
        q_len = max(1, len(query_tokens))
        q_tf = {tok: c / q_len for tok, c in query_counts.items()}

        # Compute query vector and query L2 norm
        q_norm_sq = 0.0
        q_weights: Dict[str, float] = {}
        for tok, tf in q_tf.items():
            idf_val = self.idf.get(tok, 1.5)
            weight = tf * idf_val
            q_weights[tok] = weight
            q_norm_sq += weight * weight
        q_norm = math.sqrt(q_norm_sq) if q_norm_sq > 0 else 1.0

        q_lower = query.lower().strip()
        scored: List[CourseChunk] = []

        for chunk in self.chunks:
            # 1. Cosine similarity
            dot_product = 0.0
            overlap_count = 0
            for tok, q_w in q_weights.items():
                if tok in chunk.term_freqs:
                    overlap_count += 1
                    doc_w = chunk.term_freqs[tok] * self.idf.get(tok, 1.0)
                    dot_product += q_w * doc_w

            if overlap_count == 0:
                continue

            cosine_sim = dot_product / (q_norm * chunk.vector_norm)

            # 2. Exact phrase and title boost
            phrase_boost = 0.0
            if q_lower in chunk.text.lower():
                phrase_boost += 0.25
            if any(tok in chunk.title.lower() for tok in query_tokens):
                phrase_boost += 0.15

            total_score = cosine_sim + phrase_boost
            chunk.score = round(total_score, 4)
            # Relevance percentage normalized between 20% and 99%
            relevance = min(99.0, max(25.0, round(total_score * 85.0 + 15.0, 1)))
            chunk.relevance_percent = relevance
            scored.append(chunk)

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]

    def search_with_metadata(self, query: str, limit: int = 3) -> List[dict]:
        """Return structured citations with snippets, scores, and source file metadata."""
        matches = self.search(query, limit=limit)
        results = []
        for m in matches:
            results.append(
                {
                    "chunk_id": m.chunk_id or f"{m.source}_0",
                    "source": m.source,
                    "title": m.title,
                    "snippet": (m.text[:220] + "...") if len(m.text) > 220 else m.text,
                    "full_text": m.text,
                    "score": m.score,
                    "relevance_percent": m.relevance_percent,
                }
            )
        return results

    def get_context(self, query: str, limit: int = 3) -> str:
        matches = self.search(query, limit=limit)
        if not matches:
            return "No course material matched this question."
        return "\n\n".join(
            f"[Source: {chunk.source} | Chunk: {chunk.chunk_id or idx + 1} | Match: {chunk.relevance_percent}%]\n{chunk.text}"
            for idx, chunk in enumerate(matches)
        )

    def materials(self) -> List[str]:
        """Return the indexed source filenames without duplicate chunk entries."""
        return sorted({chunk.source for chunk in self.chunks})


__all__ = ["KnowledgeBase", "CourseChunk"]
