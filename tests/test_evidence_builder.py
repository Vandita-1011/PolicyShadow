"""Connectivity check: real replay -> real clusters -> real evidence, packaged."""

from policyshadow.clustering.clusterer import cluster_violations
from policyshadow.data.multi_policy_replay import replay_all_policies
from policyshadow.embeddings.embedder import embed_violations
from policyshadow.rag.evidence_builder import build_cluster_evidence


def test_evidence_packaged_per_cluster(tmp_path):
    violations = replay_all_policies(str(tmp_path / "violations.json"))
    embeddings = embed_violations(violations)
    clusters = cluster_violations(violations, embeddings)

    packaged = build_cluster_evidence(clusters, violations)

    assert len(packaged) == len(clusters)
    total_violations = sum(p["violation_count"] for p in packaged)
    assert total_violations == len(violations)
    for p in packaged:
        assert len(p["evidence"]) == 3
        assert p["rule_name"] in ("restrict-privileged-containers", "require-non-root")
