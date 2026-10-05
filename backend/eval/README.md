# Evaluation

Measures the retrieval, citation verification and document-comparison parts of the application. Results are in `results/`; `python -m eval.report` prints them as the tables used in the root README.

ADKAR scoring is **not** evaluated. It is an LLM judgment with no ground truth, so any accuracy figure for it would be invented.

## Reproduce

```bash
cd backend
pip install -r requirements.txt -r requirements-eval.txt
python -m eval.validate_labels                       # label consistency checks
python -m eval.run_retrieval --split dev             # explore
python -m eval.run_retrieval --split test            # report
python -m eval.run_citations --split test
python -m eval.run_diff --live --runs 3 --context retrieved   # calls Gemini
python -m eval.run_diff --live --runs 3 --context full        # calls Gemini
python -m eval.report
```

`run_retrieval` with the embeddings variant needs `GEMINI_API_KEY` in `backend/.env`; add `--no-embeddings` to skip it. Embedding vectors are cached in `eval/.cache/` (gitignored). `run_diff` only runs with `--live` because it spends API quota.

## Data

| File | Contents |
|---|---|
| `data/corpus/*.md` + `../data/sample_docs/*.md` | 12 documents, 35 chunks at the production chunker settings (900 characters, 150 overlap). Four new scenarios (expense, vendor, incident, refund), each with an old and a new document, plus the original onboarding documents. |
| `data/questions.jsonl` | 42 questions, each with one or more gold evidence spans. Types: factual (25), lexical mismatch (9), change (5), multi-evidence (3). Fixed split: 16 dev, 26 test. |
| `data/citations.jsonl` | 74 labeled citations (30 valid, 44 invalid), fixed split 37 dev, 37 test. |
| `data/gold_changes.json` | The known differences for each old/new pair, with the keyword rule used to score the live comparison. |

**Gold labels are evidence spans, not chunk indexes.** A retrieved chunk counts as a hit when it comes from the right document and contains the span (case and whitespace ignored), so the labels stay valid if the chunking changes. `validate_labels.py` fails if any span is missing from its document, too long to fit in one chunk, or if a citation case is mislabeled.

**Citation labels are assigned by construction.** Valid: verbatim sentences, sentences with a list marker added, sentences with one word changed by one character. Invalid: sentences attributed to the wrong document, fabricated sentences, paraphrases, and real sentences with one number altered. The application asks the model for verbatim excerpts, so a paraphrase counts as invalid even though it is not a hallucination.

## Method

- **Dev and test splits.** Variants were compared and the decision rule was fixed on dev. The test split was then run once, before any production change. No parameter was tuned on test.
- **Adoption rule, fixed before looking at test:** adopt stemming only if the paired MRR@10 gain over the shipped TF-IDF has a 95% interval that excludes zero on test, with no drop in hit@5. It did not, so retrieval was left unchanged.
- **Paired comparison.** Variants are compared on the same questions using a bootstrap over per-question differences, which is more sensitive than checking whether two separate intervals overlap.
- **Intervals.** Wilson intervals for proportions, percentile bootstrap (2,000 resamples, fixed seed) for means.
- **Chance level.** The random-ranking row is the exact expected hit@k given how many chunks cover each question's evidence.

## Limitations

- The corpus is synthetic and was written with LLM assistance. It is not real enterprise documentation, and the questions share more vocabulary with the documents than real queries would, which favors lexical retrievers.
- One annotator. The labels have not been independently reviewed.
- Small samples (26 test questions, 37 test citations). Intervals are wide, and several differences between retrievers are inside the noise.
- The citation cases were built to probe specific behaviors. Real model errors are subtler, so a perfect score here does not mean the verifier is perfect in use.
- The retrieval index is global across all 12 documents, which is harder than the application's per-project index. In the application, a single project's corpus is small enough that retrieval rarely filters anything, which is why the comparison task now passes whole documents to the model.
- The embeddings variant uses the same vendor family as the generator.
- The live comparison depends on the model behind the `gemini-flash-lite-latest` alias, which changes over time, and on sampling randomness. Treat a single run as one draw. Its recall score uses a keyword rule that is slightly generous in places (for example a finding about audit sampling earned credit for duplicate controls), so it is a proxy, not a human judgment. One manual audit of two scenario runs found the missed changes were genuine omissions rather than matcher strictness.
