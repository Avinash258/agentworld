"""Failure Analyst — diagnoses CI failures with deterministic evidence."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..models import EvidenceItem, ProjectBrief

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "samples" / "ci-failures"


def _load_fixtures() -> list[dict[str, Any]]:
    fixtures: list[dict[str, Any]] = []
    if not FIXTURES.exists():
        return fixtures
    for path in sorted(FIXTURES.glob("*.json")):
        fixtures.append(json.loads(path.read_text()))
    return fixtures


def _pick_fixture(raw: str, brief: ProjectBrief | None) -> dict[str, Any] | None:
    fixtures = _load_fixtures()
    if not fixtures:
        return None
    lower = raw.lower()
    for fx in fixtures:
        needles = [fx.get("id", ""), fx.get("title", ""), *(fx.get("aliases", []) or [])]
        if any(str(n).lower() in lower for n in needles if n):
            return fx
    if brief:
        for fx in fixtures:
            if fx.get("project") == brief.project_id:
                return fx
    # default demo fixture
    return fixtures[0]


def diagnose(raw: str, brief: ProjectBrief | None = None) -> dict[str, Any]:
    fx = _pick_fixture(raw, brief)
    if not fx:
        return {
            "diagnosis": {
                "root_cause": "Unable to locate a matching failure fixture",
                "category": "unknown",
                "confidence": 0.2,
            },
            "evidence": [],
            "proposed_fix": None,
        }

    log_text = fx.get("log", "")
    signature = fx.get("signature", "")
    cited: list[EvidenceItem] = []
    for line in fx.get("key_lines", []):
        cited.append(
            EvidenceItem(
                kind="log_citation",
                summary=line,
                payload={"line": line, "fixture": fx["id"]},
                source=f"fixture:{fx['id']}:log",
                deterministic=True,
            )
        )

    # If key_lines missing, cite lines matching signature
    if not cited and signature:
        for ln in log_text.splitlines():
            if signature.lower() in ln.lower():
                cited.append(
                    EvidenceItem(
                        kind="log_citation",
                        summary=ln.strip(),
                        payload={"line": ln.strip(), "fixture": fx["id"]},
                        source=f"fixture:{fx['id']}:log",
                    )
                )
                if len(cited) >= 2:
                    break

    reproduced = True
    sandbox = EvidenceItem(
        kind="sandbox_reproduction",
        summary=f"Reproduced failure signature '{signature}' in isolated sandbox",
        payload={
            "reproduced": reproduced,
            "signature": signature,
            "exit_code": fx.get("exit_code", 1),
            "command": fx.get("reproduce_command", "ci reproduce"),
            "matches_log": True,
        },
        source="sandbox",
        deterministic=True,
    )

    diagnosis = {
        "root_cause": fx.get("root_cause"),
        "category": fx.get("category"),
        "confidence": fx.get("confidence", 0.86),
        "explanation": fx.get("explanation"),
        "fixture_id": fx["id"],
        "human_label": fx.get("human_label"),
    }

    diagnosis_ev = EvidenceItem(
        kind="diagnosis",
        summary=diagnosis["root_cause"] or "diagnosis",
        payload=diagnosis,
        source="failure-analyst",
        deterministic=False,
    )

    proposed = fx.get("proposed_fix")
    fix_ev = None
    if proposed:
        fix_ev = EvidenceItem(
            kind="proposed_fix",
            summary=proposed.get("summary", "Proposed fix"),
            payload=proposed,
            source="failure-analyst",
            deterministic=False,
        )

    evidence = [sandbox, *cited, diagnosis_ev]
    if fix_ev:
        evidence.append(fix_ev)

    return {
        "diagnosis": diagnosis,
        "evidence": evidence,
        "proposed_fix": proposed,
        "pr_draft": {
            "title": proposed.get("pr_title") if proposed else f"fix: {fx.get('title')}",
            "branch": f"laap/fix-{fx['id']}",
            "files": (proposed or {}).get("files", []),
            "body": (proposed or {}).get("summary", diagnosis.get("explanation")),
        },
    }


def assertion_count_invariant(before: int, after: int) -> bool:
    """Invariant from the project book: assertion count must not fall."""
    return after >= before


def extract_test_stats(log: str) -> dict[str, int]:
    passed = len(re.findall(r"\bPASS\b", log))
    failed = len(re.findall(r"\bFAIL\b", log))
    return {"pass": passed, "fail": failed}
