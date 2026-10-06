"""Team Pack loader — configuration bundles, not engine code."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
PACKS_DIR = ROOT / "packs"


def list_packs() -> list[dict[str, Any]]:
    packs: list[dict[str, Any]] = []
    if not PACKS_DIR.exists():
        return packs
    for path in sorted(PACKS_DIR.glob("*/pack.yaml")):
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        data["_path"] = str(path.parent)
        packs.append(data)
    return packs


def get_pack(name: str) -> dict[str, Any] | None:
    for pack in list_packs():
        if pack.get("name") == name:
            return pack
    return None


def workflow_for(pack_name: str, workflow_id: str) -> dict[str, Any] | None:
    pack = get_pack(pack_name)
    if not pack:
        return None
    for wf in pack.get("workflows", []):
        if wf.get("id") == workflow_id:
            return wf
    return None


def infer_pack_and_workflow(text: str) -> tuple[str, str]:
    lower = text.lower()
    story_signals = ("user stor", "acceptance criteria", "requirement", "as a ", "backlog", "epic")
    if any(s in lower for s in story_signals):
        return "ba-product", "requirement-to-stories"
    return "delivery-core", "ci-failure-diagnosis"
