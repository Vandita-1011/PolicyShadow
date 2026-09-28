"""FastAPI application exposing the PolicyShadow pipeline."""

from fastapi import FastAPI

from policyshadow.api.pipeline import run_full_pipeline
from policyshadow.persistence.postgres_repository import PostgresViolationRepository

app = FastAPI(title="PolicyShadow")


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/analyze")
def analyze():
    return run_full_pipeline()


@app.get("/violations")
def violations():
    repo = PostgresViolationRepository()
    return [v.model_dump(mode="json") for v in repo.get_all()]
