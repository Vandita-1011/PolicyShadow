"""Deterministic tests for retry behavior, using a fake subprocess.run."""

from types import SimpleNamespace

import pytest

from policyshadow.api import analysis_runner
from policyshadow.core.schemas import Violation


def _violation():
    return Violation(
        record_id="r1", policy_id="p1", rule_name="x",
        resource_kind="Pod", resource_name="p", namespace="default", message="m",
    )


def test_succeeds_on_first_attempt(monkeypatch, tmp_path):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        out_path = cmd[-1]
        __import__("pathlib").Path(out_path).write_text("[]")
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(analysis_runner.subprocess, "run", fake_run)
    result = analysis_runner.run_analysis([_violation()])
    assert result == []
    assert len(calls) == 1


def test_succeeds_on_second_attempt_after_one_failure(monkeypatch):
    attempts = []

    def fake_run(cmd, **kwargs):
        attempts.append(1)
        out_path = cmd[-1]
        if len(attempts) == 1:
            return SimpleNamespace(returncode=1, stderr="blocked")
        __import__("pathlib").Path(out_path).write_text("[]")
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(analysis_runner.subprocess, "run", fake_run)
    monkeypatch.setattr(analysis_runner.time, "sleep", lambda s: None)
    result = analysis_runner.run_analysis([_violation()])
    assert result == []
    assert len(attempts) == 2


def test_raises_after_max_attempts_exhausted(monkeypatch):
    attempts = []

    def fake_run(cmd, **kwargs):
        attempts.append(1)
        return SimpleNamespace(returncode=1, stderr="still blocked")

    monkeypatch.setattr(analysis_runner.subprocess, "run", fake_run)
    monkeypatch.setattr(analysis_runner.time, "sleep", lambda s: None)
    with pytest.raises(RuntimeError, match="still blocked"):
        analysis_runner.run_analysis([_violation()])
    assert len(attempts) == analysis_runner.MAX_ATTEMPTS
