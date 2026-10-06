"""FastAPI application exposing the PolicyShadow pipeline."""

import time
import threading
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

# ---------------------------------------------------------------------------
# Lightweight in-memory TTL cache
# Keeps the last computed value of slow read endpoints for up to TTL seconds.
# Any write operation (analyze / decide / submit) calls _invalidate_cache()
# so the next read always fetches fresh data from the database.
# ---------------------------------------------------------------------------
_CACHE_TTL = 5  # seconds — kept short because multiple machines may
# share the same remote database; a long TTL risks one machine
# showing stale data after another machine writes.
_cache_lock = threading.Lock()
_cache: dict[str, tuple[float, object]] = {}  # key -> (timestamp, value)


def _cache_get(key: str):
    """Return cached value if still within TTL, else None."""
    with _cache_lock:
        entry = _cache.get(key)
        if entry and (time.monotonic() - entry[0]) < _CACHE_TTL:
            return entry[1]
    return None


def _cache_set(key: str, value):
    """Store a value in the cache with the current timestamp."""
    with _cache_lock:
        _cache[key] = (time.monotonic(), value)
    return value


def _invalidate_cache(*keys: str):
    """Remove specific keys from the cache (or all keys if none given)."""
    with _cache_lock:
        if keys:
            for k in keys:
                _cache.pop(k, None)
        else:
            _cache.clear()


# ---------------------------------------------------------------------------
# Singleton store accessors (unchanged)
# ---------------------------------------------------------------------------

class PolicyCreateRequest(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    rule_definition: str | None = None
    notes: str | None = None
    status: str = "active"


class PolicyValidateRequest(BaseModel):
    policy_yaml: str


class PolicySubmitRequest(BaseModel):
    name: str
    description: str | None = None
    policy_yaml: str


class AnalyzeRequest(BaseModel):
    policy_id: str | None = None


class DecisionRequest(BaseModel):
    decision: Literal["approve", "reject"]
    note: str | None = None


@lru_cache
def _policy_store() -> PolicyStore:
    return PolicyStore()


@lru_cache
def _store() -> RunStore:
    return RunStore()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(body: AnalyzeRequest | None = None):
    policy_id = body.policy_id if body else None
    result = run_full_pipeline(policy_id=policy_id)
    # A new run was created — invalidate run list and stats caches
    _invalidate_cache("runs", "stats")
    return result


@app.get("/runs")
def runs():
    cached = _cache_get("runs")
    if cached is not None:
        return cached
    return _cache_set("runs", _store().list_runs())


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
    # Decision changed pending count and run summaries — bust both caches
    _invalidate_cache("stats", "runs")
    return result


@app.get("/violations")
def violations():
    repo = PostgresViolationRepository()
    return [v.model_dump(mode="json") for v in repo.get_all()]


@app.get("/policies")
def list_policies():
    cached = _cache_get("policies")
    if cached is not None:
        return cached
    return _cache_set("policies", _policy_store().list_policies())


@app.post("/policies")
def create_policy(body: PolicyCreateRequest):
    result = _policy_store().create_policy(
        body.name, body.description, body.category,
        body.rule_definition, body.notes, body.status,
    )
    _invalidate_cache("policies", "stats")
    return result


@app.post("/policies/validate")
def validate_policy(body: PolicyValidateRequest):
    from policyshadow.policy_engines.policy_validator import validate_policy_yaml
    valid, error = validate_policy_yaml(body.policy_yaml)
    return {"valid": valid, "error": error}


@app.post("/policies/submit")
def submit_policy(body: PolicySubmitRequest):
    from policyshadow.policy_engines.policy_validator import validate_policy_yaml
    valid, error = validate_policy_yaml(body.policy_yaml)
    if not valid:
        raise HTTPException(status_code=422, detail=error)
    result = _policy_store().create_user_policy(body.name, body.description, body.policy_yaml)
    _invalidate_cache("policies", "stats")
    return result


@app.get("/stats")
def stats():
    cached = _cache_get("stats")
    if cached is not None:
        return cached
    value = {
        "total_runs": _store().count_runs(),
        "total_policies": _policy_store().count_policies(),
        "total_violations_detected": _store().count_total_violations(),
        "pending_decisions": _store().count_pending_decisions(),
    }
    return _cache_set("stats", value)
