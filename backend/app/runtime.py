"""Agent Runtime — task lifecycle with evidence gating and policy."""

from __future__ import annotations

from typing import Any

from .agents import failure_analyst, onboarding, planner, prompt_architect, requirements_analyst
from .evidence import validate_evidence
from .models import (
    ApprovalDecision,
    CreateTaskRequest,
    EvidenceStatus,
    OnboardRequest,
    PolicyDecision,
    Task,
    TaskState,
    new_id,
    utcnow,
)
from .packs import get_pack
from .policy import evaluate_action, make_approval
from .store import store


def ensure_sample_brief() -> None:
    if store.get_brief("sample-payments-api"):
        return
    brief = onboarding.onboard_project(
        "samples/projects/payments-api",
        project_id="sample-payments-api",
        name="Payments API",
    )
    store.save_brief(brief)


def create_and_run(req: CreateTaskRequest) -> Task:
    ensure_sample_brief()
    brief = store.get_brief(req.project_id) if req.project_id else None

    task = Task(
        raw_request=req.request,
        requester=req.requester,
        project_id=req.project_id,
        pack=req.pack or "delivery-core",
        workflow=req.workflow or "ci-failure-diagnosis",
    )
    task.audit_log(req.requester, "task_created", {"request": req.request})
    store.save_task(task)

    if not req.auto_run:
        return task

    return run_task(task.id)


def run_task(task_id: str) -> Task:
    task = store.get_task(task_id)
    if not task:
        raise KeyError(task_id)

    try:
        # 1) Prompt Architect
        task.state = TaskState.STRUCTURING
        task.audit_log("prompt-architect", "structuring_started")
        brief = store.get_brief(task.project_id) if task.project_id else None
        structured = prompt_architect.structure_request(
            task.raw_request,
            brief=brief,
            pack=task.pack if task.pack else None,
            workflow=task.workflow if task.workflow else None,
        )
        task.structured = structured
        task.pack = structured.pack
        task.workflow = structured.workflow
        task.audit_log(
            "prompt-architect",
            "structuring_completed",
            {"diff": structured.diff_summary, "questions": structured.questions},
        )
        store.save_task(task)

        # If clarifications are mandatory and blocking — escalate lightly for demo
        # but continue with assumptions when we have a brief/fixture.

        # 2) Planner
        task.state = TaskState.PLANNING
        task.plan = planner.build_plan(structured)
        task.audit_log("planner", "plan_ready", {"steps": [s.model_dump() for s in task.plan]})
        store.save_task(task)

        # 3) Execute worker steps
        task.state = TaskState.EXECUTING
        for step in task.plan:
            if step.agent == "failure-analyst":
                result = failure_analyst.diagnose(task.raw_request, brief)
                task.diagnosis = result["diagnosis"]
                task.evidence.extend(result["evidence"])
                step.result = {
                    "diagnosis": result["diagnosis"],
                    "pr_draft": result.get("pr_draft"),
                }
                step.status = "done"
                task.audit_log("failure-analyst", "diagnosis_ready", result["diagnosis"])
            elif step.agent == "requirements-analyst":
                result = requirements_analyst.draft_stories(task.raw_request)
                task.stories = result["stories"]
                task.evidence.extend(result["evidence"])
                step.result = {"stories": result["stories"]}
                step.status = "done"
                task.audit_log(
                    "requirements-analyst",
                    "stories_ready",
                    {"count": len(result["stories"])},
                )
            elif step.agent == "verifier":
                task.state = TaskState.VERIFYING
                status, validations = validate_evidence(
                    task.pack,
                    task.workflow,
                    task.evidence,
                    diagnosis=task.diagnosis,
                    stories=task.stories,
                )
                task.validations = validations
                task.evidence_status = status
                step.result = {"status": status.value, "validations": [v.model_dump() for v in validations]}
                step.status = "done"
                task.audit_log(
                    "verifier",
                    "evidence_checked",
                    {"status": status.value, "validations": step.result["validations"]},
                )
                if status != EvidenceStatus.VERIFIED:
                    task.state = TaskState.FAILED
                    task.error = "Evidence gating rejected or incomplete; result not accepted."
                    store.save_task(task)
                    return task
            elif step.agent == "policy":
                decision, reason = evaluate_action(
                    task.pack,
                    step.action,
                    _action_args(task, step.action),
                )
                if decision == PolicyDecision.DENY:
                    step.status = "denied"
                    task.state = TaskState.REJECTED
                    task.error = reason
                    task.audit_log("policy", "denied", {"action": step.action, "reason": reason})
                    store.save_task(task)
                    return task
                if decision == PolicyDecision.REQUIRE_APPROVAL:
                    apr = make_approval(step.action, _action_args(task, step.action), reason)
                    task.approvals.append(apr)
                    step.status = "awaiting_approval"
                    task.state = TaskState.AWAITING_APPROVAL
                    task.audit_log(
                        "policy",
                        "approval_required",
                        {"approval_id": apr.id, "action": step.action},
                    )
                    store.save_task(task)
                    return task
                step.status = "done"
            store.save_task(task)

        task.state = TaskState.COMPLETED
        task.audit_log("runtime", "completed")
        store.save_task(task)
        return task
    except Exception as exc:  # noqa: BLE001 — surface in task record for demo
        task.state = TaskState.FAILED
        task.error = str(exc)
        task.audit_log("runtime", "failed", {"error": str(exc)})
        store.save_task(task)
        return task


def _action_args(task: Task, action: str) -> dict[str, Any]:
    if action == "open_pull_request":
        draft = {}
        for step in task.plan:
            if step.result and "pr_draft" in (step.result or {}):
                draft = step.result["pr_draft"]
        return draft or {"title": "proposed fix", "branch": "laap/fix"}
    if action == "write_backlog":
        return {"stories": task.stories or []}
    return {}


def decide_approval(task_id: str, approval_id: str, decision: ApprovalDecision) -> Task:
    task = store.get_task(task_id)
    if not task:
        raise KeyError(task_id)

    apr = next((a for a in task.approvals if a.id == approval_id), None)
    if not apr:
        raise KeyError(approval_id)
    if apr.status != "pending":
        return task

    apr.decided_by = decision.decided_by
    apr.decided_at = utcnow()
    if decision.approve:
        apr.status = "approved"
        apr.token = new_id("tok")
        task.state = TaskState.APPROVED
        # Mark plan step done and complete
        for step in task.plan:
            if step.needs_approval and step.status == "awaiting_approval":
                step.status = "approved"
                step.result = {"token": apr.token, "note": decision.note}
        task.state = TaskState.COMPLETED
        task.audit_log(
            decision.decided_by,
            "approval_granted",
            {"approval_id": apr.id, "action": apr.action, "token": apr.token},
        )
    else:
        apr.status = "denied"
        task.state = TaskState.REJECTED
        task.error = decision.note or "Human denied the irreversible action."
        for step in task.plan:
            if step.needs_approval and step.status == "awaiting_approval":
                step.status = "denied"
        task.audit_log(
            decision.decided_by,
            "approval_denied",
            {"approval_id": apr.id, "action": apr.action},
        )

    store.save_task(task)
    return task


def onboard(req: OnboardRequest):
    brief = onboarding.onboard_project(req.project_path, req.project_id, req.name)
    store.save_brief(brief)
    return brief


def platform_status() -> dict[str, Any]:
    ensure_sample_brief()
    packs = []
    from .packs import list_packs

    for p in list_packs():
        packs.append(
            {
                "name": p.get("name"),
                "version": p.get("version"),
                "owner": p.get("owner"),
                "workflows": [w.get("id") for w in p.get("workflows", [])],
            }
        )
    return {
        "product": "Local Agentic AI Platform",
        "version": "0.1.0-phase1",
        "gap_closed": [
            "Runs on company-controlled infrastructure (local process)",
            "Evidence gating before accepting agent results",
            "Human-approval policy engine for irreversible actions",
            "Multi-team configuration via Team Packs",
            "Prompt Architect + Project Onboarding platform agents",
        ],
        "packs": packs,
        "tasks": len(store.tasks),
        "briefs": len(store.briefs),
        "models": "local-first; cloud models optional under policy (demo uses deterministic fixtures)",
    }
