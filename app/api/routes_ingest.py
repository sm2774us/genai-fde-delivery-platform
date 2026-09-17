from __future__ import annotations

from fastapi import APIRouter

from app.agents.orchestrator import AgentOrchestrator
from app.api.schemas import IngestRequest, IngestResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])

# Share the orchestrator's RAG pipeline instance so ingested docs are queryable via /chat too.
from app.api.routes_chat import _orchestrator  # noqa: E402


@router.post("", response_model=IngestResponse)
def ingest(req: IngestRequest) -> IngestResponse:
    docs = [d.model_dump() for d in req.documents]
    n_chunks = _orchestrator.rag.ingest(docs)
    return IngestResponse(n_chunks=n_chunks)
