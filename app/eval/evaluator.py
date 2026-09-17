"""Per-example evaluator: runs the RAG pipeline against a labeled example and
scores quality, groundedness, latency, cost, and safety in one pass."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from app.eval.metrics import CostModel, groundedness_score, safety_flags, token_overlap_relevance
from app.rag.pipeline import RagPipeline


@dataclass
class EvalExample:
    query: str
    expected_keywords: list[str]
    id: str = ""


@dataclass
class EvalResult:
    example_id: str
    quality_score: float
    groundedness: float
    latency_ms: float
    estimated_cost_usd: float
    safety_flags: list[str] = field(default_factory=list)
    answer: str = ""


class Evaluator:
    def __init__(self, pipeline: RagPipeline, cost_model: CostModel | None = None):
        self.pipeline = pipeline
        self.cost_model = cost_model or CostModel()

    def evaluate(self, example: EvalExample) -> EvalResult:
        start = time.perf_counter()
        rag_answer = self.pipeline.answer(example.query)
        latency_ms = (time.perf_counter() - start) * 1000

        quality = token_overlap_relevance(rag_answer.answer, example.expected_keywords)
        grounded = groundedness_score(rag_answer.answer, [r.chunk.text for r in rag_answer.retrieved])
        # token counts are proxied via word counts in the mock LLM; good enough for a cost-gate demo
        est_cost = self.cost_model.estimate(
            input_tokens=len(example.query.split()) * 10, output_tokens=len(rag_answer.answer.split())
        )
        flags = safety_flags(rag_answer.answer)

        return EvalResult(
            example_id=example.id or example.query[:24],
            quality_score=quality,
            groundedness=grounded,
            latency_ms=latency_ms,
            estimated_cost_usd=est_cost,
            safety_flags=flags,
            answer=rag_answer.answer,
        )
