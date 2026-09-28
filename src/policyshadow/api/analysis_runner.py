"""Runs the scipy/torch-dependent analysis step in a separate plain Python process."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from policyshadow.core.schemas import Violation


def run_analysis(violations: list[Violation]) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        in_path = Path(tmp) / "violations.json"
        out_path = Path(tmp) / "clusters.json"
        in_path.write_text(
            json.dumps([v.model_dump(mode="json") for v in violations]), encoding="utf-8"
        )
        result = subprocess.run(
            [sys.executable, "-m", "policyshadow.api.analysis_worker", str(in_path), str(out_path)],
            capture_output=True, encoding="utf-8", errors="replace",
        )
        if result.returncode != 0:
            raise RuntimeError(f"analysis worker failed:\n{result.stderr}")
        return json.loads(out_path.read_text(encoding="utf-8"))
