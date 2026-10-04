"""Orchestrates the full pipeline: replay -> analysis subprocess -> explain -> recommend -> persist."""

from policyshadow.api.analysis_runner import run_analysis
from policyshadow.core.schemas import CandidatePolicy, PolicyEngineType
from policyshadow.data.dataset import ALL_RECORDS
from policyshadow.data.multi_policy_replay import CANDIDATE_POLICIES
from policyshadow.explanation.explainer import explain_cluster
from policyshadow.persistence.postgres_repository import PostgresViolationRepository
from policyshadow.persistence.run_store import RunStore
from policyshadow.policy_engines.kyverno_engine import KyvernoPolicyEngine
from policyshadow.recommendation.recommender import recommend_rollout
from policyshadow.replay.replay_engine import ReplayEngine


def run_full_pipeline(policy_id: str | None = None) -> list[dict]:
    store = RunStore()
    run_id = store.create_run(len(ALL_RECORDS))
    try:
        repo = PostgresViolationRepository(run_id=run_id)
        engine = ReplayEngine(KyvernoPolicyEngine(), repo)

        if policy_id is not None:
            from policyshadow.persistence.policy_store import PolicyStore
            path = PolicyStore().resolve_policy_path(policy_id)
            if path is None:
                raise ValueError(f"Unknown policy_id: {policy_id!r}")
            policy = PolicyStore().get_policy(policy_id)
            policies_to_run = [
                CandidatePolicy(
                    policy_id=policy_id,
                    name=policy["name"],
                    engine=PolicyEngineType.KYVERNO,
                    policy_path=path,
                )
            ]
        else:
            policies_to_run = CANDIDATE_POLICIES

        all_violations = []
        for policy in policies_to_run:
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

        policy_ids_used = [policy_id] if policy_id else [p.policy_id for p in CANDIDATE_POLICIES]
        store._set_policy_ids(run_id, policy_ids_used)
        store.complete_run(run_id)
        return results
    except Exception as exc:
        store.fail_run(run_id, str(exc))
        raise
