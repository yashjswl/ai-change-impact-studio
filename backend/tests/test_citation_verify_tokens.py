from pathlib import Path

from app.ai.citation_verify import verify_citation, verify_citation_contiguous, verify_citation_tokens

# Longer than 200 characters on purpose: difflib's default autojunk heuristic
# only misbehaves on sequences of that size, which is how real documents look.
SOURCE = (
    "The meal limit is $75 per person per day and the hotel cap is $220 per night. "
    "A line that breaks a rule is flagged and the employee must add a justification before submitting. "
    "Claims under $200 with no policy flags are approved automatically with no manager involvement. "
    "Claims from $200 to $2,000 go to the line manager, who has 3 business days to respond."
)


def test_exact_quote_verifies():
    ok, note = verify_citation("Claims under $200 with no policy flags are approved automatically", SOURCE)
    assert ok and note is None


def test_added_list_marker_still_verifies_on_long_source():
    # The earlier character-level matcher rejected this kind of excerpt on real
    # documents (its autojunk heuristic collapses on long sources); the eval in
    # backend/eval measures that. This pins the current behavior.
    excerpt = "- Claims under $200 with no policy flags are approved automatically with no manager involvement."
    assert verify_citation(excerpt, SOURCE)[0]


def test_autojunk_defect_on_a_real_document():
    # difflib's default autojunk collapses the fuzzy match on sources over 200
    # characters, so a verbatim quote with a bullet prefix is rejected by the
    # earlier matcher. This reproduces it on a real sample document.
    policies = (Path(__file__).resolve().parents[1] / "data" / "sample_docs" / "company_policies.md").read_text()
    excerpt = "- Physical storage of documents containing SSN or bank details is discouraged and must be phased out by end of fiscal year."
    assert not verify_citation_contiguous(excerpt, policies)[0]
    assert verify_citation_contiguous(excerpt, policies, autojunk=False)[0]
    assert verify_citation(excerpt, policies)[0]


def test_one_word_edit_still_verifies():
    excerpt = "A line that breaks a rule is flagged and the employee must add a justification before submit."
    assert verify_citation(excerpt, SOURCE)[0]


def test_altered_number_is_rejected():
    excerpt = "The meal limit is $85 per person per day and the hotel cap is $220 per night."
    ok, note = verify_citation(excerpt, SOURCE)
    assert not ok
    assert "number" in note


def test_lenient_mode_accepts_altered_number():
    excerpt = "The meal limit is $85 per person per day and the hotel cap is $220 per night."
    assert verify_citation_tokens(excerpt, SOURCE, strict_numbers=False)[0]


def test_fabricated_and_paraphrased_excerpts_are_rejected():
    assert not verify_citation("Claims over $10,000 must be approved by the chief financial officer.", SOURCE)[0]
    assert not verify_citation("Small claims from compliant staff are cleared with no manager sign-off.", SOURCE)[0]


def test_empty_excerpt_is_rejected():
    assert verify_citation("   ", SOURCE) == (False, "empty excerpt")
