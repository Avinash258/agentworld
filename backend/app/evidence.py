"""Evidence store helpers and deterministic validators."""

from __future__ import annotations

from typing import Any

from .models import EvidenceItem, EvidenceStatus, ValidationResult
from .packs import workflow_for


def validate_evidence(
    pack_name: str,
    workflow_id: str,
    evidence: list[EvidenceItem],
    diagnosis: dict[str, Any] | None = None,
    stories: list[dict[str, Any]] | None = None,
) -> tuple[EvidenceStatus, list[ValidationResult]]:
    wf = workflow_for(pack_name, workflow_id) or {}
    validators = wf.get("evidence_validators", [])
    results: list[ValidationResult] = []

    kinds = {e.kind for e in evidence}
    citations = [e for e in evidence if e.kind == "log_citation"]
    sandbox = next((e for e in evidence if e.kind == "sandbox_reproduction"), None)

    for v in validators:
        vid = v.get("id", "unknown")
        vtype = v.get("type")

        if vtype == "sandbox_exit_match":
            ok = sandbox is not None and bool(sandbox.payload.get("reproduced"))
            results.append(
                ValidationResult(
                    validator_id=vid,
                    passed=ok,
                    detail="Sandbox reproduced the failure signature"
                    if ok
                    else "Missing or failed sandbox reproduction",
                )
            )
        elif vtype == "min_citations":
            need = int(v.get("min", 2))
            ok = len(citations) >= need
            results.append(
                ValidationResult(
                    validator_id=vid,
                    passed=ok,
                    detail=f"{len(citations)} citations (need {need})",
                )
            )
        elif vtype == "required_fields":
            fields = v.get("fields", [])
            missing = [f for f in fields if not (diagnosis or {}).get(f)]
            ok = not missing
            results.append(
                ValidationResult(
                    validator_id=vid,
                    passed=ok,
                    detail="All classification fields present" if ok else f"Missing: {missing}",
                )
            )
        elif vtype == "every_criterion_cites_source":
            ok = True
            detail = "All criteria cite sources"
            if not stories:
                ok = False
                detail = "No stories produced"
            else:
                for story in stories:
                    for ac in story.get("acceptance_criteria", []):
                        if not ac.get("source"):
                            ok = False
                            detail = "At least one criterion lacks a source citation"
                            break
            results.append(ValidationResult(validator_id=vid, passed=ok, detail=detail))
        elif vtype == "invest_checks":
            ok = bool(stories) and all(
                story.get("title") and story.get("user_story") and story.get("acceptance_criteria")
                for story in (stories or [])
            )
            results.append(
                ValidationResult(
                    validator_id=vid,
                    passed=ok,
                    detail="Stories have title, narrative, and criteria"
                    if ok
                    else "INVEST shape incomplete",
                )
            )
        else:
            results.append(
                ValidationResult(
                    validator_id=vid,
                    passed="diagnosis" in kinds or "stories" in kinds,
                    detail=f"Generic check for validator type {vtype}",
                )
            )

    if not validators:
        status = EvidenceStatus.VERIFIED if evidence else EvidenceStatus.PENDING
        return status, results

    if all(r.passed for r in results):
        return EvidenceStatus.VERIFIED, results
    if any(r.passed for r in results):
        return EvidenceStatus.PARTIAL, results
    return EvidenceStatus.REJECTED, results
