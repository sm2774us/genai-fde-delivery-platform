"""Hybrid retrieval: BM25 (lexical) + dense vector similarity, fused with
reciprocal rank fusion (RRF). This is the retrieval pattern the JD calls out
explicitly ("hybrid search") because pure-vector retrieval underperforms on
exact-match/keyword-heavy enterprise queries (IDs, error codes, names)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from rank_bm25 import BM25Okapi

from app.rag.chunking import Chunk
from app.rag.embeddings import Embedder


@dataclass
class RetrievalResult:
    chunk: Chunk
    score: float
    lexical_rank: int | None
    vector_rank: int | None


class HybridIndex:
    def __init__(self, embedder: Embedder):
        self.embedder = embedder
        self.chunks: list[Chunk] = []
        self._bm25: BM25Okapi | None = None
        self._vectors: np.ndarray | None = None

    def build(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        tokenized = [c.text.lower().split() for c in chunks]
        self._bm25 = BM25Okapi(tokenized) if tokenized else None
        self._vectors = self.embedder.embed([c.text for c in chunks]) if chunks else None

    def search(self, query: str, top_k: int = 5, rrf_k: int = 60) -> list[RetrievalResult]:
        if not self.chunks or self._bm25 is None or self._vectors is None:
            return []

        lexical_scores = self._bm25.get_scores(query.lower().split())
        lexical_order = np.argsort(-lexical_scores)

        query_vec = self.embedder.embed([query])[0]
        vector_scores = self._vectors @ query_vec
        vector_order = np.argsort(-vector_scores)

        lex_rank = {idx: rank for rank, idx in enumerate(lexical_order)}
        vec_rank = {idx: rank for rank, idx in enumerate(vector_order)}

        fused_scores: dict[int, float] = {}
        for idx in range(len(self.chunks)):
            lr = lex_rank.get(idx, len(self.chunks))
            vr = vec_rank.get(idx, len(self.chunks))
            fused_scores[idx] = 1.0 / (rrf_k + lr + 1) + 1.0 / (rrf_k + vr + 1)

        ranked = sorted(fused_scores.items(), key=lambda kv: -kv[1])[:top_k]
        return [
            RetrievalResult(
                chunk=self.chunks[idx],
                score=score,
                lexical_rank=lex_rank.get(idx),
                vector_rank=vec_rank.get(idx),
            )
            for idx, score in ranked
        ]
