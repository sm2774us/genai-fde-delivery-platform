from app.eval.evaluator import EvalExample, Evaluator
from app.rag.pipeline import RagPipeline


def test_evaluator_produces_bounded_scores():
    pipeline = RagPipeline()
    pipeline.ingest([{"doc_id": "d1", "title": "T", "text": "Gold tier customers get a 0.5x risk weighting."}])
    evaluator = Evaluator(pipeline)
    result = evaluator.evaluate(EvalExample(query="What weighting do gold tier customers get?", expected_keywords=["0.5x", "gold"]))
    assert 0.0 <= result.quality_score <= 1.0
    assert 0.0 <= result.groundedness <= 1.0
    assert result.latency_ms >= 0
    assert result.estimated_cost_usd >= 0
