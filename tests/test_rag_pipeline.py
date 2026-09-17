from app.rag.pipeline import RagPipeline


def make_pipeline():
    p = RagPipeline()
    p.ingest([
        {"doc_id": "d1", "title": "Doc 1", "text": "The quick brown fox jumps over the lazy dog near the river bank."},
        {"doc_id": "d2", "title": "Doc 2", "text": "Customer risk scores are weighted by account tier gold silver bronze."},
    ])
    return p


def test_ingest_creates_chunks():
    p = make_pipeline()
    assert len(p.index.chunks) == 2


def test_answer_returns_citations():
    p = make_pipeline()
    result = p.answer("How are customer risk scores weighted?")
    assert result.citations
    assert any("d2" in c for c in result.citations)


def test_answer_with_empty_index_is_ungrounded():
    p = RagPipeline()
    result = p.answer("anything")
    assert result.grounded is False
