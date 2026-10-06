"""Requirements Analyst — draft stories with mandatory source citations."""

from __future__ import annotations

import re
from typing import Any

from ..models import EvidenceItem


def draft_stories(raw: str) -> dict[str, Any]:
    # Split requirement into rough capabilities
    sentences = [s.strip() for s in re.split(r"[.\n]+", raw) if len(s.strip()) > 20]
    if not sentences:
        sentences = [raw.strip()]

    stories: list[dict[str, Any]] = []
    for i, sentence in enumerate(sentences[:4], start=1):
        source = f"requirement://span/{i}"
        title = sentence[:72].rstrip(".")
        stories.append(
            {
                "id": f"US-{i}",
                "title": title,
                "user_story": f"As a user, I want {sentence[0].lower() + sentence[1:]} so that the product meets the stated need.",
                "acceptance_criteria": [
                    {
                        "text": f"Given the system is available, when the capability is used, then: {sentence}",
                        "source": source,
                    },
                    {
                        "text": "Negative path is handled with a clear error and no data loss.",
                        "source": source,
                    },
                ],
                "invest": {
                    "independent": True,
                    "negotiable": True,
                    "valuable": True,
                    "estimable": True,
                    "small": len(sentence) < 200,
                    "testable": True,
                },
            }
        )

    evidence = [
        EvidenceItem(
            kind="stories",
            summary=f"Drafted {len(stories)} user stories with citations",
            payload={"count": len(stories)},
            source="requirements-analyst",
            deterministic=False,
        ),
        EvidenceItem(
            kind="source_map",
            summary="Each criterion maps to a requirement span",
            payload={"spans": len(sentences)},
            source="requirements-analyst",
            deterministic=True,
        ),
    ]

    return {"stories": stories, "evidence": evidence, "backlog_payload": {"stories": stories}}
