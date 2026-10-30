from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import hashlib
import json
import uuid


class Mode(str, Enum):
    PLAN = "PLAN"
    VERIFY = "VERIFY"
    APPLY = "APPLY"
    ASSURE = "ASSURE"


class Classification(str, Enum):
    VERIFIED = "VERIFIED"
    REPORTED = "REPORTED"
    INFERRED = "INFERRED"
    BLOCKED = "BLOCKED"
    UNTESTED = "UNTESTED"


class Disposition(str, Enum):
    SUCCESS = "SUCCESS"
    RETRY = "RETRY"
    STOP = "STOP"
    REQUIRE_HUMAN = "REQUIRE_HUMAN"
    BLOCKED = "BLOCKED"
    INDETERMINATE = "INDETERMINATE"


class LifecycleState(str, Enum):
    DEFINED = "DEFINED"
    APPROVED = "APPROVED"
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    MEASURED = "MEASURED"
    COMPLIANT = "COMPLIANT"
    VIOLATION = "VIOLATION"
    CONTAIN = "CONTAIN"
    RECOVER = "RECOVER"
    RETIRED = "RETIRED"


@dataclass
class EvidenceRecord:
    evidence_id: str
    classification: Classification
    subject: str
    observation: Dict[str, Any]
    evidence_hash: str
    timestamp: str
    parent_operation_id: Optional[str] = None

    @staticmethod
    def create(
        classification: Classification,
        subject: str,
        observation: Dict[str, Any],
        parent_operation_id: Optional[str] = None,
    ) -> "EvidenceRecord":
        payload = json.dumps(observation, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256(payload.encode()).hexdigest()
        return EvidenceRecord(
            evidence_id=str(uuid.uuid4()),
            classification=classification,
            subject=subject,
            observation=observation,
            evidence_hash=h,
            timestamp=datetime.now(timezone.utc).isoformat(),
            parent_operation_id=parent_operation_id,
        )


@dataclass
class Authorization:
    required: bool = True
    approver: Optional[str] = None
    approval_ref: Optional[str] = None
    status: str = "PENDING"  # PENDING | GRANTED | DENIED | NOT_REQUIRED


@dataclass
class OperationRecord:
    operation_id: str
    feature: str
    mode: Mode
    desired_state_revision: str
    preconditions: List[Dict[str, Any]] = field(default_factory=list)
    authorization: Authorization = field(default_factory=Authorization)
    action: Dict[str, Any] = field(default_factory=dict)
    observations: List[Dict[str, Any]] = field(default_factory=list)
    postconditions: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[EvidenceRecord] = field(default_factory=list)
    classification: Classification = Classification.UNTESTED
    disposition: Disposition = Disposition.INDETERMINATE
    lifecycle_state: LifecycleState = LifecycleState.DEFINED
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["mode"] = self.mode.value
        d["classification"] = self.classification.value
        d["disposition"] = self.disposition.value
        d["lifecycle_state"] = self.lifecycle_state.value
        return d
