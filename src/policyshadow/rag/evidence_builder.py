"""Packages each cluster together with its retrieved evidence for downstream use."""

from policyshadow.core.schemas import Violation
from policyshadow.rag.retriever import retrieve


def build_cluster_evidence(
    clusters: dict[str, list[str]], violations: list[Violation]
) -> list[dict]:
    by_id = {v.violation_id: v for v in violations}
    result = []
    for cluster_id, member_ids in clusters.items():
        members = [by_id[vid] for vid in member_ids]
        rule_name = members[0].rule_name
        query = f"{rule_name}: {members[0].message}"
        evidence = retrieve(query, top_k=3)
        result.append({
            "cluster_id": cluster_id,
            "rule_name": rule_name,
            "violation_count": len(members),
            "violations": members,
            "evidence": evidence,
        })
    return result
