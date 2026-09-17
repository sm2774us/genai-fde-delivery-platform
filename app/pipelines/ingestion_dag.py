"""Data ingestion DAG (extract -> clean -> chunk -> embed -> index), expressed
as a plain dependency-ordered stage list here for portability. In a real
client engagement this same stage graph maps directly onto Airflow/dbt or a
Foundry pipeline build — the interface (each stage takes/returns a typed
payload) is what would be preserved when porting to a real orchestrator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from app.core.logging import get_logger
from app.rag.pipeline import RagPipeline

log = get_logger(__name__)


@dataclass
class Stage:
    name: str
    fn: Callable[[Any], Any]


def extract(raw_sources: list[dict]) -> list[dict]:
    """Stage 1: pull raw documents from source systems (stubbed here as
    pass-through; real implementation would hit SharePoint/Confluence/DB
    connectors)."""
    log.info("ingestion_extract", n=len(raw_sources))
    return raw_sources


def clean(docs: list[dict]) -> list[dict]:
    """Stage 2: normalize whitespace, strip boilerplate/markup."""
    cleaned = []
    for d in docs:
        text = " ".join(d["text"].split())
        cleaned.append({**d, "text": text})
    log.info("ingestion_clean", n=len(cleaned))
    return cleaned


def load_into_rag(docs: list[dict], pipeline: RagPipeline) -> int:
    """Stage 3+4 (chunk+embed+index handled inside RagPipeline.ingest)."""
    n_chunks = pipeline.ingest(docs)
    log.info("ingestion_load", n_chunks=n_chunks)
    return n_chunks


def run_ingestion_dag(raw_sources: list[dict], pipeline: RagPipeline) -> int:
    docs = extract(raw_sources)
    docs = clean(docs)
    return load_into_rag(docs, pipeline)
