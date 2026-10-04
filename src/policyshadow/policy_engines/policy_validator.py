"""Validates candidate Kyverno policy YAML before it is stored or run.

Uses real yaml parsing for syntax, a minimal schema check for shape,
and the actual Kyverno CLI for a real dry-run check - never a
hand-written Kyverno parser.
"""

import tempfile
from pathlib import Path

import yaml

from policyshadow.data.synthetic_records import SYNTHETIC_RECORDS
from policyshadow.policy_engines.base import cleanup_tempfile
from policyshadow.policy_engines.kyverno_engine import KyvernoPolicyEngine
from policyshadow.core.schemas import CandidatePolicy, PolicyEngineType


def validate_policy_yaml(policy_text: str) -> tuple[bool, str | None]:
    if not policy_text or not policy_text.strip():
        return False, "Policy content is empty."

    if len(policy_text) > 100_000:
        return False, "Policy content is too large."

    try:
        parsed = yaml.safe_load(policy_text)
    except yaml.YAMLError as e:
        return False, f"Invalid YAML syntax: {e}"

    if not isinstance(parsed, dict):
        return False, "Policy must be a single YAML object."

    api_version = parsed.get("apiVersion", "")
    kind = parsed.get("kind", "")
    if not str(api_version).startswith("kyverno.io/"):
        return False, f"apiVersion must be a kyverno.io/* value, got: {api_version!r}"
    if kind not in ("ClusterPolicy", "Policy"):
        return False, f"kind must be ClusterPolicy or Policy, got: {kind!r}"
    if not parsed.get("spec", {}).get("rules"):
        return False, "Policy must define at least one rule under spec.rules."
    if not parsed.get("metadata", {}).get("name"):
        return False, "Policy must have metadata.name set."

    policy_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(policy_text)
            policy_path = f.name

        candidate = CandidatePolicy(
            policy_id="validation-check", name=parsed["metadata"]["name"],
            engine=PolicyEngineType.KYVERNO, policy_path=policy_path,
        )
        engine = KyvernoPolicyEngine()
        sample_record = SYNTHETIC_RECORDS[0]
        engine.evaluate(sample_record, candidate)
    except Exception as e:
        return False, f"Kyverno rejected this policy: {e}"
    finally:
        if policy_path:
            Path(policy_path).unlink(missing_ok=True)

    return True, None
