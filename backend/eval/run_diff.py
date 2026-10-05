"""End-to-end check of the document-comparison task on real Gemini output.

For each old/new document pair this runs the same pipeline the API runs
(retrieve, build context, structured LLM call), then reports:
  - recall of known changes (see data/gold_changes.json for the matching rule)
  - how many returned citations verify, under the shipped and the current verifier
  - the citations the two verifiers disagree on, for manual inspection

It calls the Gemini API, so it only runs with --live.

  python -m eval.run_diff --live --runs 3
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import time

from dotenv import load_dotenv

from .corpus import BACKEND_DIR, DATA_DIR, EVAL_DIR, load_docs

load_dotenv(BACKEND_DIR / ".env")  # must precede importing app.ai.llm, which reads env at import

from app.ai import citation_verify, generation, llm  # noqa: E402
from app.ai.rag import DocumentStore  # noqa: E402

QUESTION = "What changed between the old and new processes?"


def covered_changes(findings, changes) -> list[str]:
    texts = [f"{f.topic} {f.old_state} {f.new_state}".lower() for f in findings]
    covered = []
    for change in changes:
        need = math.ceil(0.6 * len(change["keywords"]))
        if any(sum(1 for k in change["keywords"] if k.lower() in t) >= need for t in texts):
            covered.append(change["id"])
    return covered


def keywords_present(text: str, change: dict) -> bool:
    need = math.ceil(0.6 * len(change["keywords"]))
    lowered = text.lower()
    return sum(1 for k in change["keywords"] if k.lower() in lowered) >= need


def run_once(scenario: dict, docs: dict[str, str], mode: str) -> dict:
    # "retrieved" is the previous behavior: project-scoped store, top_k=10.
    # "full" passes every chunk of both documents, which services/diff_service.py
    # now does for corpora of up to 40 chunks.
    store = DocumentStore()
    store.add_document(scenario["old_doc"], "old_process", docs[scenario["old_doc"]])
    store.add_document(scenario["new_doc"], "new_process", docs[scenario["new_doc"]])
    chunks = store.search(QUESTION, top_k=10) if mode == "retrieved" else list(store.chunks)
    context = store.format_context(chunks)
    context_available = [c["id"] for c in scenario["changes"] if keywords_present(context, c)]
    # services/diff_service.py verifies each citation against the cited document's full text.
    source_text = {name: docs[name] for name in (scenario["old_doc"], scenario["new_doc"])}

    started = time.time()
    result = generation.analyze_document_diff(QUESTION, context)
    latency = time.time() - started

    covered = covered_changes(result.findings, scenario["changes"])
    citations = []
    for finding in result.findings:
        for cit in finding.citations:
            src = source_text.get(cit.source, "")
            shipped, _ = citation_verify.verify_citation_contiguous(cit.excerpt, src)
            current, note = citation_verify.verify_citation(cit.excerpt, src)
            citations.append({"source": cit.source, "excerpt": cit.excerpt, "shipped": shipped, "current": current, "note": note})
    return {
        "scenario": scenario["name"],
        "n_findings": len(result.findings),
        "chunks_in_context": len(chunks),
        "chunks_total": len(store.chunks),
        "context_availability": len(context_available) / len(scenario["changes"]),
        "recall": len(covered) / len(scenario["changes"]),
        "covered": covered,
        "missed": [c["id"] for c in scenario["changes"] if c["id"] not in covered],
        "latency_s": round(latency, 1),
        "findings": [{"topic": f.topic, "old_state": f.old_state, "new_state": f.new_state} for f in result.findings],
        "n_citations": len(citations),
        "verified_shipped": sum(c["shipped"] for c in citations),
        "verified_current": sum(c["current"] for c in citations),
        "citations": citations,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="required: this calls the Gemini API")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--context", choices=["retrieved", "full"], default="retrieved")
    parser.add_argument("--sleep", type=float, default=6.0, help="seconds between calls, to stay under the free-tier rate limit")
    args = parser.parse_args()
    if not args.live:
        print("Refusing to call the Gemini API without --live.")
        return

    docs = load_docs()
    gold = json.loads((DATA_DIR / "gold_changes.json").read_text())
    runs, failures = [], 0
    for scenario in gold["scenarios"]:
        for i in range(args.runs):
            try:
                row = run_once(scenario, docs, args.context)
                row["run"] = i + 1
                runs.append(row)
                print(f'{scenario["name"]:<11} run {i + 1}: ctx={row["chunks_in_context"]}/{row["chunks_total"]} '
                      f'findings={row["n_findings"]:<2} recall={row["recall"]:.2f} '
                      f'citations={row["n_citations"]:<3} verified shipped/current={row["verified_shipped"]}/{row["verified_current"]} '
                      f'({row["latency_s"]}s)')
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f'{scenario["name"]:<11} run {i + 1}: FAILED {str(exc)[:160]}')
            time.sleep(args.sleep)

    def mean(xs):
        return sum(xs) / len(xs) if xs else 0.0

    total_cit = sum(r["n_citations"] for r in runs)
    summary = {
        "model": llm.DEFAULT_MODEL,
        "date": datetime.date.today().isoformat(),
        "context_mode": args.context,
        "runs_attempted": len(gold["scenarios"]) * args.runs,
        "runs_failed": failures,
        "mean_chunks_in_context": mean([r["chunks_in_context"] for r in runs]),
        "mean_chunks_total": mean([r["chunks_total"] for r in runs]),
        "mean_context_availability": mean([r["context_availability"] for r in runs]),
        "mean_findings": mean([r["n_findings"] for r in runs]),
        "mean_recall": mean([r["recall"] for r in runs]),
        "per_scenario_recall": {
            s["name"]: mean([r["recall"] for r in runs if r["scenario"] == s["name"]]) for s in gold["scenarios"]
        },
        "total_citations": total_cit,
        "verified_rate_shipped": sum(r["verified_shipped"] for r in runs) / total_cit if total_cit else 0.0,
        "verified_rate_current": sum(r["verified_current"] for r in runs) / total_cit if total_cit else 0.0,
        "mean_latency_s": mean([r["latency_s"] for r in runs]),
    }
    disagreements = [
        {"scenario": r["scenario"], **c} for r in runs for c in r["citations"] if c["shipped"] != c["current"]
    ]
    still_unverified = [{"scenario": r["scenario"], **c} for r in runs for c in r["citations"] if not c["current"]]

    print("\nsummary:", json.dumps(summary, indent=2))
    print(f"\nshipped vs current disagree on {len(disagreements)} citation(s):")
    for d in disagreements:
        print(f'  [{d["scenario"]}] shipped={d["shipped"]} current={d["current"]} :: {d["excerpt"][:110]!r}')
    print(f"\ncitations still unverified under the current verifier: {len(still_unverified)}")
    for d in still_unverified:
        print(f'  [{d["scenario"]}] {d["note"]} :: {d["excerpt"][:110]!r}')

    out_dir = EVAL_DIR / "results"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"diff_live_{args.context}.json"
    out.write_text(
        json.dumps({"summary": summary, "runs": runs, "disagreements": disagreements, "still_unverified": still_unverified}, indent=2)
    )
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
