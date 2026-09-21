"""Core data contracts for PolicyShadow: policy, historical record, violation."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Operation(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class PolicyEngineType(str, Enum):
    KYVERNO = "kyverno"
    OPA = "opa"


class AdmissionReviewRecord(BaseModel):
    record_id: str
    operation: Operation
    namespace: str
    resource_kind: str
    resource_name: str
    resource_manifest: dict[str, Any]
    timestamp: Optional[datetime] = None


class CandidatePolicy(BaseModel):
    policy_id: str
    name: str
    engine: PolicyEngineType
    policy_path: str
    mode: Optional[str] = "audit"


class Violation(BaseModel):
    violation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    record_id: str
    policy_id: str
    rule_name: str
    resource_kind: str
    resource_name: str
    namespace: str
    message: str
    severity: Optional[str] = None
    raw_result: Optional[dict[str, Any]] = None
