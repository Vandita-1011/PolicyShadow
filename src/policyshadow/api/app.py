"""FastAPI application exposing the PolicyShadow pipeline."""

from functools import lru_cache
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from policyshadow.api.pipeline import run_full_pipeline
from policyshadow.persistence.postgres_repository import PostgresViolationRepository
from policyshadow.persistence.run_store import RunStore

app = FastAPI(title="PolicyShadow")


class DecisionRequest(BaseModel):
    decision: Literal["approve", "reject"]
    note: str | None = None


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
