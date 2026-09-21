"""Connectivity check: real clusters + real evidence -> real Groq call.

LLM output is non-deterministic, so this checks STRUCTURE (grounding,
non-triviality) not exact text. The full text is printed separately
below for manual review, same discipline as clustering/retrieval.
"""

from policyshadow.clustering.clusterer import cluster_violations
from policyshadow.data.multi_policy_replay import replay_all_policies
from policyshadow.embeddings.embedder import embed_violations
from policyshadow.explanation.explainer import explain_cluster
from policyshadow.rag.evidence_builder import build_cluster_evidence


def test_explanation_cites_real_evidence_sources(tmp_path):
    violations = replay_all_policies(str(tmp_path / "violations.json"))
    embeddings = embed_violations(violations)
    clusters = cluster_violations(violations, embeddings)
    packaged = build_cluster_evidence(clusters, violations)

    for cluster in packaged:
        explanation = explain_cluster(cluster)
        assert len(explanation) > 100
        source_names = [e["source"] for e in cluster["evidence"]]
        assert any(name in explanation for name in source_names)
