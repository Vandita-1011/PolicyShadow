"""Subprocess worker: embeds, clusters, and retrieves evidence in a plain Python process."""

import json
import sys

from policyshadow.clustering.clusterer import cluster_violations
from policyshadow.core.schemas import Violation
from policyshadow.embeddings.embedder import embed_violations
from policyshadow.rag.evidence_builder import build_cluster_evidence


def main(in_path: str, out_path: str) -> None:
    with open(in_path, encoding="utf-8") as f:
        violations = [Violation(**v) for v in json.load(f)]
    embeddings = embed_violations(violations)
    clusters = cluster_violations(violations, embeddings)
    packaged = build_cluster_evidence(clusters, violations)
    result = [
        {
            "cluster_id": c["cluster_id"],
            "rule_name": c["rule_name"],
            "violation_count": c["violation_count"],
            "evidence": c["evidence"],
            "violation_ids": [v.violation_id for v in c["violations"]],
        }
        for c in packaged
    ]
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
