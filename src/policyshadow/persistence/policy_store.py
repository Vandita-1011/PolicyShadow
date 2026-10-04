"""Persistence for policies (both system and user-created)."""

import uuid
from pathlib import Path

from policyshadow.persistence.db import SessionLocal, engine
from policyshadow.persistence.models import Base, PolicyModel

USER_POLICIES_DIR = Path(__file__).parent.parent / "data" / "user_policies"

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

    def count_policies(self) -> int:
        with SessionLocal() as session:
            return session.query(PolicyModel).count()

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

    def create_user_policy(
        self, name: str, description: str | None, policy_yaml: str,
    ) -> dict:
        USER_POLICIES_DIR.mkdir(parents=True, exist_ok=True)
        policy_id = str(uuid.uuid4())
        file_path = USER_POLICIES_DIR / f"{policy_id}.yaml"
        file_path.write_text(policy_yaml, encoding="utf-8")

        with SessionLocal() as session:
            row = PolicyModel(
                policy_id=policy_id, name=name, description=description,
                category="User-submitted", rule_definition=None, notes=None,
                status="active", is_system="false",
                policy_yaml=policy_yaml, policy_file_path=str(file_path),
            )
            session.add(row)
            session.commit()
            return self._to_dict(row)

    def resolve_policy_path(self, policy_id: str) -> str | None:
        """Returns the file path to use for Kyverno evaluation for a given policy_id."""
        policy = self.get_policy(policy_id)
        if policy is None:
            return None
        if policy["is_system"]:
            system_paths = {
                "p1": str(Path(__file__).parent.parent / "data" / "sample_policies" / "restrict-privileged-containers.yaml"),
                "p2": str(Path(__file__).parent.parent / "data" / "sample_policies" / "require-non-root.yaml"),
            }
            return system_paths.get(policy_id)
        return policy["policy_file_path"]

    @staticmethod
    def _to_dict(r: PolicyModel) -> dict:
        return {
            "policy_id": r.policy_id, "name": r.name, "description": r.description,
            "category": r.category, "rule_definition": r.rule_definition,
            "notes": r.notes, "status": r.status,
            "is_system": r.is_system == "true", "created_at": r.created_at.isoformat(),
            "policy_yaml": r.policy_yaml, "policy_file_path": r.policy_file_path,
        }
