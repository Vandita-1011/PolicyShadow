"""Persistence for runs, clusters, recommendations and engineer decisions."""

import uuid

from policyshadow.persistence.db import SessionLocal, engine
from policyshadow.persistence.models import (
    Base,
    ClusterModel,
    DecisionModel,
    RecommendationModel,
    RunModel,
    ViolationModel,
    utcnow,
)


def _new_id() -> str:
    return str(uuid.uuid4())


class RunStore:
    def __init__(self):
        Base.metadata.create_all(engine)

    def create_run(self, total_records: int) -> str:
        run_id = _new_id()
        with SessionLocal() as session:
            session.add(RunModel(run_id=run_id, status="running", total_records=total_records))
            session.commit()
        return run_id

    def complete_run(self, run_id: str) -> None:
        self._set_status(run_id, "completed", None)

    def fail_run(self, run_id: str, error: str) -> None:
        self._set_status(run_id, "failed", error[:2000])

    def _set_status(self, run_id: str, status: str, error: str | None) -> None:
        with SessionLocal() as session:
            session.query(RunModel).filter(RunModel.run_id == run_id).update(
                {"status": status, "error": error}
            )
            session.commit()

    def save_cluster_result(
        self, run_id: str, cluster: dict, explanation: str, recommendation: dict
    ) -> tuple[str, str]:
        cluster_id, recommendation_id = _new_id(), _new_id()
        with SessionLocal() as session:
            session.add(ClusterModel(
                id=cluster_id, run_id=run_id, label=cluster["cluster_id"],
                rule_name=cluster["rule_name"], violation_count=cluster["violation_count"],
                evidence=cluster["evidence"], explanation=explanation,
            ))
            session.flush()
            session.add(RecommendationModel(
                id=recommendation_id, cluster_id=cluster_id,
                category=recommendation["category"], risk_level=recommendation["risk_level"],
                rationale=recommendation["rationale"],
            ))
            session.flush()
            session.query(ViolationModel).filter(
                ViolationModel.violation_id.in_(cluster["violation_ids"])
            ).update({"cluster_id": cluster_id}, synchronize_session=False)
            session.commit()
        return cluster_id, recommendation_id

    def record_decision(
        self, recommendation_id: str, decision: str, note: str | None
    ) -> dict | None:
        with SessionLocal() as session:
            if session.get(RecommendationModel, recommendation_id) is None:
                return None
            decided_at = utcnow()
            row = DecisionModel(
                recommendation_id=recommendation_id, decision=decision,
                note=note, decided_at=decided_at,
            )
            session.add(row)
            session.flush()
            decision_id = row.id
            session.commit()
        return {
            "decision_id": decision_id, "recommendation_id": recommendation_id,
            "decision": decision, "note": note, "decided_at": decided_at.isoformat(),
        }

    def delete_run(self, run_id: str) -> bool:
        with SessionLocal() as session:
            deleted = session.query(RunModel).filter(
                RunModel.run_id == run_id
            ).delete(synchronize_session=False)
            session.commit()
        return deleted > 0

    def list_runs(self) -> list[dict]:
        with SessionLocal() as session:
            rows = session.query(RunModel).order_by(RunModel.created_at.desc()).all()
            return [
                {
                    "run_id": r.run_id, "created_at": r.created_at.isoformat(),
                    "status": r.status, "total_records": r.total_records,
                }
                for r in rows
            ]

    def get_run(self, run_id: str) -> dict | None:
        with SessionLocal() as session:
            run = session.get(RunModel, run_id)
            if run is None:
                return None
            clusters = (
                session.query(ClusterModel)
                .filter(ClusterModel.run_id == run_id)
                .order_by(ClusterModel.label)
                .all()
            )
            recommendations = (
                session.query(RecommendationModel)
                .filter(RecommendationModel.cluster_id.in_([c.id for c in clusters]))
                .all()
            )
            recommendation_by_cluster = {r.cluster_id: r for r in recommendations}
            decisions = (
                session.query(DecisionModel)
                .filter(DecisionModel.recommendation_id.in_([r.id for r in recommendations]))
                .order_by(DecisionModel.id)
                .all()
            )
            latest_decision = {d.recommendation_id: d for d in decisions}
            members = (
                session.query(ViolationModel.violation_id, ViolationModel.cluster_id)
                .filter(ViolationModel.run_id == run_id)
                .all()
            )
            ids_by_cluster: dict[str | None, list[str]] = {}
            for violation_id, cluster_id in members:
                ids_by_cluster.setdefault(cluster_id, []).append(violation_id)

            cluster_dicts = []
            for c in clusters:
                r = recommendation_by_cluster[c.id]
                d = latest_decision.get(r.id)
                cluster_dicts.append({
                    "cluster_id": c.id,
                    "label": c.label,
                    "rule_name": c.rule_name,
                    "violation_count": c.violation_count,
                    "violation_ids": sorted(ids_by_cluster.get(c.id, [])),
                    "evidence": c.evidence,
                    "explanation": c.explanation,
                    "recommendation": {
                        "recommendation_id": r.id,
                        "category": r.category,
                        "risk_level": r.risk_level,
                        "rationale": r.rationale,
                        "decision": None if d is None else {
                            "decision": d.decision,
                            "note": d.note,
                            "decided_at": d.decided_at.isoformat(),
                        },
                    },
                })
            return {
                "run_id": run.run_id,
                "created_at": run.created_at.isoformat(),
                "status": run.status,
                "total_records": run.total_records,
                "error": run.error,
                "violation_count": len(members),
                "clusters": cluster_dicts,
            }
