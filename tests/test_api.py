"""Connectivity check: real HTTP request -> real pipeline -> real Postgres.

This calls the actual Groq API and actual Neon database through the real
FastAPI app, not mocked. Expect this to take 2-3 minutes.
"""

from fastapi.testclient import TestClient

from policyshadow.api.app import app
from policyshadow.recommendation.recommender import CATEGORIES

client = TestClient(app)


def test_root_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_returns_two_clusters_with_valid_data():
    response = client.post("/analyze")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    rule_names = {c["rule_name"] for c in data}
    assert rule_names == {"restrict-privileged-containers", "require-non-root"}

    total = sum(c["violation_count"] for c in data)
    assert total == 31

    for c in data:
        assert len(c["explanation"]) > 100
        assert c["recommendation"]["category"] in CATEGORIES
        assert c["recommendation"]["risk_level"] in ("Low", "Medium", "High")


def test_violations_endpoint_returns_persisted_data():
    response = client.get("/violations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 31
