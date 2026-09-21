"""Shared helpers for policy engine implementations."""

import tempfile
from pathlib import Path

import yaml


def write_manifest_to_tempfile(manifest: dict) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.safe_dump(manifest, f)
        return f.name


def cleanup_tempfile(path: str) -> None:
    Path(path).unlink(missing_ok=True)
