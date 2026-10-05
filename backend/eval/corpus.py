"""Loads the evaluation corpus and chunks it with the production chunker, so
retrieval is measured on exactly the units the application would index."""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.ai.rag import Chunk, chunk_text

EVAL_DIR = Path(__file__).resolve().parent
BACKEND_DIR = EVAL_DIR.parent
DATA_DIR = EVAL_DIR / "data"
CORPUS_DIRS = [BACKEND_DIR / "data" / "sample_docs", DATA_DIR / "corpus"]

_WS = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Lowercase and collapse whitespace so hard-wrapped markdown still matches."""
    return _WS.sub(" ", text).strip().lower()


def load_docs() -> dict[str, str]:
    docs: dict[str, str] = {}
    for directory in CORPUS_DIRS:
        for path in sorted(directory.glob("*.md")):
            if path.name in docs:
                raise ValueError(f"duplicate document name: {path.name}")
            docs[path.name] = path.read_text(encoding="utf-8")
    return docs


def build_chunks(docs: dict[str, str]) -> list[Chunk]:
    chunks: list[Chunk] = []
    for name, text in docs.items():
        for i, piece in enumerate(chunk_text(text)):
            chunks.append(Chunk(doc_name=name, doc_type="eval", chunk_id=i, text=piece))
    return chunks


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
