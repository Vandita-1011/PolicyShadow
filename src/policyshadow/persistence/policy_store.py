"""Persistence for policies (both system and user-created)."""

import uuid

from policyshadow.persistence.db import SessionLocal, engine
from policyshadow.persistence.models import Base, PolicyModel

SYSTEM_POLICIES = [
    {
        "policy_id": "p1",
        "name": "restrict-privileged-containers",
        "description": "Blocks Pods that set securityContext.privileged to true.",
        "category": "Pod Security Standards (Baseline)",
        "rule_definition": "spec.containers[*].securityContext.privileged must be unset or false",
        "is_system": "true",
    },
    {
        "policy_id": "p2",
        "name": "require-non-root",
        "description": "Requires every container to explicitly set runAsNonRoot to true.",
        "category": "Pod Security Standards (Restricted)",
        "rule_definition": "spec.containers[*].securityContext.runAsNonRoot must be true",
        "is_system": "true",
    },
]


class PolicyStore:
    def __init__(self):
        Base.metadata.create_all(engine)
        self._seed_system_policies()

    def _seed_system_policies(self) -> None:
        with SessionLocal() as session:
            for p in SYSTEM_POLICIES:
                if session.get(PolicyModel, p["policy_id"]) is None:
                    session.add(PolicyModel(status="active", **p))
            session.commit()

    def list_policies(self) -> list[dict]:
        with SessionLocal() as session:
            rows = session.query(PolicyModel).order_by(PolicyModel.created_at).all()
            return [self._to_dict(r) for r in rows]

    def get_policy(self, policy_id: str) -> dict | None:
        with SessionLocal() as session:
            row = session.get(PolicyModel, policy_id)
            return None if row is None else self._to_dict(row)

    def create_policy(
        self, name: str, description: str | None, category: str | None,
        rule_definition: str | None, notes: str | None, status: str,
    ) -> dict:
        policy_id = str(uuid.uuid4())
        with SessionLocal() as session:
            row = PolicyModel(
                policy_id=policy_id, name=name, description=description,
                category=category, rule_definition=rule_definition, notes=notes,
                status=status, is_system="false",
            )
            session.add(row)
            session.commit()
            return self._to_dict(row)

    @staticmethod
    def _to_dict(r: PolicyModel) -> dict:
        return {
            "policy_id": r.policy_id, "name": r.name, "description": r.description,
            "category": r.category, "rule_definition": r.rule_definition,
            "notes": r.notes, "status": r.status,
            "is_system": r.is_system == "true", "created_at": r.created_at.isoformat(),
        }
