"""Tool registry for the agentic orchestrator. Each tool declares a risk
level so the orchestrator can enforce human-in-the-loop gating consistently,
independent of which tool is invoked — a governance pattern, not a per-tool
hack."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from app.ontology.registry import get_registry


@dataclass
class Tool:
    name: str
    description: str
    keywords: list[str]
    risk: str  # low | medium | high
    handler: Callable[[dict[str, Any]], dict[str, Any]]

    def to_schema(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "keywords": self.keywords}


def _tool_lookup_customer(args: dict[str, Any]) -> dict[str, Any]:
    reg = get_registry()
    customers = reg.list_objects("Customer")
    return {"customers": customers}


def _tool_lookup_case(args: dict[str, Any]) -> dict[str, Any]:
    reg = get_registry()
    cases = reg.list_objects("Case")
    return {"cases": cases}


def _tool_escalate_case(args: dict[str, Any]) -> dict[str, Any]:
    reg = get_registry()
    case_id = args.get("case_id", "CS-1")
    return reg.invoke_action("escalate_case", {"case_id": case_id}, actor="agent", approved=args.get("approved", False))


def _tool_web_search_stub(args: dict[str, Any]) -> dict[str, Any]:
    return {"result": f"(stub) external search results for: {args.get('query', '')}"}


def build_tool_registry() -> dict[str, Tool]:
    tools = [
        Tool("lookup_customer", "Look up customer records in the ontology.",
             ["lookup customer", "customer account", "customer record", "customer information"],
             "low", _tool_lookup_customer),
        Tool("escalate_case", "Escalate a case to tier-2 (write-back action; requires approval).",
             ["escalate"], "high", _tool_escalate_case),
        Tool("lookup_case", "Look up support cases in the ontology.",
             ["lookup case", "ticket", "case status", "case information"], "low", _tool_lookup_case),
        Tool("web_search", "Search external knowledge (stub connector).",
             ["search", "look up online"], "medium", _tool_web_search_stub),
    ]
    return {t.name: t for t in tools}
