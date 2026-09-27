"""Lightweight document retrieval (RAG) layer.

Uses TF-IDF + cosine similarity rather than a neural embedding model so the
app has no heavyweight model download and runs fully offline for retrieval
(only the generation step calls out to the LLM). Swap `DocumentStore` for a
vector-DB-backed implementation without changing any calling code if you
later want semantic embeddings instead.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    doc_name: str
    doc_type: str
    chunk_id: int
    text: str


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    text = text.strip()
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


class DocumentStore:
    """In-memory store of chunked documents with TF-IDF retrieval."""

    def __init__(self) -> None:
        self.chunks: List[Chunk] = []
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._matrix = None

    def add_document(self, doc_name: str, doc_type: str, text: str) -> int:
        pieces = chunk_text(text)
        for i, piece in enumerate(pieces):
            self.chunks.append(Chunk(doc_name=doc_name, doc_type=doc_type, chunk_id=i, text=piece))
        self._invalidate()
        return len(pieces)

    def remove_document(self, doc_name: str) -> None:
        self.chunks = [c for c in self.chunks if c.doc_name != doc_name]
        self._invalidate()

    def clear(self) -> None:
        self.chunks = []
        self._invalidate()

    def _invalidate(self) -> None:
        self._vectorizer = None
        self._matrix = None

    @property
    def document_names(self) -> List[str]:
        seen: List[str] = []
        for c in self.chunks:
            if c.doc_name not in seen:
                seen.append(c.doc_name)
        return seen

    def _ensure_index(self) -> None:
        if self._vectorizer is None and self.chunks:
            self._vectorizer = TfidfVectorizer(stop_words="english")
            self._matrix = self._vectorizer.fit_transform([c.text for c in self.chunks])

    def search(self, query: str, top_k: int = 8, doc_type: Optional[str] = None) -> List[Chunk]:
        self._ensure_index()
        if not self.chunks or self._vectorizer is None:
            return []
        query_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self._matrix)[0]
        ranked = sorted(range(len(self.chunks)), key=lambda i: sims[i], reverse=True)
        results: List[Chunk] = []
        for i in ranked:
            if sims[i] <= 0:
                continue
            chunk = self.chunks[i]
            if doc_type and chunk.doc_type != doc_type:
                continue
            results.append(chunk)
            if len(results) >= top_k:
                break
        return results

    def format_context(self, chunks: List[Chunk]) -> str:
        blocks = []
        for c in chunks:
            blocks.append(f"[Source: {c.doc_name} | type: {c.doc_type} | chunk {c.chunk_id}]\n{c.text}")
        return "\n\n---\n\n".join(blocks)
