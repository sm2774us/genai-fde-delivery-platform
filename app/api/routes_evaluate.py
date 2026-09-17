from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.routes_chat import _orchestrator
from app.eval.evaluator import EvalExample, Evaluator

router = APIRouter(prefix="/evaluate", tags=["evaluate"])


class EvalRequest(BaseModel):
    query: str
    expected_keywords: list[str] = []


@router.post("")
def evaluate(req: EvalRequest):
    evaluator = Evaluator(_orchestrator.rag)
    result = evaluator.evaluate(EvalExample(query=req.query, expected_keywords=req.expected_keywords))
    return result.__dict__
