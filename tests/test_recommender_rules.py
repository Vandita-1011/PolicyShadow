"""Deterministic tests for the rollout rules — no network, no real LLM call."""

from types import SimpleNamespace

import pytest

from policyshadow.recommendation import recommender
from policyshadow.recommendation.recommender import (
    CATEGORIES,
    ENFORCE,
    allowed_categories,
    recommend_rollout,
)

CLUSTER = {"rule_name": "run-as-non-root", "violation_count": 16, "evidence": []}
VALID = "CATEGORY: Continue Audit while remediation occurs\nRATIONALE: ok"
BAD = "CATEGORY: Proceed toward Enforce\nRATIONALE: bad"


def _fake_client(responses):
    calls = []

    def create(model, messages):
        calls.append(list(messages))
        text = responses[len(calls) - 1]
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    return client, calls


def test_enforce_only_allowed_at_low_risk():
    assert allowed_categories("Low") == CATEGORIES
    for level in ("Medium", "High"):
        allowed = allowed_categories(level)
        assert ENFORCE not in allowed
        assert len(allowed) == len(CATEGORIES) - 1


def test_valid_first_answer_uses_one_call(monkeypatch):
    client, calls = _fake_client([VALID])
    monkeypatch.setattr(recommender, "_get_client", lambda: client)
    result = recommend_rollout(CLUSTER, "explanation", 30)
    assert result["category"] == "Continue Audit while remediation occurs"
    assert result["risk_level"] == "Medium"
    assert len(calls) == 1
    assert "- Proceed toward Enforce" not in calls[0][0]["content"]


def test_disallowed_answer_is_corrected_on_retry(monkeypatch):
    client, calls = _fake_client([BAD, "CATEGORY: Delay enforcement\nRATIONALE: better"])
    monkeypatch.setattr(recommender, "_get_client", lambda: client)
    result = recommend_rollout(CLUSTER, "explanation", 30)
    assert result["category"] == "Delay enforcement"
    assert len(calls) == 2
    assert len(calls[1]) == 3
    assert "not permitted" in calls[1][2]["content"]


def test_malformed_answer_is_retried(monkeypatch):
    client, calls = _fake_client(["Sure, here you go.", VALID])
    monkeypatch.setattr(recommender, "_get_client", lambda: client)
    result = recommend_rollout(CLUSTER, "explanation", 30)
    assert result["category"] == "Continue Audit while remediation occurs"
    assert len(calls) == 2


def test_still_disallowed_after_retry_raises(monkeypatch):
    client, calls = _fake_client([BAD, BAD])
    monkeypatch.setattr(recommender, "_get_client", lambda: client)
    with pytest.raises(ValueError):
        recommend_rollout(CLUSTER, "explanation", 30)
    assert len(calls) == 2
