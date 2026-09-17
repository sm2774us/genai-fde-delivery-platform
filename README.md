# Forward Deployed Engineering Showcase — GenAI Delivery Platform

A production-shaped reference implementation demonstrating the technical scope of a **Lead Forward Deployed Engineer** role: client-embedded GenAI delivery combining an **Ontology layer** (Foundry/AIP-style), **RAG pipeline**, **agentic workflows with tool-use and human-in-the-loop**, an **evaluation/observability framework** (quality, hallucination, latency, cost, safety), **data pipelines**, and **CI/CD governance**.

This is not a toy chatbot — it is structured the way an FDE pod would structure a real client engagement: ontology-first modeling, phased prototype→production pipeline, quality gates, and multi-pod-ready service boundaries.

## Why this repo maps to the JD

| JD Requirement | Where it's demonstrated |
|---|---|
| GenAI solutions into production (copilots, agentic workflows, knowledge search) | `app/agents/`, `app/rag/`, `app/api/routes_chat.py` |
| Palantir-style platform experience (Foundry/AIP/Maven concepts) | `app/ontology/` — object types, action types, links, write-back |
| RAG pipeline governance (ingestion, chunking, embedding, hybrid search) | `app/rag/pipeline.py`, `app/rag/chunking.py`, `app/rag/hybrid_search.py` |
| Prompt engineering, tool-use, human-in-the-loop | `app/agents/orchestrator.py`, `app/agents/tools.py`, `app/agents/hitl.py` |
| Evaluation frameworks (quality, hallucination, safety, latency, cost) | `app/eval/` — `evaluator.py`, `metrics.py`, `harness.py` |
| Data pipeline / feature-engineering foundations | `app/pipelines/ingestion_dag.py`, `app/pipelines/feature_pipeline.py` |
| Production engineering rigor: testing, CI/CD, logging, versioning | `.github/workflows/ci.yml`, `tests/`, `app/core/logging.py`, `app/core/config.py` |
| Cloud-agnostic deployment (AWS/Azure/GCP) | `infra/` (Terraform-style stubs + Dockerfile), `infra/cloud_adapter.py` |
| Executive-facing metrics / phased delivery plan | `docs/DELIVERY_PLAYBOOK.md`, `docs/EXEC_METRICS.md` |
| Multi-pod / governance cadences | `docs/POD_GOVERNANCE.md` |

## Architecture

```
Client Data Sources
      │  (ingestion_dag.py: extract → clean → chunk → embed)
      ▼
 Ontology Layer (app/ontology) ── Object/Action/Link types, write-back actions
      │
      ▼
 RAG Pipeline (app/rag) ── hybrid (BM25 + vector) retrieval, re-rank, cite
      │
      ▼
 Agent Orchestrator (app/agents) ── planner, tool-use, HITL approval gate
      │
      ▼
 Evaluation Harness (app/eval) ── quality / hallucination / latency / cost / safety gates
      │
      ▼
 FastAPI Service (app/api) ── /chat, /ingest, /evaluate, /ontology, /actions
```

## Quickstart

```bash
git clone <this-repo>
cd fde-showcase
cp .env.example .env
docker compose -f infra/docker-compose.yml up --build
# or locally:
pip install -r requirements.txt
uvicorn app.api.main:app --reload
```

Run the evaluation harness (quality gate CI step):
```bash
python -m app.eval.harness --dataset data/sample/eval_set.jsonl
```

Run tests:
```bash
pytest -q
```

## Repo Map
```
app/
  core/        config, logging, security, telemetry
  ontology/    Foundry/AIP-style object/action/link model + semantic layer
  rag/         ingestion, chunking, embeddings, hybrid retrieval, citation
  agents/      orchestrator, tool registry, HITL gate, prompt templates
  eval/        metrics, LLM-judge evaluator, regression harness, cost tracker
  pipelines/   data ingestion DAG, feature pipeline (Spark-style interface)
  api/         FastAPI routes: chat, ingest, ontology, actions, evaluate
infra/         Dockerfile, docker-compose, cloud adapter (AWS/Azure/GCP), Terraform stub
docs/          delivery playbook, exec metrics, pod governance, security/compliance
tests/         unit + integration tests, CI-enforced
```

See `docs/DELIVERY_PLAYBOOK.md` for the phased prototype→production plan and
`docs/EXEC_METRICS.md` for the C-suite-facing success-metrics framework used to
frame this kind of engagement with client sponsors.
