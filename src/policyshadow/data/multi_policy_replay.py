"""Replays the dataset against multiple candidate policies and combines violations."""

from pathlib import Path

from policyshadow.core.schemas import CandidatePolicy, PolicyEngineType, Violation
from policyshadow.data.dataset import ALL_RECORDS
from policyshadow.persistence.repository import JSONFileViolationRepository
from policyshadow.policy_engines.kyverno_engine import KyvernoPolicyEngine
from policyshadow.replay.replay_engine import ReplayEngine

POLICIES_DIR = Path(__file__).parent / "sample_policies"

CANDIDATE_POLICIES = [
    CandidatePolicy(
        policy_id="p1", name="restrict-privileged-containers",
        engine=PolicyEngineType.KYVERNO,
        policy_path=str(POLICIES_DIR / "restrict-privileged-containers.yaml"),
    ),
    CandidatePolicy(
        policy_id="p2", name="require-non-root",
        engine=PolicyEngineType.KYVERNO,
        policy_path=str(POLICIES_DIR / "require-non-root.yaml"),
    ),
]


def replay_all_policies(output_path: str) -> list[Violation]:
    repo = JSONFileViolationRepository(output_path)
    engine = ReplayEngine(KyvernoPolicyEngine(), repo)
    all_violations = []
    for policy in CANDIDATE_POLICIES:
        all_violations.extend(engine.replay(ALL_RECORDS, policy))
    repo.save(all_violations)
    return all_violations
