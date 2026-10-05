"""Prints the README results tables as markdown, straight from results/*.json,
so the published numbers cannot drift from the committed result files.

  python -m eval.report
"""

from __future__ import annotations

import json

from .corpus import EVAL_DIR

RESULTS = EVAL_DIR / "results"


def load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text())


def ci(metric: dict) -> str:
    lo, hi = metric["ci"]
    return f'{metric["value"]:.2f} ({lo:.2f} to {hi:.2f})'


def retrieval_table() -> str:
    data = load("retrieval_test.json")
    meta = data["meta"]
    lines = [
        f'Held-out test split: {meta["n_questions"]} questions over {meta["n_chunks"]} chunks from {meta["n_docs"]} documents. 95% intervals in brackets.',
        "",
        "| Retriever | hit@1 | hit@3 | hit@5 | MRR@10 |",
        "|---|---|---|---|---|",
    ]
    c = data["chance"]
    lines.append(f'| Random ranking (expected) | {c["hit@1"]:.2f} | {c["hit@3"]:.2f} | {c["hit@5"]:.2f} | n/a |')
    labels = {
        "tfidf": "TF-IDF (shipped)",
        "tfidf_stem": "TF-IDF + stemming",
        "bm25": "BM25",
        "bm25_stem": "BM25 + stemming",
        "embeddings": "Gemini embeddings",
    }
    for key, label in labels.items():
        o = data["variants"][key]["overall"]
        lines.append(f'| {label} | {ci(o["hit@1"])} | {ci(o["hit@3"])} | {ci(o["hit@5"])} | {ci(o["mrr@10"])} |')
    lines += ["", "Paired change versus the shipped TF-IDF on the same questions (mean per-question difference, 95% bootstrap interval):", ""]
    lines += ["| Retriever | hit@5 | MRR@10 |", "|---|---|---|"]
    for key in ("tfidf_stem", "bm25", "bm25_stem", "embeddings"):
        p = data["paired_vs_tfidf"][key]
        cells = [f'{p[m]["mean_diff"]:+.2f} ({p[m]["ci"][0]:+.2f} to {p[m]["ci"][1]:+.2f})' for m in ("hit@5", "rr")]
        lines.append(f"| {labels[key]} | {cells[0]} | {cells[1]} |")
    dev = load("retrieval_dev.json")["paired_vs_tfidf"]["tfidf_stem"]["rr"]
    lines += [
        "",
        f'On the dev split, stemming looked helpful (MRR@10 {dev["mean_diff"]:+.2f}, interval {dev["ci"][0]:+.2f} to {dev["ci"][1]:+.2f}); that did not hold on the test split.',
    ]
    return "\n".join(lines)


def citation_table() -> str:
    data = load("citations_test.json")
    meta = data["meta"]
    lines = [
        f'Held-out test split: {meta["n_cases"]} labeled citations ({meta["n_valid"]} valid, {meta["n_invalid"]} invalid), threshold {meta["production_threshold"]}.',
        "",
        "| Verifier | Precision | Recall | F1 | Altered numbers accepted |",
        "|---|---|---|---|---|",
    ]
    labels = {
        "contiguous_shipped": "Character-level, longest block (originally shipped)",
        "contiguous_autojunk_off": "Same, with difflib autojunk disabled",
        "token_window_lenient": "Word-level window, numbers not checked",
        "token_window": "Word-level window, numbers must match (current)",
    }
    for key, label in labels.items():
        r = data["verifiers"][key]["at_production_threshold"]
        ne = r["by_kind"]["number_edit"]
        lines.append(
            f'| {label} | {r["precision"]:.2f} | {r["recall"]:.2f} | {r["f1"]:.2f} | {ne["n"] - ne["correct"]} of {ne["n"]} |'
        )
    return "\n".join(lines)


def diff_table() -> str:
    retrieved = load("diff_live_retrieved.json")["summary"]
    full = load("diff_live_full.json")["summary"]
    lines = [
        f'Real {retrieved["model"]} output, {retrieved["runs_attempted"]} runs per row (5 scenarios x 3 runs), run {full["date"]}.',
        "",
        "| Context given to the model | Chunks in context | Known changes with evidence present | Findings returned | Recall of known changes | Runs failed |",
        "|---|---|---|---|---|---|",
    ]
    for label, s in (("Retrieval only (previous behavior)", retrieved), ("Full documents (now used for small corpora)", full)):
        lines.append(
            f'| {label} | {s["mean_chunks_in_context"]:.1f} of {s["mean_chunks_total"]:.1f} | {s["mean_context_availability"]:.0%} '
            f'| {s["mean_findings"]:.1f} | {s["mean_recall"]:.2f} | {s["runs_failed"]} of {s["runs_attempted"]} |'
        )
    lines += ["", "Recall by scenario:", "", "| Scenario | Retrieval only | Full documents |", "|---|---|---|"]
    for name in retrieved["per_scenario_recall"]:
        lines.append(f'| {name} | {retrieved["per_scenario_recall"][name]:.2f} | {full["per_scenario_recall"][name]:.2f} |')
    lines += [
        "",
        f'Citations returned by the model that the verifier accepts: {full["verified_rate_current"]:.1%} with the current word-level verifier versus '
        f'{full["verified_rate_shipped"]:.1%} with the earlier character-level one, both checked against the cited document\'s full text '
        f'({full["total_citations"]} citations, full-document runs). The model quotes accurately most of the time, so the gap on real output is small; '
        f'the labeled citation test above is where the verifiers differ.',
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    for title, body in (("Retrieval", retrieval_table()), ("Citation verification", citation_table()), ("Document comparison (end to end)", diff_table())):
        print(f"### {title}\n\n{body}\n")
