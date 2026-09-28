"""Persistence tests against the real database — fabricated violations, no Kyverno, no LLM."""

from policyshadow.core.schemas import Violation
from policyshadow.persistence.postgres_repository import PostgresViolationRepository
from policyshadow.persistence.run_store import RunStore


def _violation(n):
    return Violation(
        record_id=f"r{n}", policy_id="p1", rule_name="privileged-containers",
        resource_kind="Pod", resource_name=f"pod-{n}", namespace="default", message="msg",
    )


def test_repository_is_scoped_to_its_run():
    store = RunStore()
    run_a, run_b = store.create_run(4), store.create_run(4)
    try:
        va, vb = [_violation(1), _violation(2)], [_violation(3)]
        PostgresViolationRepository(run_id=run_a).save(va)
        PostgresViolationRepository(run_id=run_b).save(vb)
        ids_a = {v.violation_id for v in PostgresViolationRepository(run_id=run_a).get_all()}
        ids_b = {v.violation_id for v in PostgresViolationRepository(run_id=run_b).get_all()}
        assert ids_a == {v.violation_id for v in va}
        assert ids_b == {v.violation_id for v in vb}
    finally:
        store.delete_run(run_a)
        store.delete_run(run_b)


def test_run_lifecycle_traceability_and_decisions():
    store = RunStore()
    run_id = store.create_run(4)
    try:
        violations = [_violation(i) for i in range(3)]
        PostgresViolationRepository(run_id=run_id).save(violations)
        cluster = {
            "cluster_id": "cluster-0", "rule_name": "privileged-containers",
            "violation_count": 3, "evidence": [{"source": "a.txt", "text": "t"}],
            "violation_ids": [v.violation_id for v in violations],
        }
        recommendation = {"category": "Delay enforcement", "risk_level": "Medium", "rationale": "because"}
        cluster_id, recommendation_id = store.save_cluster_result(
            run_id, cluster, "explanation", recommendation
        )

        assert store.get_run(run_id)["status"] == "running"
        store.complete_run(run_id)
        detail = store.get_run(run_id)
        assert detail["status"] == "completed"
        assert detail["total_records"] == 4
        assert detail["violation_count"] == 3
        [c] = detail["clusters"]
        assert c["cluster_id"] == cluster_id and c["label"] == "cluster-0"
        assert c["violation_ids"] == sorted(v.violation_id for v in violations)
        assert c["recommendation"]["recommendation_id"] == recommendation_id
        assert c["recommendation"]["decision"] is None

        store.record_decision(recommendation_id, "reject", "first")
        store.record_decision(recommendation_id, "approve", "changed mind")
        latest = store.get_run(run_id)["clusters"][0]["recommendation"]["decision"]
        assert latest["decision"] == "approve" and latest["note"] == "changed mind"
    finally:
        store.delete_run(run_id)
    assert store.get_run(run_id) is None
    assert PostgresViolationRepository(run_id=run_id).get_all() == []


def test_failed_run_records_error_and_unknown_recommendation_returns_none():
    store = RunStore()
    run_id = store.create_run(1)
    try:
        store.fail_run(run_id, "boom")
        detail = store.get_run(run_id)
        assert detail["status"] == "failed" and detail["error"] == "boom"
        assert store.record_decision("does-not-exist", "approve", None) is None
    finally:
        store.delete_run(run_id)
