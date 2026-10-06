"""Planner — short verifiable plans; single agent by default."""

from __future__ import annotations

from ..models import PlanStep, StructuredPrompt, new_id


def build_plan(structured: StructuredPrompt) -> list[PlanStep]:
    if structured.workflow == "requirement-to-stories":
        return [
            PlanStep(
                id=new_id("step"),
                agent="requirements-analyst",
                action="draft_stories_with_citations",
            ),
            PlanStep(
                id=new_id("step"),
                agent="verifier",
                action="validate_evidence",
            ),
            PlanStep(
                id=new_id("step"),
                agent="policy",
                action="write_backlog",
                needs_approval=True,
            ),
        ]

    # CI failure diagnosis — one worker by default
    return [
        PlanStep(
            id=new_id("step"),
            agent="failure-analyst",
            action="diagnose_ci_failure",
        ),
        PlanStep(
            id=new_id("step"),
            agent="verifier",
            action="validate_evidence",
        ),
        PlanStep(
            id=new_id("step"),
            agent="policy",
            action="open_pull_request",
            needs_approval=True,
        ),
    ]
