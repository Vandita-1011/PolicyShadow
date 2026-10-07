"""Proves the user-submitted policy, not the hardcoded demo policies,
actually controls the analysis result. This is the single most
important test for the real-time policy submission feature."""

from policyshadow.persistence.policy_store import PolicyStore
from policyshadow.api.pipeline import run_full_pipeline
from policyshadow.persistence.run_store import RunStore

DISTINCT_POLICY = """
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-team-label-test
spec:
  background: true
  rules:
    - name: require-team-label
      match:
        any:
          - resources:
              kinds:
                - Pod
      validate:
        failureAction: Audit
        message: "Pods must declare a team label."
        pattern:
          metadata:
            labels:
              team: "?*"
"""


def test_submitted_policy_produces_different_result_than_demo_policies():
    store = PolicyStore()
    created = store.create_user_policy("require-team-label-test", "test policy", DISTINCT_POLICY)

    try:
        results = run_full_pipeline(policy_id=created["policy_id"])

        assert len(results) == 1, "Submitting one policy must evaluate exactly that one policy"
        assert results[0]["rule_name"] == "require-team-label-test"
        assert results[0]["violation_count"] not in (15, 16)
        assert results[0]["violation_count"] > 20
    finally:
        RunStore().delete_run(results[0]["run_id"])
        from policyshadow.persistence.db import SessionLocal
        from policyshadow.persistence.models import PolicyModel
        with SessionLocal() as s:
            s.query(PolicyModel).filter(PolicyModel.policy_id == created["policy_id"]).delete()
            s.commit()


def test_invalid_policy_id_raises_instead_of_silently_using_demo_policies():
    import pytest
    from policyshadow.persistence.db import SessionLocal
    from policyshadow.persistence.models import RunModel
    with pytest.raises(ValueError):
        run_full_pipeline(policy_id="this-policy-does-not-exist")
    with SessionLocal() as s:
        s.query(RunModel).filter(
            RunModel.status == "failed",
            RunModel.error.like("%this-policy-does-not-exist%")
        ).delete()
        s.commit()



def test_no_policy_id_preserves_existing_default_behavior():
    results = run_full_pipeline(policy_id=None)
    try:
        assert len(results) == 2
        rule_names = {r["rule_name"] for r in results}
        assert rule_names == {"restrict-privileged-containers", "require-non-root"}
    finally:
        RunStore().delete_run(results[0]["run_id"])
