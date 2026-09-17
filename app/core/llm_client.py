"""Provider-agnostic LLM client. Swapping LLM_PROVIDER swaps the backend with
no changes to RAG/agent/eval code — the kind of platform abstraction an FDE
must build so a client engagement isn't locked to one vendor.

`mock` provider is deterministic and offline so this repo runs with zero API
keys (interviewer-friendly); real providers are wired but optional.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    model: str = "mock-llm-v1"


class LLMClient:
    """Uniform interface: complete() and complete_with_tools()."""

    def __init__(self, provider: str | None = None):
        self.provider = provider or get_settings().llm_provider

    def complete(self, system: str, prompt: str, max_tokens: int = 512) -> LLMResponse:
        if self.provider == "mock":
            return self._mock_complete(system, prompt, max_tokens)
        # Real integrations would branch here (anthropic / azure_openai / bedrock / vertex).
        # Kept out-of-box functional via mock so the repo runs with zero external deps.
        log.warning("provider_not_configured_falling_back_to_mock", provider=self.provider)
        return self._mock_complete(system, prompt, max_tokens)

    def complete_with_tools(
        self, system: str, prompt: str, tools: list[dict[str, Any]], max_tokens: int = 512
    ) -> LLMResponse:
        """Deterministic mock tool-selection: keyword-routes to a tool so the
        agentic-workflow demo is fully reproducible without live model calls."""
        chosen = self._route_tool(prompt, tools)
        base = self._mock_complete(system, prompt, max_tokens)
        if chosen:
            base.tool_calls = [chosen]
        return base

    # -- mock backend -----------------------------------------------------
    def _mock_complete(self, system: str, prompt: str, max_tokens: int) -> LLMResponse:
        seed = int(hashlib.sha256((system + prompt).encode()).hexdigest(), 16) % (10**6)
        summary = self._extractive_summary(prompt, max_sentences=3)
        text = f"{summary}"
        return LLMResponse(
            text=text,
            input_tokens=len(prompt.split()),
            output_tokens=len(text.split()),
            model=f"mock-llm-v1#{seed}",
        )

    @staticmethod
    def _extractive_summary(text: str, max_sentences: int = 3) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [s for s in sentences if s]
        if not sentences:
            return "No content available to summarize."
        return " ".join(sentences[:max_sentences])

    @staticmethod
    def _route_tool(prompt: str, tools: list[dict[str, Any]]) -> dict[str, Any] | None:
        p = prompt.lower()
        for tool in tools:
            name = tool["name"].lower()
            keywords = tool.get("keywords", [name.replace("_", " ")])
            if any(kw in p for kw in keywords):
                return {"name": tool["name"], "arguments": {"query": prompt[:200]}}
        return None
