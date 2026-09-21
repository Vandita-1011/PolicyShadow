"""Connectivity check: real M2 clusters -> retrieval, not mocked clusters.

Checks that each real cluster retrieves knowledge from the correct
source files (by filename tag), not just that retrieval returns
something.
"""

from policyshadow.clustering.clusterer import cluster_violations
from policyshadow.data.multi_policy_replay import replay_all_policies
from policyshadow.embeddings.embedder import embed_violations
from policyshadow.rag.retriever import retrieve


def test_retrieval_matches_correct_cluster_topic(tmp_path):
    violations = replay_all_policies(str(tmp_path / "violations.json"))
    embeddings = embed_violations(violations)
    clusters = cluster_violations(violations, embeddings)
    by_id = {v.violation_id: v for v in violations}

    for members in clusters.values():
        rule_name = by_id[members[0]].rule_name
        query = f"{rule_name}: {by_id[members[0]].message}"
        results = retrieve(query, top_k=2)
        sources = [r["source"] for r in results]

        if rule_name == "privileged-containers":
            assert any("privileged" in s for s in sources)
        elif rule_name == "run-as-non-root":
            assert any("non-root" in s for s in sources)
