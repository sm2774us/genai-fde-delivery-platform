# FDE Delivery Playbook — Prototype to Production

The phased plan an FDE pod runs with a client, from executive discovery through
scaled production, and how this repo's components map to each phase.

## Phase 0 — Executive Discovery (Weeks 1–2)
- Identify 1–2 high-value, bounded use cases (not "AI for everything").
- Define success metrics up front across five axes: **quality, latency, cost,
  adoption, risk** (see `docs/EXEC_METRICS.md`).
- Map data sources, systems of record, and identity/access constraints.
- Output: one-page charter signed by executive sponsor + IT/security leadership.

## Phase 1 — Prototype (Weeks 3–6)
- Stand up the ontology layer for the target domain (`app/ontology/`): define
  object types, relationships, and the first governed write-back action.
- Build the ingestion pipeline (`app/pipelines/ingestion_dag.py`) against a
  representative data sample; validate hybrid retrieval quality
  (`app/rag/hybrid_search.py`) on 15–20 real user questions.
- Ship a thin-slice copilot behind a feature flag to 3–5 pilot users.
- Exit criteria: quality gate ≥ target on the eval harness (`app/eval/harness.py`).

## Phase 2 — Pilot Hardening (Weeks 7–10)
- Add human-in-the-loop gating for any write-back action (`app/agents/hitl.py`).
- Wire CI-enforced regression testing (`.github/workflows/ci.yml`) so every
  prompt/retrieval change is scored before merge.
- Establish latency and cost budgets as hard CI gates, not dashboards nobody
  reads (`app/core/config.py` gate thresholds).
- Run a security/compliance review (`docs/SECURITY_COMPLIANCE.md`).

## Phase 3 — Production Rollout (Weeks 11–16)
- Expand pod to full onshore/offshore configuration; introduce sprint cadence
  and escalation paths (`docs/POD_GOVERNANCE.md`).
- Move vector store from in-memory to a managed backend (pgvector/OpenSearch);
  swap `VECTOR_STORE` config — no application code changes required.
- Instrument production observability: correlation IDs end-to-end
  (`app/core/logging.py`), per-query cost tracking, hallucination-rate
  dashboards sourced from the same metrics used in CI (`app/eval/metrics.py`).
- Go-live gate: two consecutive weekly eval runs pass all five quality gates.

## Phase 4 — Scale & Multi-Workstream (Month 5+)
- Replicate the ontology + RAG + agent pattern into adjacent workstreams
  under shared governance standards.
- Introduce multi-pod architecture review checkpoints to keep client
  experience consistent across workstreams.
- Transition steady-state operations to the client's platform team with a
  documented runbook and on-call rotation.

## Anti-patterns this playbook exists to prevent
- Shipping an ungoverned agent with write-access and no HITL gate.
- Declaring "production" without a CI-enforced eval harness.
- Vector-only retrieval on enterprise data with exact-match query patterns.
- Vendor lock-in from hardcoding one LLM provider's SDK into business logic.
