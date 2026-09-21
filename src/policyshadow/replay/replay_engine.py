"""Historical Replay Engine: replays historical records against a candidate policy."""

from policyshadow.core.interfaces import PolicyEngine, ViolationRepository
from policyshadow.core.schemas import AdmissionReviewRecord, CandidatePolicy, Violation


class ReplayEngine:
    def __init__(self, policy_engine: PolicyEngine, repository: ViolationRepository):
        self.policy_engine = policy_engine
        self.repository = repository

    def replay(self, records: list[AdmissionReviewRecord], policy: CandidatePolicy) -> list[Violation]:
        violations = []
        for record in records:
            violations.extend(self.policy_engine.evaluate(record, policy))
        self.repository.save(violations)
        return violations
