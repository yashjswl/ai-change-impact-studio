from app.ai.citation_verify import verify_citation


def test_exact_substring_verified():
    source = "The system automatically routes approvals to the manager within 2 days."
    verified, note = verify_citation("automatically routes approvals to the manager", source)
    assert verified
    assert note is None


def test_whitespace_and_case_insensitive():
    source = "Old   process   required   manual   entry.\nNew process is automated."
    verified, note = verify_citation("old process required manual entry", source)
    assert verified


def test_unrelated_excerpt_not_verified():
    source = "The onboarding workflow triggers automatically when an offer is accepted."
    verified, note = verify_citation("Finance manually re-keys data into payroll", source)
    assert not verified
    assert note is not None


def test_empty_excerpt_not_verified():
    verified, note = verify_citation("", "some source text")
    assert not verified
