from app.rag.chunking import chunk_document
from app.rag.embeddings import HashingEmbedder
from app.rag.hybrid_search import HybridIndex


def test_hybrid_search_ranks_relevant_chunk_first():
    chunks = chunk_document("doc1", "apples oranges bananas " * 20 + " the risk score is high for gold tier")
    chunks += chunk_document("doc2", "completely unrelated text about weather and rain clouds " * 10)
    idx = HybridIndex(HashingEmbedder())
    idx.build(chunks)
    results = idx.search("risk score gold tier", top_k=2)
    assert results
    assert "risk" in results[0].chunk.text or "gold" in results[0].chunk.text


def test_empty_index_returns_no_results():
    idx = HybridIndex(HashingEmbedder())
    idx.build([])
    assert idx.search("anything") == []
