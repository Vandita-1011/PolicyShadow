"""Abstractions decoupling the replay engine from specific policy engines and storage."""

from abc import ABC, abstractmethod

from policyshadow.core.schemas import AdmissionReviewRecord, CandidatePolicy, Violation


class PolicyEngine(ABC):
    @abstractmethod
    def evaluate(self, record: AdmissionReviewRecord, policy: CandidatePolicy) -> list[Violation]:
        ...


class ViolationRepository(ABC):
    @abstractmethod
    def save(self, violations: list[Violation]) -> None:
        ...

    @abstractmethod
    def get_all(self) -> list[Violation]:
        ...
