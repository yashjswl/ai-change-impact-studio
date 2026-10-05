"""Retriever variants behind one interface: build(chunks) then search(query, k).

`tfidf` is the production implementation (app.ai.rag.DocumentStore) and is the
baseline every other variant is compared against.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
import snowballstemmer
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.ai.rag import Chunk, DocumentStore

from .corpus import BACKEND_DIR, EVAL_DIR

_TOKEN = re.compile(r"(?u)\b\w\w+\b")
_STEMMER = snowballstemmer.stemmer("english")
CACHE_DIR = EVAL_DIR / ".cache"
EMBEDDING_MODEL = "gemini-embedding-001"


def tokenize(text: str, stem: bool) -> list[str]:
    tokens = [t for t in _TOKEN.findall(text.lower()) if t not in ENGLISH_STOP_WORDS]
    return _STEMMER.stemWords(tokens) if stem else tokens


class Retriever(ABC):
    name: str

    @abstractmethod
    def build(self, chunks: list[Chunk]) -> None: ...

    @abstractmethod
    def search(self, query: str, k: int) -> list[Chunk]: ...


class ProductionTfidf(Retriever):
    """The retriever the application ships: sklearn TF-IDF over raw tokens."""

    name = "tfidf"

    def build(self, chunks: list[Chunk]) -> None:
        self._store = DocumentStore()
        self._store.chunks = list(chunks)
        self._store._invalidate()

    def search(self, query: str, k: int) -> list[Chunk]:
        return self._store.search(query, top_k=k)


class StemmedTfidf(Retriever):
    name = "tfidf_stem"

    def build(self, chunks: list[Chunk]) -> None:
        self._chunks = list(chunks)
        self._vec = TfidfVectorizer(analyzer=lambda t: tokenize(t, stem=True))
        self._matrix = self._vec.fit_transform([c.text for c in chunks])

    def search(self, query: str, k: int) -> list[Chunk]:
        sims = cosine_similarity(self._vec.transform([query]), self._matrix)[0]
        order = np.argsort(-sims, kind="stable")
        return [self._chunks[i] for i in order if sims[i] > 0][:k]


class Bm25(Retriever):
    def __init__(self, stem: bool) -> None:
        self._stem = stem
        self.name = "bm25_stem" if stem else "bm25"

    def build(self, chunks: list[Chunk]) -> None:
        self._chunks = list(chunks)
        self._bm25 = BM25Okapi([tokenize(c.text, self._stem) for c in chunks])

    def search(self, query: str, k: int) -> list[Chunk]:
        scores = self._bm25.get_scores(tokenize(query, self._stem))
        order = np.argsort(-scores, kind="stable")
        return [self._chunks[i] for i in order if scores[i] > 0][:k]


class GeminiEmbeddings(Retriever):
    """Dense retrieval with Gemini embeddings. Vectors are cached on disk so a
    re-run costs no API calls."""

    name = "embeddings"

    def __init__(self) -> None:
        self._cache_path = CACHE_DIR / f"{EMBEDDING_MODEL}.json"
        self._cache: dict[str, list[float]] = (
            json.loads(self._cache_path.read_text()) if self._cache_path.exists() else {}
        )
        self._client = None

    def _embed(self, texts: list[str], task_type: str) -> np.ndarray:
        keys = [hashlib.sha256(f"{task_type}|{t}".encode()).hexdigest() for t in texts]
        missing = [(k, t) for k, t in zip(keys, texts) if k not in self._cache]
        if missing:
            from google import genai
            from google.genai import types

            load_dotenv(BACKEND_DIR / ".env")
            if self._client is None:
                self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            for start in range(0, len(missing), 50):
                batch = missing[start : start + 50]
                response = self._client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=[t for _, t in batch],
                    config=types.EmbedContentConfig(task_type=task_type),
                )
                for (key, _), emb in zip(batch, response.embeddings):
                    self._cache[key] = list(emb.values)
            CACHE_DIR.mkdir(exist_ok=True)
            self._cache_path.write_text(json.dumps(self._cache))
        return np.array([self._cache[k] for k in keys])

    def build(self, chunks: list[Chunk]) -> None:
        self._chunks = list(chunks)
        self._matrix = self._embed([c.text for c in chunks], "RETRIEVAL_DOCUMENT")

    def search(self, query: str, k: int) -> list[Chunk]:
        q = self._embed([query], "RETRIEVAL_QUERY")
        sims = cosine_similarity(q, self._matrix)[0]
        order = np.argsort(-sims, kind="stable")[:k]
        return [self._chunks[i] for i in order]


def all_retrievers(include_embeddings: bool = True) -> list[Retriever]:
    retrievers: list[Retriever] = [ProductionTfidf(), StemmedTfidf(), Bm25(stem=False), Bm25(stem=True)]
    if include_embeddings:
        retrievers.append(GeminiEmbeddings())
    return retrievers
