"""Connectivity check: real dataset -> real replay -> real Kyverno violations -> embeddings.

No mocks — this proves the new embedding step actually connects to the
existing Milestone 1 pipeline, not just that it works in isolation.
"""

from pathlib import Path

from policyshadow.core.schemas import CandidatePolicy, PolicyEngineType
from policyshadow.data.dataset import ALL_RECORDS
from policyshadow.embeddings.embedder import embed_violations
from policyshadow.persistence.repository import JSONFileViolationRepository
from policyshadow.policy_engines.kyverno_engine import KyvernoPolicyEngine
from policyshadow.replay.replay_engine import ReplayEngine

POLICY_PATH = str(
    Path(__file__).parent.parent
    / "src" / "policyshadow" / "data" / "sample_policies" / "restrict-privileged-containers.yaml"
)


def test_embeddings_generated_for_real_violations(tmp_path):
    policy = CandidatePolicy(
        policy_id="p1", name="restrict-privileged-containers",
        engine=PolicyEngineType.KYVERNO, policy_path=POLICY_PATH,
    )
    repo = JSONFileViolationRepository(str(tmp_path / "violations.json"))
    engine = ReplayEngine(KyvernoPolicyEngine(), repo)
    violations = engine.replay(ALL_RECORDS, policy)

    embeddings = embed_violations(violations)

    assert len(embeddings) == len(violations)
    for vec in embeddings.values():
        assert len(vec) == 384
