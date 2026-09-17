from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    approved_request_id: str | None = None


class ChatResponse(BaseModel):
    final_text: str
    steps: list[dict[str, Any]]
    hitl_request_id: str | None = None


class IngestDocument(BaseModel):
    doc_id: str
    title: str
    text: str


class IngestRequest(BaseModel):
    documents: list[IngestDocument]


class IngestResponse(BaseModel):
    n_chunks: int


class ApprovalDecision(BaseModel):
    request_id: str
    approve: bool


class ActionInvokeRequest(BaseModel):
    action_api_name: str
    payload: dict[str, Any]
    actor: str = "api-user"
    approved: bool = False
