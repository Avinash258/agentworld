# Team Packs

A Team Pack is a versioned configuration bundle. It does **not** contain engine code.

## Minimal `pack.yaml`

```yaml
name: delivery-core
version: "1.0.0"
owner: devops-lead
description: CI and build failure diagnosis
roles:
  - id: failure-analyst
    seat: agent
    permissions:
      read: ["logs", "ci", "repo:read"]
      write: [".github/workflows/**"]
    tools:
      - read_ci_log
      - reproduce_in_sandbox
      - cite_log_lines
      - propose_fix
workflows:
  - id: ci-failure-diagnosis
    title: CI and build failure diagnosis
    evidence_validators:
      - id: reproduced
        type: sandbox_exit_match
      - id: cited_logs
        type: min_citations
        min: 2
      - id: classification
        type: required_fields
        fields: ["root_cause", "category", "confidence"]
    human_approval_for:
      - open_pull_request
      - paid_rerun
    budgets:
      max_tokens: 80000
      max_tool_calls: 24
```

## Required parts

| Part | Purpose |
| --- | --- |
| `pack.yaml` | Roles, seats, permissions, approvals, budgets |
| `owner` | Accountable human |
| `workflows[].evidence_validators` | Deterministic accept/reject checks |
| `workflows[].human_approval_for` | Irreversible / externally visible actions |
| eval fixtures | Real past tasks with expected outcomes |

## Seats

- `agent` — model/code worker
- `human assisted by agent` — human remains lead; agent drafts
- `code plus agent` — Verifier pattern (hard checks in code)

## Checklist before merging a new pack

- [ ] Named human owner
- [ ] At least one workflow with validators
- [ ] Approval list for irreversible actions
- [ ] Fixture or eval path
- [ ] Runtime test proves evidence gate + approval gate
- [ ] No secrets in pack files
