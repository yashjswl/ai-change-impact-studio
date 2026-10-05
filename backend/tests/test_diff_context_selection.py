from app.ai.rag import DocumentStore
from app.services.diff_service import FULL_CONTEXT_MAX_CHUNKS, select_context_chunks


def store_with_chunks(n_chunks: int) -> DocumentStore:
    store = DocumentStore()
    # chunk_text splits on a 900/150 window, so size each doc to yield several chunks
    text = ("word " * 180).strip()
    added = 0
    i = 0
    while added < n_chunks:
        added += store.add_document(f"doc{i}.md", "other", text)
        i += 1
    return store


def test_small_corpus_uses_every_chunk_in_order():
    store = store_with_chunks(10)
    selected = select_context_chunks(store, "what changed between the old and new processes?")
    assert len(selected) == len(store.chunks)
    assert selected == store.chunks


def test_corpus_at_the_limit_still_uses_every_chunk():
    store = store_with_chunks(FULL_CONTEXT_MAX_CHUNKS)
    assert len(store.chunks) <= FULL_CONTEXT_MAX_CHUNKS
    assert len(select_context_chunks(store, "anything")) == len(store.chunks)


def test_large_corpus_falls_back_to_retrieval():
    store = store_with_chunks(FULL_CONTEXT_MAX_CHUNKS + 30)
    assert len(store.chunks) > FULL_CONTEXT_MAX_CHUNKS
    selected = select_context_chunks(store, "word")
    assert 0 < len(selected) <= 10
