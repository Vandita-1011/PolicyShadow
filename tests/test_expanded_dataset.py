"""Connectivity check: the M1 replay engine, unmodified, against the expanded dataset."""

import json
from pathlib import Path

from policyshadow.core.schemas import CandidatePolicy, PolicyEngineType
from policyshadow.data.dataset import ALL_RECORDS
from policyshadow.persistence.repository import JSONFileViolationRepository
from policyshadow.policy_engines.kyverno_engine import KyvernoPolicyEngine
from policyshadow.replay.replay_engine import ReplayEngine

FIXTURE = Path(__file__).parent / "fixtures" / "expected_violations_expanded.json"
POLICY_PATH = str(
    Path(__file__).parent.parent
    / "src" / "policyshadow" / "data" / "sample_policies" / "restrict-privileged-containers.yaml"
)


def test_expanded_dataset_matches_expected(tmp_path):
    expected = json.loads(FIXTURE.read_text())
    policy = CandidatePolicy(
        policy_id="p1", name="restrict-privileged-containers",
        engine=PolicyEngineType.KYVERNO, policy_path=POLICY_PATH,
    )
    repo = JSONFileViolationRepository(str(tmp_path / "violations.json"))
    engine = ReplayEngine(KyvernoPolicyEngine(), repo)

    violations = engine.replay(ALL_RECORDS, policy)

    assert len(violations) == expected["expected_violation_count"]
    assert {v.record_id for v in violations} == set(expected["expected_violating_record_ids"])
