"""Deterministic tests for policy persistence."""

from policyshadow.persistence.policy_store import PolicyStore


def test_system_policies_are_seeded_and_idempotent():
    store = PolicyStore()
    policies = store.list_policies()
    system = [p for p in policies if p["is_system"]]
    assert {p["name"] for p in system} == {"restrict-privileged-containers", "require-non-root"}
    PolicyStore()
    assert len({p["policy_id"] for p in PolicyStore().list_policies()}) == len(
        PolicyStore().list_policies()
    )


def test_create_custom_policy_persists_and_lists():
    from policyshadow.persistence.db import SessionLocal
    from policyshadow.persistence.models import PolicyModel

    store = PolicyStore()
    created = store.create_policy(
        "test-policy-xyz", "desc", "Custom", "rule text", "note", "active"
    )
    try:
        assert created["is_system"] is False
        fetched = store.get_policy(created["policy_id"])
        assert fetched["name"] == "test-policy-xyz"
        assert any(p["policy_id"] == created["policy_id"] for p in store.list_policies())
    finally:
        with SessionLocal() as s:
            s.query(PolicyModel).filter(PolicyModel.policy_id == created["policy_id"]).delete()
            s.commit()
