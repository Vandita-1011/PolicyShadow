"""Converts violations into semantic embeddings using a local sentence-transformers model."""

from sentence_transformers import SentenceTransformer

from policyshadow.core.schemas import Violation

_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_violations(violations: list[Violation]) -> dict[str, list[float]]:
    texts = [f"{v.rule_name}: {v.message}" for v in violations]
    vectors = _get_model().encode(texts)
    return {v.violation_id: vec.tolist() for v, vec in zip(violations, vectors)}
