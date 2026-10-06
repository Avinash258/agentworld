"""Policy engine — allow, deny, or require human approval for every sensitive action."""

from __future__ import annotations

from typing import Any

from .models import ApprovalRequest, PolicyDecision, new_id
from .packs import get_pack

# Hard denies — agents never see or act on these
ALWAYS_DENY = {
    "read_secret",
    "write_secret",
    "payment",
    "delete_production_data",
    "disable_policy",
    "exfiltrate",
}


def evaluate_action(
    pack_name: str,
    action: str,
    arguments: dict[str, Any] | None = None,
) -> tuple[PolicyDecision, str]:
    if action in ALWAYS_DENY:
        return PolicyDecision.DENY, f"Action '{action}' is permanently denied by platform policy."

    # Path / secret heuristics
    args = arguments or {}
    for key, value in args.items():
        text = str(value).lower()
        if any(s in text for s in ("password", "api_key", "secret", "private_key", "/etc/shadow")):
            return PolicyDecision.DENY, "Arguments appear to reference secrets; denied."

    pack = get_pack(pack_name) or {}
    approval_actions: set[str] = set()
    for wf in pack.get("workflows", []):
        for a in wf.get("human_approval_for", []):
            approval_actions.add(a)

    # Platform-wide irreversible defaults
    approval_actions.update(
        {
            "open_pull_request",
            "merge_pull_request",
            "deploy",
            "delete_data",
            "write_backlog",
            "paid_rerun",
            "push_branch",
        }
    )

    if action in approval_actions:
        return (
            PolicyDecision.REQUIRE_APPROVAL,
            f"Action '{action}' is irreversible or externally visible; human approval required.",
        )

    return PolicyDecision.ALLOW, f"Action '{action}' allowed under pack '{pack_name}'."


def make_approval(action: str, arguments: dict[str, Any], reason: str) -> ApprovalRequest:
    return ApprovalRequest(
        id=new_id("apr"),
        action=action,
        arguments=arguments,
        reason=reason,
        status="pending",
    )
