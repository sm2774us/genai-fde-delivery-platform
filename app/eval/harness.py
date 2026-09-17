"""Regression evaluation harness — CI-runnable quality gate. This is what a
delivery pod runs on every PR to prevent silent quality/cost/latency
regressions in a production GenAI system, satisfying the JD's requirement to
"define evaluation frameworks ... ensure the pod meets agreed engineering
quality bars."

Usage:
    python -m app.eval.harness --dataset data/sample/eval_set.jsonl
Exit code is non-zero if any quality gate fails (CI-enforceable).
"""
from __future__ import annotations

import argparse
import json
import sys
from statistics import mean

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.eval.evaluator import EvalExample, Evaluator
from app.rag.pipeline import RagPipeline

log = get_logger(__name__)


def load_dataset(path: str) -> list[EvalExample]:
    examples = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            examples.append(EvalExample(query=row["query"], expected_keywords=row["expected_keywords"], id=row.get("id", "")))
    return examples


def load_corpus(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def run(dataset_path: str, corpus_path: str) -> int:
    configure_logging()
    settings = get_settings()

    pipeline = RagPipeline()
    pipeline.ingest(load_corpus(corpus_path))

    examples = load_dataset(dataset_path)
    evaluator = Evaluator(pipeline)
    results = [evaluator.evaluate(ex) for ex in examples]

    avg_quality = mean(r.quality_score for r in results) if results else 0.0
    avg_grounded = mean(r.groundedness for r in results) if results else 0.0
    n_hallucinated = sum(1 for r in results if r.groundedness < 0.2)
    hallucination_rate = n_hallucinated / max(len(results), 1)
    p95_latency = sorted(r.latency_ms for r in results)[int(0.95 * (len(results) - 1))] if results else 0.0
    avg_cost = mean(r.estimated_cost_usd for r in results) if results else 0.0
    unsafe = [r for r in results if r.safety_flags]

    print("\n=== Evaluation Report ===")
    for r in results:
        print(f"[{r.example_id}] quality={r.quality_score:.2f} grounded={r.groundedness:.2f} "
              f"latency={r.latency_ms:.1f}ms cost=${r.estimated_cost_usd:.5f}")
    print("\n--- Aggregate ---")
    print(f"avg_quality={avg_quality:.3f} (gate >= {settings.quality_gate_min_score})")
    print(f"avg_groundedness={avg_grounded:.3f}")
    print(f"hallucination_rate={hallucination_rate:.3f} (gate <= {settings.hallucination_max_rate})")
    print(f"p95_latency_ms={p95_latency:.1f} (gate <= {settings.latency_p95_ms_budget})")
    print(f"avg_cost_per_query_usd={avg_cost:.5f} (gate <= {settings.cost_per_query_budget_usd})")
    print(f"unsafe_outputs={len(unsafe)} (gate == 0)")

    gates_passed = (
        avg_quality >= settings.quality_gate_min_score
        and hallucination_rate <= settings.hallucination_max_rate
        and p95_latency <= settings.latency_p95_ms_budget
        and avg_cost <= settings.cost_per_query_budget_usd
        and len(unsafe) == 0
    )

    print(f"\nQUALITY GATES: {'PASSED' if gates_passed else 'FAILED'}")
    return 0 if gates_passed else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="data/sample/eval_set.jsonl")
    parser.add_argument("--corpus", default="data/sample/corpus.json")
    args = parser.parse_args()
    sys.exit(run(args.dataset, args.corpus))
