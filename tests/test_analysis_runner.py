"""Checks the subprocess boundary and guards against re-importing the blocked stack."""

import subprocess
import sys

from policyshadow.api.analysis_runner import run_analysis
from policyshadow.data.multi_policy_replay import replay_all_policies


def test_api_process_does_not_import_blocked_stack():
    code = (
        "import sys, policyshadow.api.app; "
        "print([m for m in ('scipy','sklearn','torch','sentence_transformers') if m in sys.modules])"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]"


def test_subprocess_analysis_matches_known_clusters(tmp_path):
    violations = replay_all_policies(str(tmp_path / "violations.json"))
    packaged = run_analysis(violations)

    assert len(packaged) == 2
    counts = {c["rule_name"]: c["violation_count"] for c in packaged}
    assert counts == {"restrict-privileged-containers": 15, "require-non-root": 16}
    for c in packaged:
        assert len(c["evidence"]) == 3
