# FDE Pod Leadership & Governance Model

## Pod composition
- 1 Lead FDE (onshore, client-embedded) — technical direction, client trust,
  escalation owner.
- 2–4 supporting engineers (mixed onshore/offshore) — feature delivery,
  code review, pairing.
- Shared: 1 client-side product/data owner as counterpart.

## Cadences
- **Daily standup** (15 min, cross-timezone-friendly window) — blockers only.
- **Weekly eval review** — walk the CI eval harness trend report
  (`app/eval/harness.py` output) with the pod; any regression gets a named
  owner and a fix-by date before the meeting ends.
- **Bi-weekly steering sync** with client executive sponsor — five-metric
  scorecard (`docs/EXEC_METRICS.md`), risks, and the next milestone.
- **Sprint cadence**: 2-week sprints, quality gates enforced at PR time via
  CI (`.github/workflows/ci.yml`), not at sprint-end.

## Escalation paths
1. Engineering blocker → Lead FDE same-day.
2. Client organizational blocker (access, sign-off, scope) → Lead FDE
   escalates to client sponsor within 24h with a proposed resolution, not
   just a flag.
3. Production incident → Lead FDE is incident commander; postmortem within
   48h using the audit trail already captured (`ActionAudit`, correlation IDs).

## Quality gates enforced across the pod (non-negotiable)
- No PR merges without passing the eval harness gates (quality, hallucination,
  latency, cost, safety — see `docs/EXEC_METRICS.md`).
- No write-back action ships without a defined risk tier and, for high-risk
  actions, a human-in-the-loop approval path (`app/agents/hitl.py`).
- All ontology changes (`app/ontology/`) are reviewed by the Lead FDE before
  merge — this is the client's system-of-record contract.

## Mentorship
- Junior FDEs pair on at least one ontology/action-type design per sprint
  with the Lead FDE reviewing, not just approving.
- Rotating "eval harness owner" role so every engineer builds fluency in
  reading and improving the quality-gate metrics, not just shipping features.

## Multi-pod / multi-workstream coordination
- Shared ontology conventions (naming, risk-tiering, audit schema) documented
  once and reused across pods to keep the client experience consistent.
- Cross-pod architecture review every 4 weeks to catch drift before it
  becomes technical debt across workstreams.
