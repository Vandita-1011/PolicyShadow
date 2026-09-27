"""Connectivity check: real pipeline through to a validated recommendation."""

from policyshadow.clustering.clusterer import cluster_violations
from policyshadow.data.dataset import ALL_RECORDS
from policyshadow.data.multi_policy_replay import replay_all_policies
from policyshadow.embeddings.embedder import embed_violations
from policyshadow.explanation.explainer import explain_cluster
from policyshadow.rag.evidence_builder import build_cluster_evidence
from policyshadow.recommendation.recommender import (
    CATEGORIES,
    assess_risk_level,
    recommend_rollout,
)


def test_risk_level_thresholds():
    assert assess_risk_level(1, 100) == "Low"
    assert assess_risk_level(19, 100) == "Low"
    assert assess_risk_level(20, 100) == "Medium"
    assert assess_risk_level(60, 100) == "Medium"
    assert assess_risk_level(61, 100) == "High"
    assert assess_risk_level(100, 100) == "High"


def test_recommendation_uses_valid_category(tmp_path):
    violations = replay_all_policies(str(tmp_path / "violations.json"))
    embeddings = embed_violations(violations)
    clusters = cluster_violations(violations, embeddings)
    packaged = build_cluster_evidence(clusters, violations)

    for cluster in packaged:
        explanation = explain_cluster(cluster)
        result = recommend_rollout(cluster, explanation, len(ALL_RECORDS))
        assert result["category"] in CATEGORIES
        assert result["risk_level"] in ("Low", "Medium", "High")
        assert len(result["rationale"]) > 20

