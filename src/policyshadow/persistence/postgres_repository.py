"""Postgres-backed implementation of the existing ViolationRepository interface."""

from policyshadow.core.interfaces import ViolationRepository
from policyshadow.core.schemas import Violation
from policyshadow.persistence.db import SessionLocal, engine
from policyshadow.persistence.models import Base, ViolationModel


class PostgresViolationRepository(ViolationRepository):
    def __init__(self):
        Base.metadata.create_all(engine)

    def save(self, violations: list[Violation]) -> None:
        session = SessionLocal()
        for v in violations:
            session.merge(ViolationModel(**v.model_dump(mode="json")))
        session.commit()
        session.close()

    def get_all(self) -> list[Violation]:
        session = SessionLocal()
        rows = session.query(ViolationModel).all()
        session.close()
        return [
            Violation(
                violation_id=r.violation_id, record_id=r.record_id, policy_id=r.policy_id,
                rule_name=r.rule_name, resource_kind=r.resource_kind, resource_name=r.resource_name,
                namespace=r.namespace, message=r.message, severity=r.severity,
                raw_result=r.raw_result,
            )
            for r in rows
        ]
