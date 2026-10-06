"""Pydantic models for the Local Agentic AI Platform runtime."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class TaskState(str, Enum):
    RECEIVED = "received"
    STRUCTURING = "structuring"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


class EvidenceStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    PARTIAL = "partial"


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class StructuredPrompt(BaseModel):
    original: str
    goal: str
    project: str | None = None
    scope: str | None = None
    constraints: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    evidence_required: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    channel: str = "human_to_agent"
    risk: str = "low"
    pack: str = "delivery-core"
    workflow: str = "ci-failure-diagnosis"
    intent_preserved: bool = True
    diff_summary: str = ""


class PlanStep(BaseModel):
    id: str
    agent: str
    action: str
    needs_approval: bool = False
    status: str = "pending"
    result: dict[str, Any] | None = None


class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: new_id("ev"))
    kind: str
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)
    source: str
    deterministic: bool = True
    created_at: datetime = Field(default_factory=utcnow)


class ValidationResult(BaseModel):
    validator_id: str
    passed: bool
    detail: str


class ApprovalRequest(BaseModel):
    id: str = Field(default_factory=lambda: new_id("apr"))
    action: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    reason: str
    status: str = "pending"  # pending | approved | denied
    decided_by: str | None = None
    decided_at: datetime | None = None
    token: str | None = None


class AuditEvent(BaseModel):
    id: str = Field(default_factory=lambda: new_id("aud"))
    at: datetime = Field(default_factory=utcnow)
    actor: str
    event: str
    detail: dict[str, Any] = Field(default_factory=dict)


class ProjectBrief(BaseModel):
    project_id: str
    name: str
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    build_command: str | None = None
    test_command: str | None = None
    ci_system: str | None = None
    conventions: list[str] = Field(default_factory=list)
    dangerous_paths: list[str] = Field(default_factory=list)
    glossary: dict[str, str] = Field(default_factory=dict)
    facts: list[dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utcnow)
    provenance_note: str = "Executed facts outrank CI config, code, then documents."


class Task(BaseModel):
    id: str = Field(default_factory=lambda: new_id("task"))
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    requester: str = "demo-user"
    raw_request: str
    state: TaskState = TaskState.RECEIVED
    pack: str = "delivery-core"
    workflow: str = "ci-failure-diagnosis"
    project_id: str | None = None
    structured: StructuredPrompt | None = None
    plan: list[PlanStep] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    evidence_status: EvidenceStatus = EvidenceStatus.PENDING
    validations: list[ValidationResult] = Field(default_factory=list)
    approvals: list[ApprovalRequest] = Field(default_factory=list)
    diagnosis: dict[str, Any] | None = None
    stories: list[dict[str, Any]] | None = None
    audit: list[AuditEvent] = Field(default_factory=list)
    error: str | None = None

    def touch(self) -> None:
        self.updated_at = utcnow()

    def audit_log(self, actor: str, event: str, detail: dict[str, Any] | None = None) -> None:
        self.audit.append(AuditEvent(actor=actor, event=event, detail=detail or {}))
        self.touch()


class CreateTaskRequest(BaseModel):
    request: str
    requester: str = "demo-user"
    pack: str | None = None
    workflow: str | None = None
    project_id: str | None = "sample-payments-api"
    auto_run: bool = True


class ApprovalDecision(BaseModel):
    approve: bool
    decided_by: str = "human-lead"
    note: str | None = None


class OnboardRequest(BaseModel):
    project_path: str
    project_id: str | None = None
    name: str | None = None
