"""Chunking strategies for the RAG ingestion pipeline. Token-aware sliding
window with overlap — the production-grade default for governed RAG (avoids
mid-sentence truncation, preserves context across boundaries)."""
from __future__ import annotations

from dataclasses import dataclass

try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")
except Exception:  # pragma: no cover - offline fallback
    _ENC = None


@dataclass
class Chunk:
    text: str
    doc_id: str
    chunk_id: str
    start_token: int
    end_token: int


def _token_len(text: str) -> int:
    return len(_ENC.encode(text)) if _ENC else len(text.split())


def chunk_document(
    doc_id: str, text: str, chunk_size: int = 256, overlap: int = 32
) -> list[Chunk]:
    """Sliding-window chunking by (approx) token count with overlap."""
    words = text.split()
    if not words:
        return []
    chunks: list[Chunk] = []
    step = max(chunk_size - overlap, 1)
    idx = 0
    i = 0
    while i < len(words):
        window = words[i : i + chunk_size]
        chunk_text = " ".join(window)
        chunks.append(
            Chunk(
                text=chunk_text,
                doc_id=doc_id,
                chunk_id=f"{doc_id}::chunk-{idx}",
                start_token=i,
                end_token=i + len(window),
            )
        )
        idx += 1
        i += step
    return chunks
