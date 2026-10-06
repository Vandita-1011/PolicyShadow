from pathlib import Path

from policyshadow.core.schemas import CandidatePolicy, PolicyEngineType
from policyshadow.data.synthetic_records import SYNTHETIC_RECORDS
from policyshadow.policy_engines.kyverno_engine import KyvernoPolicyEngine

POLICY_PATH = str(
    Path(__file__).parent.parent
    / "src" / "policyshadow" / "data" / "sample_policies" / "restrict-privileged-containers.yaml"
)


def _policy():
    return CandidatePolicy(
        policy_id="p1", name="restrict-privileged-containers",
        engine=PolicyEngineType.KYVERNO, policy_path=POLICY_PATH,
    )


def _record(record_id):
    return next(r for r in SYNTHETIC_RECORDS if r.record_id == record_id)


def test_clean_record_produces_no_violation():
    engine = KyvernoPolicyEngine()
    assert engine.evaluate(_record("r01"), _policy()) == []


def test_violating_record_produces_violation():
    engine = KyvernoPolicyEngine()
    violations = engine.evaluate(_record("r02"), _policy())
    assert len(violations) == 1
    assert violations[0].rule_name == "restrict-privileged-containers"
