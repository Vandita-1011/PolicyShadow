"""Runs the scipy/torch-dependent analysis step in a separate plain Python process.

Retries on failure, since Windows Smart App Control (in evaluation mode)
can inconsistently block a compiled dependency file on some runs but not
others - a retry often succeeds without any code change needed.
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from policyshadow.core.schemas import Violation

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2


def run_analysis(violations: list[Violation]) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        in_path = Path(tmp) / "violations.json"
        out_path = Path(tmp) / "clusters.json"
        in_path.write_text(
            json.dumps([v.model_dump(mode="json") for v in violations]), encoding="utf-8"
        )

        last_error = ""
        for attempt in range(1, MAX_ATTEMPTS + 1):
            result = subprocess.run(
                [sys.executable, "-m", "policyshadow.api.analysis_worker", str(in_path), str(out_path)],
                capture_output=True, encoding="utf-8", errors="replace",
            )
            if result.returncode == 0:
                return json.loads(out_path.read_text(encoding="utf-8"))
            last_error = result.stderr
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)

        raise RuntimeError(
            f"analysis worker failed after {MAX_ATTEMPTS} attempts:\n{last_error}"
        )
