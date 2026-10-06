"""End-to-end: real HTTP app -> real pipeline (Groq, Kyverno) -> real Postgres. Takes minutes."""

from fastapi.testclient import TestClient

from policyshadow.api.app import app
from policyshadow.persistence.run_store import RunStore

client = TestClient(app)


def test_run_is_persisted_and_traceable():
    response = client.post("/analyze")
    assert response.status_code == 200
    items = response.json()
    run_id = items[0]["run_id"]
    try:
        assert {i["run_id"] for i in items} == {run_id}
        assert run_id in [r["run_id"] for r in client.get("/runs").json()]

        detail = client.get(f"/runs/{run_id}").json()
        assert detail["status"] == "completed"
        assert detail["total_records"] == 30
        assert detail["violation_count"] == 31
        assert len(detail["clusters"]) == 2
        counts = {c["rule_name"]: c["violation_count"] for c in detail["clusters"]}
        assert counts == {"restrict-privileged-containers": 15, "require-non-root": 16}
        for c in detail["clusters"]:
            assert len(c["violation_ids"]) == c["violation_count"]
            assert len(c["evidence"]) == 3
            assert len(c["explanation"]) > 100
            assert c["recommendation"]["decision"] is None

        rec_id = detail["clusters"][0]["recommendation"]["recommendation_id"]
        decision = client.post(
            f"/recommendations/{rec_id}/decision", json={"decision": "approve", "note": "test"}
        )
        assert decision.status_code == 200

        after = client.get(f"/runs/{run_id}").json()
        by_id = {c["recommendation"]["recommendation_id"]: c for c in after["clusters"]}
        assert by_id[rec_id]["recommendation"]["decision"]["decision"] == "approve"
        [other] = [c for rid, c in by_id.items() if rid != rec_id]
        assert other["recommendation"]["decision"] is None
    finally:
        RunStore().delete_run(run_id)


def test_decision_validation_and_unknown_ids():
    assert client.post("/recommendations/nope/decision", json={"decision": "approve"}).status_code == 404
    assert client.post("/recommendations/nope/decision", json={"decision": "maybe"}).status_code == 422
    assert client.get("/runs/nope").status_code == 404
