"""Smoke tests for evidence gating and policy."""

from app.models import CreateTaskRequest, ApprovalDecision
from app.runtime import create_and_run, decide_approval, ensure_sample_brief
from app.models import TaskState, EvidenceStatus
from app.policy import evaluate_action
from app.models import PolicyDecision


def test_ci_diagnosis_awaits_approval_with_verified_evidence():
    ensure_sample_brief()
    task = create_and_run(
        CreateTaskRequest(
            request="main is red again, can someone check the payments pipeline?",
            project_id="sample-payments-api",
            pack="delivery-core",
        )
    )
    assert task.evidence_status == EvidenceStatus.VERIFIED
    assert task.state == TaskState.AWAITING_APPROVAL
    assert task.approvals and task.approvals[0].action == "open_pull_request"
    assert task.diagnosis and task.diagnosis["category"] == "infrastructure"


def test_approval_completes_task():
    ensure_sample_brief()
    task = create_and_run(
        CreateTaskRequest(
            request="main is red again",
            project_id="sample-payments-api",
        )
    )
    apr = task.approvals[0]
    done = decide_approval(
        task.id, apr.id, ApprovalDecision(approve=True, decided_by="tester")
    )
    assert done.state == TaskState.COMPLETED
    assert done.approvals[0].token


def test_secrets_denied():
    decision, _ = evaluate_action("delivery-core", "read_secret", {})
    assert decision == PolicyDecision.DENY


def test_ba_pack_stories():
    ensure_sample_brief()
    task = create_and_run(
        CreateTaskRequest(
            request="Users need to pause a recurring payment and receive email confirmation.",
            pack="ba-product",
            workflow="requirement-to-stories",
        )
    )
    assert task.stories
    assert task.evidence_status == EvidenceStatus.VERIFIED
    assert task.state == TaskState.AWAITING_APPROVAL
