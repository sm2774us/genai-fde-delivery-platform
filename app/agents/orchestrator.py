"""Agentic orchestrator: plans, selects tools, enforces HITL gating on
high-risk actions, and falls back to the RAG pipeline for knowledge
questions. This is the "copilot / agentic workflow" surface called out in
the JD, built on top of the ontology (system-of-record actions) and RAG
(knowledge grounding) layers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agents.hitl import get_hitl_queue
from app.agents.tools import build_tool_registry
from app.core.config import get_settings
from app.core.llm_client import LLMClient
from app.core.logging import get_logger
from app.rag.pipeline import RagPipeline

log = get_logger(__name__)


@dataclass
class AgentStep:
    kind: str  # "tool_call" | "rag_answer" | "hitl_pending"
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    final_text: str
    steps: list[AgentStep]
    hitl_request_id: str | None = None


class AgentOrchestrator:
    def __init__(self, rag_pipeline: RagPipeline | None = None):
        self.llm = LLMClient()
        self.tools = build_tool_registry()
        self.rag = rag_pipeline or RagPipeline()
        self.hitl = get_hitl_queue()
        self.settings = get_settings()

    def run(self, user_message: str, approved_request_id: str | None = None) -> AgentResult:
        steps: list[AgentStep] = []

        # Resume path: a previously-queued HITL action has now been approved.
        if approved_request_id:
            req = self.hitl.get(approved_request_id)
            if req and req.status == "approved":
                tool = self.tools[req.tool_name]
                result = tool.handler({**req.arguments, "approved": True})
                steps.append(AgentStep("tool_call", {"tool": tool.name, "result": result}))
                return AgentResult(final_text=f"Action '{tool.name}' executed: {result}", steps=steps)

        tool_schemas = [t.to_schema() for t in self.tools.values()]
        routed = self.llm.complete_with_tools(
            system="Route the user request to a tool if one clearly applies; otherwise answer from knowledge.",
            prompt=user_message,
            tools=tool_schemas,
        )

        if routed.tool_calls:
            call = routed.tool_calls[0]
            tool = self.tools[call["name"]]
            steps.append(AgentStep("tool_call", {"tool": tool.name, "risk": tool.risk}))

            if tool.risk == self.settings.hitl_required_action_risk:
                req = self.hitl.submit(tool.name, call["arguments"], tool.risk)
                steps.append(AgentStep("hitl_pending", {"request_id": req.request_id}))
                log.info("hitl_gate_triggered", tool=tool.name, request_id=req.request_id)
                return AgentResult(
                    final_text=(
                        f"This action ('{tool.name}') is high-risk and requires human approval "
                        f"before execution. Approval request `{req.request_id}` has been queued."
                    ),
                    steps=steps,
                    hitl_request_id=req.request_id,
                )

            result = tool.handler(call["arguments"])
            steps.append(AgentStep("tool_call", {"tool": tool.name, "result": result}))
            return AgentResult(final_text=f"Tool '{tool.name}' result: {result}", steps=steps)

        # Fallback: grounded knowledge answer via RAG
        rag_answer = self.rag.answer(user_message)
        steps.append(AgentStep("rag_answer", {"grounded": rag_answer.grounded, "citations": rag_answer.citations}))
        return AgentResult(final_text=rag_answer.answer, steps=steps)
