"""Builds data/citations.jsonl, the labeled cases for the citation verifier.

Labels are assigned by construction, not by judgement:
  valid   verbatim          sentence copied exactly from the cited document
  valid   marker_added      same, with a list marker the model might add ("- ", "1. ")
  valid   one_word_edit     same, with one mid-sentence word changed by one character
  invalid wrong_source      a real sentence attributed to a different document
  invalid fabricated        a plausible sentence that appears in no document
  invalid paraphrase        a faithful restatement in different words (not a quote)
  invalid number_edit       a real sentence with one number changed (altered fact)

The application asks the model for verbatim excerpts, so a paraphrase counts as
invalid here even though it is not a hallucination. It is reported as its own
kind so the distinction stays visible.

Run:  python -m eval.make_citation_cases
"""

from __future__ import annotations

import json
import random
import re

from .corpus import DATA_DIR, load_docs

SEED = 7

PARAPHRASES = [
    ("Employees get repaid roughly a month or more after submitting a paper claim.", "expense_old.md"),
    ("A second manager has to countersign the affidavit for a lost receipt.", "expense_old.md"),
    ("The vendor returns the application by email alongside tax paperwork and a bank letter.", "vendor_old.md"),
    ("Contract expiries were never flagged ahead of time under the previous approach.", "vendor_old.md"),
    ("If nobody answers the page within five minutes it moves up to the backup engineer.", "incident_new.md"),
    ("Outages shorter than eight hours never received a formal write-up before.", "incident_old.md"),
    ("Small refunds for reliable customers are approved with no agent involvement.", "refund_new.md"),
    ("Customers had to wait about nine days for their money before the change.", "refund_old.md"),
    ("New starters receive their laptop and logins within two working days.", "new_process.md"),
    ("Compliance courses were allocated by word of mouth from the manager.", "old_process.md"),
    ("The cross-functional approval board must review changes touching several departments.", "company_policies.md"),
    ("Engineering was the first team to try the new workflow.", "implementation_plan.md"),
]

FABRICATED = [
    ("Claims over $10,000 must be approved by the chief financial officer.", "expense_new.md"),
    ("Receipts must be submitted within 14 days of the expense date.", "expense_new.md"),
    ("Tier 1 vendors must also provide proof of cyber insurance.", "vendor_new.md"),
    ("Vendors are re-validated every 6 months by the compliance team.", "vendor_new.md"),
    ("SEV3 incidents are paged to the engineering director.", "incident_new.md"),
    ("The incident commander writes the postmortem within 24 hours.", "incident_new.md"),
    ("Refunds above $500 are issued as store credit only.", "refund_new.md"),
    ("Customers can request a refund up to 60 days after delivery.", "refund_new.md"),
    ("HR must obtain written consent before ordering a laptop.", "new_process.md"),
    ("Mileage reimbursement is capped at 200 miles per month.", "expense_new.md"),
    ("The change advisory board meets every Monday at 9 a.m.", "company_policies.md"),
    ("The pilot department was Finance and ran for six weeks.", "implementation_plan.md"),
]

_LIST_MARKER = re.compile(r"^(?:\d+\.\s+|-\s+)")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def sentences(text: str) -> list[str]:
    out = []
    body = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    for line_block in body.split("\n\n"):
        collapsed = re.sub(r"\s+", " ", line_block).strip()
        for sent in _SENTENCE_SPLIT.split(collapsed):
            sent = _LIST_MARKER.sub("", sent).strip()
            if "**" in sent:
                continue
            if 55 <= len(sent) <= 170 and sent.endswith("."):
                out.append(sent)
    return out


def one_word_edit(sentence: str) -> str:
    words = sentence.split(" ")
    mid = len(words) // 2
    for offset in range(len(words)):
        i = (mid + offset) % len(words)
        core = re.sub(r"[^A-Za-z]", "", words[i])
        if len(core) >= 5 and words[i] == core:
            words[i] = core[:-1] if core.endswith("s") else core + "s"
            return " ".join(words)
    raise ValueError(f"no editable word in: {sentence}")


def number_edit(sentence: str) -> str:
    """Change the first integer in the sentence by +2, altering the claimed fact."""
    match = re.search(r"\d+", sentence)
    if match is None:
        raise ValueError(f"no number in: {sentence}")
    return sentence[: match.start()] + str(int(match.group()) + 2) + sentence[match.end() :]


def main() -> None:
    rng = random.Random(SEED)
    docs = load_docs()
    names = sorted(docs)
    pool: list[tuple[str, str]] = []
    for name in names:
        for sent in sentences(docs[name]):
            pool.append((name, sent))
    rng.shuffle(pool)

    def take(n: int) -> list[tuple[str, str]]:
        chosen, pool[:] = pool[:n], pool[n:]
        return chosen

    cases: list[dict] = []

    def add(excerpt: str, source_doc: str, label: str, kind: str) -> None:
        cases.append({"id": f"c{len(cases) + 1:02d}", "excerpt": excerpt, "source_doc": source_doc, "label": label, "kind": kind})

    for doc, sent in take(12):
        add(sent, doc, "valid", "verbatim")
    for i, (doc, sent) in enumerate(take(8)):
        marker = "- " if i % 2 == 0 else "* "
        add(marker + sent, doc, "valid", "marker_added")
    for doc, sent in take(10):
        add(one_word_edit(sent), doc, "valid", "one_word_edit")
    for doc, sent in take(10):
        other = names[(names.index(doc) + 1) % len(names)]
        add(sent, other, "invalid", "wrong_source")
    for excerpt, doc in FABRICATED:
        add(excerpt, doc, "invalid", "fabricated")
    for excerpt, doc in PARAPHRASES:
        add(excerpt, doc, "invalid", "paraphrase")
    # Hard negatives: a real sentence with one number altered. Added last so the
    # ids and sampling of every other kind stay stable.
    digit_pool = [p for p in pool if re.search(r"\d", p[1])]
    for doc, sent in digit_pool[:10]:
        add(number_edit(sent), doc, "invalid", "number_edit")

    seen_per_kind: dict[str, int] = {}
    for case in cases:  # alternate within each kind so dev and test are stratified
        i = seen_per_kind.get(case["kind"], 0)
        case["split"] = "dev" if i % 2 == 0 else "test"
        seen_per_kind[case["kind"]] = i + 1

    path = DATA_DIR / "citations.jsonl"
    path.write_text("\n".join(json.dumps(c) for c in cases) + "\n", encoding="utf-8")
    kinds = {}
    for c in cases:
        kinds[(c["label"], c["kind"])] = kinds.get((c["label"], c["kind"]), 0) + 1
    print(f"wrote {len(cases)} cases to {path}")
    for k, v in sorted(kinds.items()):
        print(" ", k, v)


if __name__ == "__main__":
    main()
