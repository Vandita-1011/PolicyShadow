"""Orchestrates the full pipeline: replay -> analysis subprocess -> explain -> recommend -> persist."""

from policyshadow.api.analysis_runner import run_analysis
from policyshadow.data.dataset import ALL_RECORDS
from policyshadow.data.multi_policy_replay import CANDIDATE_POLICIES
from policyshadow.explanation.explainer import explain_cluster
from policyshadow.persistence.postgres_repository import PostgresViolationRepository
from policyshadow.persistence.run_store import RunStore
from policyshadow.policy_engines.kyverno_engine import KyvernoPolicyEngine
from policyshadow.recommendation.recommender import recommend_rollout
from policyshadow.replay.replay_engine import ReplayEngine


def run_full_pipeline() -> list[dict]:
    store = RunStore()
    run_id = store.create_run(len(ALL_RECORDS))
    try:
        repo = PostgresViolationRepository(run_id=run_id)
        engine = ReplayEngine(KyvernoPolicyEngine(), repo)

        all_violations = []
        for policy in CANDIDATE_POLICIES:
            all_violations.extend(engine.replay(ALL_RECORDS, policy))

        results = []
        for cluster in run_analysis(all_violations):
            explanation = explain_cluster(cluster)
            recommendation = recommend_rollout(cluster, explanation, len(ALL_RECORDS))
            cluster_id, recommendation_id = store.save_cluster_result(
                run_id, cluster, explanation, recommendation
            )
            results.append({
                "run_id": run_id,
                "cluster_id": cluster_id,
                "label": cluster["cluster_id"],
                "rule_name": cluster["rule_name"],
                "violation_count": cluster["violation_count"],
                "explanation": explanation,
                "recommendation": {**recommendation, "recommendation_id": recommendation_id},
            })
        store.complete_run(run_id)
        return results
    except Exception as exc:
        store.fail_run(run_id, str(exc))
        raise
