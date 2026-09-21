"""End-to-end Milestone 1 runner: replay synthetic records against the sample policy."""

from pathlib import Path

from policyshadow.core.schemas import CandidatePolicy, PolicyEngineType
from policyshadow.data.synthetic_records import SYNTHETIC_RECORDS
from policyshadow.persistence.repository import JSONFileViolationRepository
from policyshadow.policy_engines.kyverno_engine import KyvernoPolicyEngine
from policyshadow.replay.replay_engine import ReplayEngine

POLICY_PATH = str(
    Path(__file__).parent.parent
    / "src" / "policyshadow" / "data" / "sample_policies" / "restrict-privileged-containers.yaml"
)
OUTPUT_PATH = Path(__file__).parent.parent / "milestone1_output.json"


def main():
    policy = CandidatePolicy(
        policy_id="p1", name="restrict-privileged-containers",
        engine=PolicyEngineType.KYVERNO, policy_path=POLICY_PATH,
    )
    repo = JSONFileViolationRepository(str(OUTPUT_PATH))
    engine = ReplayEngine(KyvernoPolicyEngine(), repo)

    violations = engine.replay(SYNTHETIC_RECORDS, policy)
    print(f"Replayed {len(SYNTHETIC_RECORDS)} records against '{policy.name}'.")
    print(f"Violations found: {len(violations)}")
    print(f"Output written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
