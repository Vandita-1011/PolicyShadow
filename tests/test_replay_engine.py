import json
from pathlib import Path

from policyshadow.core.schemas import CandidatePolicy, PolicyEngineType
from policyshadow.data.synthetic_records import SYNTHETIC_RECORDS
from policyshadow.persistence.repository import JSONFileViolationRepository
from policyshadow.policy_engines.kyverno_engine import KyvernoPolicyEngine
from policyshadow.replay.replay_engine import ReplayEngine

FIXTURE = Path(__file__).parent / "fixtures" / "expected_violations.json"
POLICY_PATH = str(
    Path(__file__).parent.parent
    / "src" / "policyshadow" / "data" / "sample_policies" / "restrict-privileged-containers.yaml"
)


def test_replay_produces_expected_violations(tmp_path):
    expected = json.loads(FIXTURE.read_text())
    policy = CandidatePolicy(
        policy_id="p1", name="restrict-privileged-containers",
        engine=PolicyEngineType.KYVERNO, policy_path=POLICY_PATH,
    )
    repo = JSONFileViolationRepository(str(tmp_path / "violations.json"))
    engine = ReplayEngine(KyvernoPolicyEngine(), repo)

    violations = engine.replay(SYNTHETIC_RECORDS, policy)

    violating_ids = {v.record_id for v in violations}
    assert violating_ids == set(expected["expected_violating_record_ids"])
    for v in violations:
        assert v.rule_name == expected["expected_rule_name"]
        assert expected["expected_message_substring"] in v.message
