"""Core metrics for the evaluation framework: quality (answer relevance),
hallucination/groundedness, latency, and cost. These are the exact axes the
JD calls out for GenAI evaluation frameworks."""
from __future__ import annotations

from dataclasses import dataclass


def token_overlap_relevance(answer: str, expected_keywords: list[str]) -> float:
    """Cheap, deterministic relevance proxy: fraction of expected keywords
    present in the answer. Stands in for an LLM-judge score in this offline
    demo; `evaluator.py` shows where a real judge model plugs in."""
    if not expected_keywords:
        return 1.0
    answer_l = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in answer_l)
    return hits / len(expected_keywords)


def groundedness_score(answer: str, context_chunks: list[str]) -> float:
    answer_tokens = set(answer.lower().split())
    context_tokens = set(tok for c in context_chunks for tok in c.lower().split())
    if not answer_tokens:
        return 0.0
    return len(answer_tokens & context_tokens) / len(answer_tokens)


@dataclass
class CostModel:
    input_cost_per_1k: float = 0.003
    output_cost_per_1k: float = 0.015

    def estimate(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens / 1000) * self.input_cost_per_1k + (
            output_tokens / 1000
        ) * self.output_cost_per_1k


def safety_flags(answer: str) -> list[str]:
    """Lightweight safety screen (PII patterns, unsafe-content markers).
    Production systems would call a moderation endpoint; this stub keeps the
    interface and gate logic real without external dependencies."""
    flags = []
    lowered = answer.lower()
    if any(term in lowered for term in ["ssn:", "social security number", "password:"]):
        flags.append("possible_sensitive_data_leak")
    return flags
