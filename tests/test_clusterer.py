"""Connectivity check: real dataset -> two real policies -> real embeddings -> clustering.

Checks cluster PURITY (do violations from the same policy rule end up
together) rather than exact cluster IDs, since cluster numbering is
arbitrary and shouldn't be hardcoded.
"""

from policyshadow.clustering.clusterer import cluster_violations
from policyshadow.data.multi_policy_replay import replay_all_policies
from policyshadow.embeddings.embedder import embed_violations


def test_clustering_groups_by_rule_type(tmp_path):
    violations = replay_all_policies(str(tmp_path / "violations.json"))
    embeddings = embed_violations(violations)
    clusters = cluster_violations(violations, embeddings)
    violation_by_id = {v.violation_id: v for v in violations}

    assert len(clusters) > 1

    correct = 0
    for members in clusters.values():
        rule_names = [violation_by_id[vid].rule_name for vid in members]
        majority = max(set(rule_names), key=rule_names.count)
        correct += rule_names.count(majority)

    purity = correct / len(violations)
    assert purity >= 0.85
