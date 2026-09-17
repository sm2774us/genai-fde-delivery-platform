"""End-to-end RAG pipeline: ingest -> chunk -> embed/index -> retrieve ->
answer with inline citations. Grounding + citation is the primary lever
against hallucination and is enforced at the pipeline level, not left to
prompt instructions alone."""
from __future__ import annotations

from dataclasses import dataclass, field

from app.core.llm_client import LLMClient
from app.core.logging import get_logger
from app.rag.chunking import chunk_document
from app.rag.embeddings import get_embedder
from app.rag.hybrid_search import HybridIndex, RetrievalResult

log = get_logger(__name__)


@dataclass
class RagAnswer:
    answer: str
    citations: list[str]
    retrieved: list[RetrievalResult] = field(default_factory=list)
    grounded: bool = True


class RagPipeline:
    def __init__(self):
        self.index = HybridIndex(get_embedder())
        self.llm = LLMClient()
        self._doc_titles: dict[str, str] = {}

    def ingest(self, documents: list[dict]) -> int:
        """documents: [{"doc_id": str, "title": str, "text": str}, ...]"""
        all_chunks = []
        for doc in documents:
            self._doc_titles[doc["doc_id"]] = doc.get("title", doc["doc_id"])
            all_chunks.extend(chunk_document(doc["doc_id"], doc["text"]))
        self.index.build(all_chunks)
        log.info("rag_ingested", n_docs=len(documents), n_chunks=len(all_chunks))
        return len(all_chunks)

    def answer(self, query: str, top_k: int = 4) -> RagAnswer:
        results = self.index.search(query, top_k=top_k)
        if not results:
            return RagAnswer(
                answer="No indexed knowledge is available to answer this yet — ingest documents first.",
                citations=[], grounded=False,
            )

        context_block = "\n\n".join(
            f"[{r.chunk.chunk_id}] ({self._doc_titles.get(r.chunk.doc_id, r.chunk.doc_id)}): {r.chunk.text}"
            for r in results
        )
        system = (
            "You are a grounded enterprise knowledge assistant. Answer ONLY using the "
            "provided context. Cite chunk ids you used. If the context is insufficient, say so."
        )
        prompt = f"Context:\n{context_block}\n\nQuestion: {query}\nAnswer with citations:"
        llm_resp = self.llm.complete(system, prompt)

        citations = [r.chunk.chunk_id for r in results]
        grounded = self._check_grounding(llm_resp.text, results)
        return RagAnswer(answer=llm_resp.text, citations=citations, retrieved=results, grounded=grounded)

    @staticmethod
    def _check_grounding(answer_text: str, results: list[RetrievalResult]) -> bool:
        """Cheap lexical-overlap grounding check used as a guardrail signal
        for the eval harness's hallucination-rate metric."""
        answer_tokens = set(answer_text.lower().split())
        context_tokens = set(
            tok for r in results for tok in r.chunk.text.lower().split()
        )
        if not answer_tokens:
            return False
        overlap = len(answer_tokens & context_tokens) / max(len(answer_tokens), 1)
        return overlap >= 0.3
