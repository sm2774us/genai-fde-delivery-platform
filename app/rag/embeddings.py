"""Embedding backend abstraction. Ships a deterministic hashing-based
embedder so the repo runs fully offline/reproducibly; swap in a real
embedding API (OpenAI/Azure/Bedrock/Vertex) by implementing `Embedder`."""
from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod

import numpy as np


class Embedder(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> np.ndarray: ...


class HashingEmbedder(Embedder):
    """Deterministic bag-of-words hashing embedding (dim=256). Not
    semantically rich, but stable, offline, and sufficient to demonstrate a
    real hybrid-retrieval pipeline end-to-end without external API keys."""

    def __init__(self, dim: int = 256):
        self.dim = dim

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            for token in text.lower().split():
                h = int(hashlib.md5(token.encode()).hexdigest(), 16)
                vectors[i, h % self.dim] += 1.0
            norm = np.linalg.norm(vectors[i])
            if norm > 0:
                vectors[i] /= norm
        return vectors


def get_embedder() -> Embedder:
    return HashingEmbedder()
