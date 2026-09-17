from __future__ import annotations

from fastapi import APIRouter

from app.agents.orchestrator import AgentOrchestrator
from app.api.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])
_orchestrator = AgentOrchestrator()


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    result = _orchestrator.run(req.message, approved_request_id=req.approved_request_id)
    return ChatResponse(
        final_text=result.final_text,
        steps=[{"kind": s.kind, **s.detail} for s in result.steps],
        hitl_request_id=result.hitl_request_id,
    )
