"""Orchestrates the full pipeline: replay -> analysis subprocess -> explain -> recommend."""

from policyshadow.api.analysis_runner import run_analysis
from policyshadow.data.dataset import ALL_RECORDS
from policyshadow.data.multi_policy_replay import CANDIDATE_POLICIES
from policyshadow.explanation.explainer import explain_cluster
from policyshadow.persistence.postgres_repository import PostgresViolationRepository
from policyshadow.policy_engines.kyverno_engine import KyvernoPolicyEngine
from policyshadow.recommendation.recommender import recommend_rollout
from policyshadow.replay.replay_engine import ReplayEngine


def run_full_pipeline() -> list[dict]:
    repo = PostgresViolationRepository()
    engine = ReplayEngine(KyvernoPolicyEngine(), repo)

    all_violations = []
    for policy in CANDIDATE_POLICIES:
        all_violations.extend(engine.replay(ALL_RECORDS, policy))
    repo.save(all_violations)

    packaged = run_analysis(all_violations)

    results = []
    for cluster in packaged:
        explanation = explain_cluster(cluster)
        recommendation = recommend_rollout(cluster, explanation, len(ALL_RECORDS))
        results.append({
            "cluster_id": cluster["cluster_id"],
            "rule_name": cluster["rule_name"],
            "violation_count": cluster["violation_count"],
            "explanation": explanation,
            "recommendation": recommendation,
        })
    return results
