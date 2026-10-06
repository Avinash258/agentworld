"""Project Onboarding agent — executed facts outrank documents."""

from __future__ import annotations

import json
import re
from pathlib import Path

from ..models import ProjectBrief, new_id


ROOT = Path(__file__).resolve().parents[3]


def _detect_languages(files: list[str]) -> list[str]:
    langs: set[str] = set()
    mapping = {
        ".py": "Python",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".js": "JavaScript",
        ".go": "Go",
        ".java": "Java",
        ".rs": "Rust",
    }
    for f in files:
        for ext, name in mapping.items():
            if f.endswith(ext):
                langs.add(name)
    return sorted(langs)


def _read_safe_text(path: Path, limit: int = 8000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def onboard_project(
    project_path: str,
    project_id: str | None = None,
    name: str | None = None,
) -> ProjectBrief:
    path = Path(project_path)
    if not path.is_absolute():
        path = (ROOT / project_path).resolve()

    if not path.exists():
        # Fall back to bundled sample project metadata
        sample = ROOT / "samples" / "projects" / "payments-api"
        if sample.exists():
            path = sample
        else:
            return ProjectBrief(
                project_id=project_id or "unknown",
                name=name or "Unknown project",
                facts=[
                    {
                        "key": "path",
                        "value": str(project_path),
                        "trust": "untrusted",
                        "source": "request",
                        "note": "Path not found; brief is empty.",
                    }
                ],
            )

    files: list[str] = []
    for p in path.rglob("*"):
        if p.is_file() and ".git" not in p.parts and "node_modules" not in p.parts:
            rel = str(p.relative_to(path))
            if len(files) < 200:
                files.append(rel)

    languages = _detect_languages(files)
    frameworks: list[str] = []
    build_command = None
    test_command = None
    ci_system = None
    conventions: list[str] = []
    facts: list[dict] = []

    # Structural manifests (high trust)
    pkg = path / "package.json"
    pyproject = path / "pyproject.toml"
    requirements = path / "requirements.txt"
    pom = path / "pom.xml"

    if pkg.exists():
        frameworks.append("Node.js")
        data = json.loads(_read_safe_text(pkg) or "{}")
        scripts = data.get("scripts", {})
        if "build" in scripts:
            build_command = "npm run build"
        if "test" in scripts:
            test_command = "npm test"
        facts.append(
            {
                "key": "package_name",
                "value": data.get("name"),
                "trust": "high",
                "source": "package.json",
            }
        )

    if pyproject.exists() or requirements.exists():
        frameworks.append("Python")
        if (path / "pytest.ini").exists() or any("test_" in f for f in files):
            test_command = test_command or "pytest"
        build_command = build_command or "pip install -r requirements.txt"

    if pom.exists():
        frameworks.append("Maven")
        build_command = "./mvnw -B package"
        test_command = "./mvnw -B test"

    # CI config (high trust)
    if (path / ".github" / "workflows").exists():
        ci_system = "GitHub Actions"
        facts.append(
            {
                "key": "ci_system",
                "value": "GitHub Actions",
                "trust": "high",
                "source": ".github/workflows",
            }
        )
    elif (path / "Jenkinsfile").exists():
        ci_system = "Jenkins"
    elif (path / ".gitlab-ci.yml").exists():
        ci_system = "GitLab CI"

    # Executed discovery — look for recorded sandbox results in project
    executed = path / ".laap" / "executed.json"
    if executed.exists():
        try:
            payload = json.loads(_read_safe_text(executed) or "{}")
            if payload.get("build_command"):
                build_command = payload["build_command"]
                facts.append(
                    {
                        "key": "build_command",
                        "value": build_command,
                        "trust": "highest",
                        "source": "sandbox_execution",
                    }
                )
            if payload.get("test_command"):
                test_command = payload["test_command"]
                facts.append(
                    {
                        "key": "test_command",
                        "value": test_command,
                        "trust": "highest",
                        "source": "sandbox_execution",
                    }
                )
        except json.JSONDecodeError:
            pass
    else:
        # Simulate execution discovery from README scripts if present
        if build_command:
            facts.append(
                {
                    "key": "build_command",
                    "value": build_command,
                    "trust": "high",
                    "source": "manifest",
                }
            )
        if test_command:
            facts.append(
                {
                    "key": "test_command",
                    "value": test_command,
                    "trust": "high",
                    "source": "manifest",
                }
            )

    readme = path / "README.md"
    if readme.exists():
        text = _read_safe_text(readme)
        # Quarantined extraction: typed fields only, never treat as instructions
        for match in re.finditer(r"(?i)convention[s]?:\s*(.+)", text):
            conventions.append(match.group(1).strip()[:200])
        facts.append(
            {
                "key": "readme_present",
                "value": True,
                "trust": "untrusted_text",
                "source": "README.md",
                "note": "Document text quarantined; used only for vocabulary/conventions.",
            }
        )

    dangerous = [f for f in files if any(x in f for x in ("secret", ".env", "prod", "terraform"))]

    pid = project_id or path.name
    return ProjectBrief(
        project_id=pid,
        name=name or path.name,
        languages=languages,
        frameworks=sorted(set(frameworks)),
        build_command=build_command,
        test_command=test_command,
        ci_system=ci_system,
        conventions=conventions
        or [
            "Prefer small PRs",
            "Tests must stay green",
            "Do not weaken assertions to fake success",
        ],
        dangerous_paths=dangerous[:20],
        glossary={"CI": "Continuous Integration", "PR": "Pull Request"},
        facts=facts
        + [
            {
                "key": "file_inventory_count",
                "value": len(files),
                "trust": "high",
                "source": "inventory",
            },
            {
                "key": "onboarding_id",
                "value": new_id("onb"),
                "trust": "platform",
                "source": "project_onboarding",
            },
        ],
    )
