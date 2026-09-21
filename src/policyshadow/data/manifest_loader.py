"""Loads Kubernetes manifest YAML files from a directory as AdmissionReviewRecords."""

from pathlib import Path

import yaml

from policyshadow.core.schemas import AdmissionReviewRecord, Operation


def load_manifests(directory: str) -> list[AdmissionReviewRecord]:
    records = []
    for path in sorted(Path(directory).glob("*.yaml")):
        manifest = yaml.safe_load(path.read_text())
        records.append(AdmissionReviewRecord(
            record_id=path.stem,
            operation=Operation.CREATE,
            namespace=manifest["metadata"]["namespace"],
            resource_kind=manifest["kind"],
            resource_name=manifest["metadata"]["name"],
            resource_manifest=manifest,
        ))
    return records
