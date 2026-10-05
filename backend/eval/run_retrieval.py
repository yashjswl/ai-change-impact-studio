"""Retrieval evaluation: hit@k, recall@k and MRR for each retriever variant.

  python -m eval.run_retrieval --split dev          # explore and choose a variant
  python -m eval.run_retrieval --split test         # report (do not tune on this)
  python -m eval.run_retrieval --split test --no-embeddings   # skip API calls

Variants are compared on the same questions. A chance-level row shows what a
random ranker would score, so the numbers can be read against a floor.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
from collections import defaultdict

from .corpus import DATA_DIR, EVAL_DIR, build_chunks, load_docs, load_jsonl
from .metrics import (
    bootstrap_mean_ci,
    covers,
    hit_at_k,
    recall_at_k,
    reciprocal_rank,
    wilson_interval,
)
from .retrievers import Retriever, all_retrievers

KS = (1, 3, 5)
DEPTH = 10  # ranking depth used for MRR


def first_gold_rank(gold, ranked) -> int | None:
    for rank, chunk in enumerate(ranked, start=1):
        if any(covers(chunk, g) for g in gold):
            return rank
    return None


def run_variant(retriever: Retriever, questions: list[dict]) -> list[dict]:
    rows = []
    for q in questions:
        ranked = retriever.search(q["question"], DEPTH)
        rows.append(
            {
                "id": q["id"],
                "type": q["type"],
                "first_gold_rank": first_gold_rank(q["gold"], ranked),
                "top_docs": [f"{c.doc_name}#{c.chunk_id}" for c in ranked[:3]],
                "rr": reciprocal_rank(q["gold"], ranked),
                **{f"hit@{k}": hit_at_k(q["gold"], ranked, k) for k in KS},
                **{f"recall@{k}": recall_at_k(q["gold"], ranked, k) for k in KS},
            }
        )
    return rows


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    out: dict = {"n": n}
    for k in KS:
        hits = sum(r[f"hit@{k}"] for r in rows)
        lo, hi = wilson_interval(hits, n)
        out[f"hit@{k}"] = {"value": hits / n, "ci": [lo, hi]}
    lo, hi = bootstrap_mean_ci([r["recall@5"] for r in rows])
    out["recall@5"] = {"value": sum(r["recall@5"] for r in rows) / n, "ci": [lo, hi]}
    lo, hi = bootstrap_mean_ci([r["rr"] for r in rows])
    out["mrr@10"] = {"value": sum(r["rr"] for r in rows) / n, "ci": [lo, hi]}
    return out


def chance_hit_at_k(questions: list[dict], chunks, k: int) -> float:
    """Expected hit@k if chunks were ranked uniformly at random."""
    total = len(chunks)
    expected = 0.0
    for q in questions:
        g = sum(1 for c in chunks if any(covers(c, item) for item in q["gold"]))
        expected += 1 - math.comb(total - g, k) / math.comb(total, k)
    return expected / len(questions)


def fmt(metric: dict) -> str:
    lo, hi = metric["ci"]
    return f'{metric["value"]:.2f} [{lo:.2f},{hi:.2f}]'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["dev", "test", "all"], default="dev")
    parser.add_argument("--no-embeddings", action="store_true")
    args = parser.parse_args()

    docs = load_docs()
    chunks = build_chunks(docs)
    questions = [q for q in load_jsonl(DATA_DIR / "questions.jsonl") if args.split in ("all", q["split"])]

    results: dict = {
        "meta": {
            "date": datetime.date.today().isoformat(),
            "split": args.split,
            "n_questions": len(questions),
            "n_docs": len(docs),
            "n_chunks": len(chunks),
            "chunker": {"chunk_size": 900, "overlap": 150},
        },
        "chance": {f"hit@{k}": chance_hit_at_k(questions, chunks, k) for k in KS},
        "variants": {},
    }

    for retriever in all_retrievers(include_embeddings=not args.no_embeddings):
        retriever.build(chunks)
        rows = run_variant(retriever, questions)
        by_type: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            by_type[r["type"]].append(r)
        results["variants"][retriever.name] = {
            "overall": summarize(rows),
            "by_type": {t: summarize(rs) for t, rs in sorted(by_type.items())},
            "per_question": rows,
        }

    baseline_rows = {r["id"]: r for r in results["variants"]["tfidf"]["per_question"]}
    results["paired_vs_tfidf"] = {}
    for name, v in results["variants"].items():
        if name == "tfidf":
            continue
        paired = {}
        for metric in ("hit@1", "hit@5", "rr"):
            diffs = [r[metric] - baseline_rows[r["id"]][metric] for r in v["per_question"]]
            lo, hi = bootstrap_mean_ci(diffs)
            paired[metric] = {"mean_diff": sum(diffs) / len(diffs), "ci": [lo, hi]}
        results["paired_vs_tfidf"][name] = paired

    print(f'\nsplit={args.split}  questions={len(questions)}  chunks={len(chunks)}  (95% CIs in brackets)\n')
    header = f'{"variant":<12} {"hit@1":<18} {"hit@3":<18} {"hit@5":<18} {"recall@5":<18} {"mrr@10":<18}'
    print(header)
    print("-" * len(header))
    c = results["chance"]
    print(f'{"chance":<12} {c["hit@1"]:<18.2f} {c["hit@3"]:<18.2f} {c["hit@5"]:<18.2f}')
    for name, v in results["variants"].items():
        o = v["overall"]
        print(f'{name:<12} {fmt(o["hit@1"]):<18} {fmt(o["hit@3"]):<18} {fmt(o["hit@5"]):<18} '
              f'{fmt(o["recall@5"]):<18} {fmt(o["mrr@10"]):<18}')

    print("\npaired difference vs tfidf (mean per-question change, 95% bootstrap CI; CI containing 0 = inconclusive):")
    print(f'{"variant":<12} {"hit@1":<22} {"hit@5":<22} {"mrr@10":<22}')
    for name, paired in results["paired_vs_tfidf"].items():
        cells = [
            f'{paired[m]["mean_diff"]:+.2f} [{paired[m]["ci"][0]:+.2f},{paired[m]["ci"][1]:+.2f}]'
            for m in ("hit@1", "hit@5", "rr")
        ]
        print(f"{name:<12} " + " ".join(f"{cell:<22}" for cell in cells))

    print("\nhit@5 by question type (value, n):")
    types = sorted({r["type"] for r in results["variants"]["tfidf"]["per_question"]})
    print(f'{"variant":<12} ' + " ".join(f"{t:<20}" for t in types))
    for name, v in results["variants"].items():
        cells = [f'{v["by_type"][t]["hit@5"]["value"]:.2f} (n={v["by_type"][t]["n"]})' for t in types]
        print(f"{name:<12} " + " ".join(f"{cell:<20}" for cell in cells))

    for name in ("tfidf",):
        misses = [r for r in results["variants"][name]["per_question"] if r["hit@5"] == 0]
        print(f"\n{name} misses at k=5: {len(misses)}")
        qtext = {q["id"]: q["question"] for q in questions}
        for r in misses:
            print(f'  {r["id"]} [{r["type"]}] {qtext[r["id"]]!r} -> top: {r["top_docs"] or "no chunk retrieved"}')

    out_dir = EVAL_DIR / "results"
    out_dir.mkdir(exist_ok=True)
    suffix = "" if not args.no_embeddings else "_no_embeddings"
    out = out_dir / f"retrieval_{args.split}{suffix}.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
