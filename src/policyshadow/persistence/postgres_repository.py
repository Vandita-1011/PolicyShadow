"""Postgres-backed implementation of the existing ViolationRepository interface."""

from policyshadow.core.interfaces import ViolationRepository
from policyshadow.core.schemas import Violation
from policyshadow.persistence.db import SessionLocal, engine
from policyshadow.persistence.models import Base, ViolationModel


class PostgresViolationRepository(ViolationRepository):
    def __init__(self, run_id: str | None = None):
        self.run_id = run_id
        Base.metadata.create_all(engine)

    def save(self, violations: list[Violation]) -> None:
        with SessionLocal() as session:
            for v in violations:
                session.merge(ViolationModel(run_id=self.run_id, **v.model_dump(mode="json")))
            session.commit()

    def get_all(self) -> list[Violation]:
        with SessionLocal() as session:
            query = session.query(ViolationModel)
            if self.run_id is not None:
                query = query.filter(ViolationModel.run_id == self.run_id)
            return [
                Violation(
                    violation_id=r.violation_id, record_id=r.record_id, policy_id=r.policy_id,
                    rule_name=r.rule_name, resource_kind=r.resource_kind,
                    resource_name=r.resource_name, namespace=r.namespace, message=r.message,
                    severity=r.severity, raw_result=r.raw_result,
                )
                for r in query.all()
            ]
