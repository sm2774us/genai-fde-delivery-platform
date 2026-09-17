# Executive Success Metrics Framework

The framework used to translate engineering trade-offs into decisions client
leaders (CIO/CDO/business owners) can act on. Every metric here is computed
by code in this repo (`app/eval/metrics.py`, `app/eval/harness.py`), not
hand-waved in a slide.

| Metric | What it means to an executive | How it's measured here |
|---|---|---|
| **Quality** | "Does the assistant actually answer correctly?" | `token_overlap_relevance` / LLM-judge score against a labeled eval set |
| **Hallucination risk** | "Can we trust unsupervised outputs?" | `groundedness_score` — lexical/semantic overlap between answer and retrieved context |
| **Latency** | "Will users actually adopt this, or abandon it?" | p95 response time tracked per query in the eval harness |
| **Cost** | "What does this cost to run at scale?" | Per-query token-cost model (`CostModel`), rolled up to $/1000 queries |
| **Adoption** | "Are the people we built this for using it?" | Not code-computed here (needs production telemetry) — tracked via weekly active users / task completion rate against the Phase 0 charter |
| **Risk / Governance** | "What can go wrong, and is it contained?" | HITL gate coverage on all high-risk actions (`app/agents/hitl.py`), safety-flag rate (`safety_flags`), full action audit trail (`ActionAudit`) |

## How this is presented to a steering committee
1. **One slide, five numbers** — the five metrics above, red/yellow/green
   against the gates defined in `.env.example` (`QUALITY_GATE_MIN_SCORE`, etc).
2. **Trend, not snapshot** — week-over-week movement matters more than any
   single number; regression = immediate root-cause, not a shrug.
3. **Cost-to-value framing** — cost per query is always paired with the
   business action it enables (e.g., "$0.02/query to deflect a $12 support
   ticket" — the ROI conversation executives actually want).
4. **Risk is a first-class metric**, not an afterthought — every write-back
   action's risk tier and approval status is auditable end-to-end.
