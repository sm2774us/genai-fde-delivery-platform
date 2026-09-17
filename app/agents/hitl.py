"""Human-in-the-loop approval gate. High-risk tool calls (write-backs into
the ontology, irreversible actions) are queued for human approval rather
than auto-executed — a non-negotiable control for production GenAI agents
operating against enterprise systems of record."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ApprovalRequest:
    request_id: str
    tool_name: str
    arguments: dict
    risk: str
    status: str = "pending"  # pending | approved | rejected
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class HitlQueue:
    def __init__(self):
        self._queue: dict[str, ApprovalRequest] = {}

    def submit(self, tool_name: str, arguments: dict, risk: str) -> ApprovalRequest:
        req = ApprovalRequest(request_id=str(uuid.uuid4())[:8], tool_name=tool_name,
                               arguments=arguments, risk=risk)
        self._queue[req.request_id] = req
        return req

    def decide(self, request_id: str, approve: bool) -> ApprovalRequest:
        req = self._queue[request_id]
        req.status = "approved" if approve else "rejected"
        return req

    def pending(self) -> list[ApprovalRequest]:
        return [r for r in self._queue.values() if r.status == "pending"]

    def get(self, request_id: str) -> ApprovalRequest | None:
        return self._queue.get(request_id)


_hitl_singleton = HitlQueue()


def get_hitl_queue() -> HitlQueue:
    return _hitl_singleton
