"""FastAPI application exposing the PolicyShadow pipeline."""

from functools import lru_cache
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from policyshadow.api.pipeline import run_full_pipeline
from policyshadow.persistence.postgres_repository import PostgresViolationRepository
from policyshadow.persistence.run_store import RunStore
from policyshadow.persistence.policy_store import PolicyStore

app = FastAPI(title="PolicyShadow")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PolicyCreateRequest(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    rule_definition: str | None = None
    notes: str | None = None
    status: str = "active"


class DecisionRequest(BaseModel):
    decision: Literal["approve", "reject"]
    note: str | None = None


@lru_cache
def _policy_store() -> PolicyStore:
    return PolicyStore()


@lru_cache
def _store() -> RunStore:
    return RunStore()


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/analyze")
def analyze():
    return run_full_pipeline()


@app.get("/runs")
def runs():
    return _store().list_runs()


@app.get("/runs/{run_id}")
def run_detail(run_id: str):
    detail = _store().get_run(run_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="run not found")
    return detail


@app.post("/recommendations/{recommendation_id}/decision")
def decide(recommendation_id: str, body: DecisionRequest):
    result = _store().record_decision(recommendation_id, body.decision, body.note)
    if result is None:
        raise HTTPException(status_code=404, detail="recommendation not found")
    return result


@app.get("/violations")
def violations():
    repo = PostgresViolationRepository()
    return [v.model_dump(mode="json") for v in repo.get_all()]


@app.get("/policies")
def list_policies():
    return _policy_store().list_policies()


@app.post("/policies")
def create_policy(body: PolicyCreateRequest):
    return _policy_store().create_policy(
        body.name, body.description, body.category,
        body.rule_definition, body.notes, body.status,
    )


@app.get("/stats")
def stats():
    return {
        "total_runs": _store().count_runs(),
        "total_policies": _policy_store().count_policies(),
        "total_violations_detected": _store().count_total_violations(),
        "pending_decisions": _store().count_pending_decisions(),
    }
