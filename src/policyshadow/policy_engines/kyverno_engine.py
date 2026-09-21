"""Kyverno policy engine: evaluates a record against a policy using the real Kyverno CLI."""

import json
import subprocess

from policyshadow.core.interfaces import PolicyEngine
from policyshadow.core.schemas import AdmissionReviewRecord, CandidatePolicy, Violation
from policyshadow.policy_engines.base import cleanup_tempfile, write_manifest_to_tempfile


class KyvernoPolicyEngine(PolicyEngine):
    def evaluate(self, record: AdmissionReviewRecord, policy: CandidatePolicy) -> list[Violation]:
        resource_path = write_manifest_to_tempfile(record.resource_manifest)
        try:
            result = subprocess.run(
                [
                    "kyverno", "apply", policy.policy_path,
                    "--resource", resource_path,
                    "--policy-report", "--output-format", "json",
                ],
                capture_output=True, text=True,
            )
            return self._parse(result.stdout, record, policy)
        finally:
            cleanup_tempfile(resource_path)

    @staticmethod
    def _parse(stdout: str, record: AdmissionReviewRecord, policy: CandidatePolicy) -> list[Violation]:
        text = stdout.strip()
        start = text.find("{")
        if start == -1:
            return []
        report = json.loads(text[start:])
        violations = []
        for entry in report.get("results", []):
            if entry.get("result") != "fail":
                continue
            violations.append(Violation(
                record_id=record.record_id,
                policy_id=policy.policy_id,
                rule_name=entry.get("rule", ""),
                resource_kind=record.resource_kind,
                resource_name=record.resource_name,
                namespace=record.namespace,
                message=entry.get("message", ""),
                severity=entry.get("severity"),
                raw_result=entry,
            ))
        return violations
