# Security, Privacy & Compliance Considerations

Practical considerations an FDE must own on every client engagement,
mapped to where this repo demonstrates or stubs the control.

## Data handling
- **PII/sensitive-data screening** on LLM outputs before they reach a user —
  demonstrated as a stub in `app/eval/metrics.py::safety_flags`; in
  production this calls a real DLP/moderation service.
- **Least-privilege data access**: the ontology layer (`app/ontology/`) is
  the single governed access point for object data — application code never
  queries raw source tables directly, so access control lives in one place.
- **Data residency**: `CLOUD_PROVIDER` config plus `infra/cloud_adapter.py`
  keep storage/secrets backends swappable per client region requirement.

## Action governance
- Every write-back action carries an explicit `ActionRisk` tier
  (`app/ontology/models.py`) and high-risk actions require human approval
  (`app/agents/hitl.py`) before execution — no autonomous agent has
  unsupervised write access to systems of record.
- Full audit trail (`ActionAudit`) captures actor, payload, approval status,
  and result for every invoked action — required for SOC2/audit evidence.

## Model governance
- Provider-agnostic LLM client (`app/core/llm_client.py`) avoids vendor lock
  and makes it straightforward to route sensitive workloads to a
  client-approved/self-hosted model where required.
- Grounding/citation is enforced at the pipeline level
  (`RagPipeline._check_grounding`), not left to prompt instructions — reduces
  hallucination risk that could produce non-compliant or incorrect guidance.

## Operational security
- Structured logging with correlation IDs (`app/core/logging.py`) supports
  incident investigation without embedding raw payloads in logs by default.
- CI-enforced quality gates (`.github/workflows/ci.yml`) block regressions
  before they reach production, including a safety-flag gate.

## What a real engagement adds on top of this repo
- Formal threat model per use case, reviewed with client CISO/security team.
- Real DLP/moderation API integration (not the keyword-stub here).
- Fine-grained RBAC on ontology objects and actions per client identity
  provider (SSO/SCIM integration).
- Data retention and right-to-deletion workflows for any PII touched by RAG
  ingestion.
