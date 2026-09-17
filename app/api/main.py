from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.pipelines.ingestion_dag import run_ingestion_dag

configure_logging(get_settings().log_level)
log = get_logger(__name__)

app = FastAPI(
    title="FDE GenAI Delivery Platform — Showcase",
    description="Reference FDE-style GenAI delivery platform: ontology, RAG, agentic workflows, eval/governance.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

from app.api.routes_chat import router as chat_router  # noqa: E402
from app.api.routes_evaluate import router as evaluate_router  # noqa: E402
from app.api.routes_ingest import router as ingest_router  # noqa: E402
from app.api.routes_ontology import router as ontology_router  # noqa: E402

app.include_router(chat_router)
app.include_router(ingest_router)
app.include_router(ontology_router)
app.include_router(evaluate_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def seed_demo_knowledge():
    """Auto-ingest sample knowledge docs on boot so /chat is demoable immediately."""
    from app.api.routes_chat import _orchestrator

    seed_docs = [
        {
            "doc_id": "kb-sso-1",
            "title": "SSO Migration Runbook",
            "text": (
                "After the SSO migration on March 2nd, some customers experienced repeated login "
                "failures due to stale session tokens cached by legacy clients. The fix is to force "
                "a full re-authentication by clearing the session cache and reissuing SAML assertions. "
                "Tier-1 support should first confirm the customer's identity provider domain is on the "
                "updated allowlist before escalating to tier-2 for a token cache purge."
            ),
        },
        {
            "doc_id": "kb-risk-1",
            "title": "Customer Risk Scoring Policy",
            "text": (
                "Customer risk scores range from 0 (lowest risk) to 1 (highest risk) and are weighted "
                "by account tier: gold customers receive a 0.5x weighting, silver 0.75x, and bronze 1.0x, "
                "reflecting historical support burden per tier. Risk scores above 0.7 after weighting "
                "require manual review before any credit-limit change is approved."
            ),
        },
    ]
    run_ingestion_dag(seed_docs, _orchestrator.rag)
    log.info("startup_seed_complete", n_docs=len(seed_docs))
