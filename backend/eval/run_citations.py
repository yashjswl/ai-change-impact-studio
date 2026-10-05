"""Citation verifier evaluation.

Each case is an (excerpt, cited document) pair labeled valid or invalid by
construction (see make_citation_cases.py). A verifier predicts "verified" or
not against the full text of the cited document. Positive class = valid.

  python -m eval.run_citations --split dev     # tune thresholds here
  python -m eval.run_citations --split test    # report
"""

from __future__ import annotations

import argparse
import datetime
import json
from collections import defaultdict
from typing import Callable

from app.ai import citation_verify

from .corpus import DATA_DIR, EVAL_DIR, load_docs, load_jsonl
from .metrics import precision_recall_f1, wilson_interval

Verifier = Callable[[str, str, float], bool]

THRESHOLDS = [round(0.50 + 0.05 * i, 2) for i in range(11)]
PRODUCTION_THRESHOLD = 0.85


def verifiers() -> dict[str, Verifier]:
    """Verifier generations, oldest first. The last one is what production runs."""
    return {
        "contiguous_shipped": lambda ex, src, th: citation_verify.verify_citation_contiguous(ex, src, threshold=th)[0],
        "contiguous_autojunk_off": lambda ex, src, th: citation_verify.verify_citation_contiguous(
            ex, src, threshold=th, autojunk=False
        )[0],
        "token_window_lenient": lambda ex, src, th: citation_verify.verify_citation_tokens(
            ex, src, threshold=th, strict_numbers=False
        )[0],
        "token_window": lambda ex, src, th: citation_verify.verify_citation_tokens(ex, src, threshold=th)[0],
    }


def confusion(cases: list[dict], docs: dict[str, str], verify: Verifier, threshold: float) -> tuple[int, int, int, int, list[dict]]:
    tp = fp = fn = tn = 0
    rows = []
    for c in cases:
        predicted_valid = verify(c["excerpt"], docs[c["source_doc"]], threshold)
        actual_valid = c["label"] == "valid"
        if predicted_valid and actual_valid:
            tp += 1
        elif predicted_valid and not actual_valid:
            fp += 1
        elif not predicted_valid and actual_valid:
            fn += 1
        else:
            tn += 1
        rows.append({"id": c["id"], "kind": c["kind"], "label": c["label"], "predicted_valid": predicted_valid})
    return tp, fp, fn, tn, rows


def evaluate(cases: list[dict], docs: dict[str, str], verify: Verifier, threshold: float) -> dict:
    tp, fp, fn, tn, rows = confusion(cases, docs, verify, threshold)
    metrics = precision_recall_f1(tp, fp, fn)
    n = tp + fp + fn + tn
    acc_lo, acc_hi = wilson_interval(tp + tn, n)
    by_kind: dict[str, dict] = {}
    grouped: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        grouped[r["kind"]].append(r)
    for kind, rs in sorted(grouped.items()):
        correct = sum(1 for r in rs if r["predicted_valid"] == (r["label"] == "valid"))
        lo, hi = wilson_interval(correct, len(rs))
        by_kind[kind] = {"label": rs[0]["label"], "n": len(rs), "correct": correct, "accuracy": correct / len(rs), "ci": [lo, hi]}
    return {
        "threshold": threshold,
        "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        **metrics,
        "accuracy": (tp + tn) / n,
        "accuracy_ci": [acc_lo, acc_hi],
        "by_kind": by_kind,
        "errors": [r for r in rows if r["predicted_valid"] != (r["label"] == "valid")],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["dev", "test", "all"], default="dev")
    args = parser.parse_args()

    docs = load_docs()
    cases = [c for c in load_jsonl(DATA_DIR / "citations.jsonl") if args.split in ("all", c["split"])]
    n_valid = sum(1 for c in cases if c["label"] == "valid")
    results: dict = {
        "meta": {
            "date": datetime.date.today().isoformat(),
            "split": args.split,
            "n_cases": len(cases),
            "n_valid": n_valid,
            "n_invalid": len(cases) - n_valid,
            "production_threshold": PRODUCTION_THRESHOLD,
        },
        "verifiers": {},
    }

    print(f"\nsplit={args.split}  cases={len(cases)} (valid={n_valid}, invalid={len(cases) - n_valid})")
    for name, verify in verifiers().items():
        at_prod = evaluate(cases, docs, verify, PRODUCTION_THRESHOLD)
        sweep = [evaluate(cases, docs, verify, th) for th in THRESHOLDS]
        results["verifiers"][name] = {
            "at_production_threshold": at_prod,
            "sweep": [{k: v for k, v in s.items() if k in ("threshold", "precision", "recall", "f1", "accuracy")} for s in sweep],
        }
        cf = at_prod["confusion"]
        print(f"\n== {name} @ threshold {PRODUCTION_THRESHOLD}")
        print(f'precision {at_prod["precision"]:.2f}  recall {at_prod["recall"]:.2f}  f1 {at_prod["f1"]:.2f}  '
              f'accuracy {at_prod["accuracy"]:.2f} [{at_prod["accuracy_ci"][0]:.2f},{at_prod["accuracy_ci"][1]:.2f}]  '
              f'(tp={cf["tp"]} fp={cf["fp"]} fn={cf["fn"]} tn={cf["tn"]})')
        print(f'{"kind":<16} {"label":<8} {"n":<4} {"correct":<8} accuracy [95% CI]')
        for kind, s in at_prod["by_kind"].items():
            print(f'{kind:<16} {s["label"]:<8} {s["n"]:<4} {s["correct"]:<8} {s["accuracy"]:.2f} [{s["ci"][0]:.2f},{s["ci"][1]:.2f}]')
        print("threshold sweep (precision / recall / f1):")
        print("  " + "  ".join(f'{s["threshold"]:.2f}:{s["precision"]:.2f}/{s["recall"]:.2f}/{s["f1"]:.2f}' for s in sweep))

    out_dir = EVAL_DIR / "results"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"citations_{args.split}.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
