"""Connectivity check: real replay -> real Postgres (Neon) -> read back.

This proves the existing ViolationRepository interface from Milestone 1
works unchanged with a real Postgres implementation, not just the JSON
one it was built and tested against.
"""

from policyshadow.data.dataset import ALL_RECORDS
from policyshadow.data.multi_policy_replay import CANDIDATE_POLICIES
from policyshadow.persistence.postgres_repository import PostgresViolationRepository
from policyshadow.policy_engines.kyverno_engine import KyvernoPolicyEngine
from policyshadow.replay.replay_engine import ReplayEngine


def test_postgres_repository_round_trip():
    repo = PostgresViolationRepository()
    engine = ReplayEngine(KyvernoPolicyEngine(), repo)

    all_violations = []
    for policy in CANDIDATE_POLICIES:
        all_violations.extend(engine.replay(ALL_RECORDS, policy))
    repo.save(all_violations)

    stored = repo.get_all()
    stored_ids = {v.violation_id for v in stored}
    for v in all_violations:
        assert v.violation_id in stored_ids
    assert len(stored) >= len(all_violations)
