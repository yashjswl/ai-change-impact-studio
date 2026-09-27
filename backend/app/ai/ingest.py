"""Extracts plain text from uploaded files (txt/md/pdf) for ingestion into the
DocumentStore."""

from __future__ import annotations

import io


def extract_text(filename: str, raw_bytes: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(raw_bytes))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    return raw_bytes.decode("utf-8", errors="replace")
