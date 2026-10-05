"""Checks that the evaluation labels are internally consistent.

Run:  python -m eval.validate_labels
Exits non-zero if any label is wrong, so a typo in a gold span cannot silently
turn into a retrieval "miss".
"""

from __future__ import annotations

import re
import sys

from .corpus import DATA_DIR, build_chunks, load_docs, load_jsonl, normalize
from .metrics import covers

MAX_SPAN_CHARS = 150  # must be <= chunk overlap so a span always fits inside one chunk
_MARKER = re.compile(r"^(?:\d+\.\s+|[-*]\s+)")


def main() -> int:
    docs = load_docs()
    norm_docs = {name: normalize(text) for name, text in docs.items()}
    chunks = build_chunks(docs)
    errors: list[str] = []

    questions = load_jsonl(DATA_DIR / "questions.jsonl")
    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        errors.append("duplicate question ids")

    for q in questions:
        if q["split"] not in ("dev", "test"):
            errors.append(f'{q["id"]}: bad split {q["split"]!r}')
        if not q["gold"]:
            errors.append(f'{q["id"]}: no gold spans')
        for g in q["gold"]:
            if g["doc"] not in docs:
                errors.append(f'{q["id"]}: unknown doc {g["doc"]}')
                continue
            if len(g["span"]) > MAX_SPAN_CHARS:
                errors.append(f'{q["id"]}: span longer than {MAX_SPAN_CHARS} chars')
            if normalize(g["span"]) not in norm_docs[g["doc"]]:
                errors.append(f'{q["id"]}: span not found in {g["doc"]}: {g["span"]!r}')
            elif not any(covers(c, g) for c in chunks):
                errors.append(f'{q["id"]}: span not contained in any single chunk: {g["span"]!r}')

    cases = load_jsonl(DATA_DIR / "citations.jsonl")
    if len({c["id"] for c in cases}) != len(cases):
        errors.append("duplicate citation ids")

    for c in cases:
        if c.get("split") not in ("dev", "test"):
            errors.append(f'{c["id"]}: bad split {c.get("split")!r}')
        if c["source_doc"] not in docs:
            errors.append(f'{c["id"]}: unknown source_doc {c["source_doc"]}')
            continue
        source = norm_docs[c["source_doc"]]
        excerpt = normalize(c["excerpt"])
        in_source = excerpt in source
        kind = c["kind"]
        if kind == "verbatim" and not in_source:
            errors.append(f'{c["id"]}: verbatim excerpt not in {c["source_doc"]}')
        elif kind == "marker_added":
            stripped = normalize(_MARKER.sub("", c["excerpt"]))
            if stripped not in source:
                errors.append(f'{c["id"]}: marker_added base text not in {c["source_doc"]}')
        elif kind in ("one_word_edit", "wrong_source", "fabricated", "paraphrase", "number_edit") and in_source:
            errors.append(f'{c["id"]}: {kind} excerpt unexpectedly appears verbatim in {c["source_doc"]}')
        if kind == "wrong_source" and not any(excerpt in text for name, text in norm_docs.items() if name != c["source_doc"]):
            errors.append(f'{c["id"]}: wrong_source excerpt is not from any other document')
        if (c["label"] == "valid") != (kind in ("verbatim", "marker_added", "one_word_edit")):
            errors.append(f'{c["id"]}: label {c["label"]!r} inconsistent with kind {kind!r}')

    if errors:
        print(f"{len(errors)} label problem(s):")
        for e in errors:
            print(" -", e)
        return 1
    print(f"OK: {len(docs)} docs, {len(chunks)} chunks, {len(questions)} questions, {len(cases)} citation cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
