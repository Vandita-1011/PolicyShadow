"""Embeds the corpus once and retrieves the top-k chunks for a query."""

import numpy as np

from policyshadow.embeddings.embedder import _get_model
from policyshadow.rag.corpus_loader import load_chunks

_chunks = None
_chunk_vectors = None


def _load():
    global _chunks, _chunk_vectors
    if _chunks is None:
        _chunks = load_chunks()
        texts = [c["text"] for c in _chunks]
        _chunk_vectors = np.array(_get_model().encode(texts))


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    _load()
    query_vec = np.array(_get_model().encode([query])[0])
    sims = _chunk_vectors @ query_vec / (
        np.linalg.norm(_chunk_vectors, axis=1) * np.linalg.norm(query_vec)
    )
    top_indices = np.argsort(sims)[::-1][:top_k]
    return [_chunks[i] for i in top_indices]
