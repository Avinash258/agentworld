"""Prompt Architect — structures every request without changing intent."""

from __future__ import annotations

import re

from ..models import ProjectBrief, StructuredPrompt
from ..packs import infer_pack_and_workflow


def structure_request(
    raw: str,
    brief: ProjectBrief | None = None,
    pack: str | None = None,
    workflow: str | None = None,
) -> StructuredPrompt:
    inferred_pack, inferred_wf = infer_pack_and_workflow(raw)
    pack = pack or inferred_pack
    workflow = workflow or inferred_wf

    project = brief.project_id if brief else None
    assumptions: list[str] = []
    questions: list[str] = []
    constraints: list[str] = []
    evidence_required: list[str] = []
    acceptance: list[str] = []

    lower = raw.lower()
    risk = "low"
    if any(w in lower for w in ("prod", "production", "delete", "merge", "deploy")):
        risk = "high"
        constraints.append("No irreversible actions without human approval.")

    if workflow == "ci-failure-diagnosis":
        goal = (
            "Diagnose the CI/build failure, reproduce it in the sandbox, "
            "cite supporting log lines, classify the root cause, and propose a fix."
        )
        evidence_required = [
            "sandbox reproduction of the failure signature",
            "at least two cited log lines",
            "root_cause, category, and confidence fields",
        ]
        acceptance = [
            "Root cause is classified against the log signature",
            "Failure is reproduced in the sandbox",
            "Proposed fix is scoped to allowed paths",
            "Opening a PR requires human approval",
        ]
        if "main" in lower or "red" in lower:
            assumptions.append("Target branch is main / the default integration branch.")
        if brief and brief.ci_system:
            assumptions.append(f"Project uses {brief.ci_system} (from Project Brief).")
        # Ambiguity: which pipeline?
        if not re.search(r"(job|pipeline|workflow|build)[\w\-/ ]*", lower) and "fixture" not in lower:
            if "payments" not in lower and not (brief and brief.project_id):
                questions.append("Which project or pipeline failed?")
    else:
        goal = (
            "Turn the requirement into INVEST-shaped user stories with "
            "acceptance criteria that each cite a source."
        )
        evidence_required = [
            "every acceptance criterion cites a source",
            "stories include title, narrative, and criteria",
        ]
        acceptance = [
            "Stories are independently reviewable",
            "No orphan requirements",
            "Writing to the backlog requires human approval",
        ]

    if brief:
        constraints.extend(brief.conventions[:3])

    # Never invent — if too vague and no brief, ask
    if len(raw.strip()) < 12 and not brief:
        questions.append("Can you describe the task with a bit more detail?")

    diff_bits = [
        "Restated goal with output contract",
        "Added evidence requirements from Team Pack validators",
    ]
    if assumptions:
        diff_bits.append(f"Stated {len(assumptions)} assumption(s)")
    if questions:
        diff_bits.append(f"Queued {len(questions)} clarification(s)")

    return StructuredPrompt(
        original=raw,
        goal=goal,
        project=project or (brief.name if brief else None),
        scope="bounded diagnosis and proposal" if workflow == "ci-failure-diagnosis" else "draft only",
        constraints=constraints,
        acceptance_criteria=acceptance,
        evidence_required=evidence_required,
        assumptions=assumptions,
        questions=questions[:3],
        risk=risk,
        pack=pack,
        workflow=workflow,
        intent_preserved=True,
        diff_summary="; ".join(diff_bits),
    )
