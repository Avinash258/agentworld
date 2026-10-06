# Runtime API (Phase 1)

Base URL default: `http://127.0.0.1:8765`

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness |
| GET | `/api/status` | Product status + gap checklist + packs |
| GET | `/api/packs` | List Team Packs |
| GET | `/api/packs/{name}` | One pack |
| GET | `/api/briefs` | Project Briefs |
| POST | `/api/onboard` | Run Project Onboarding |
| GET | `/api/tasks` | List tasks |
| GET | `/api/tasks/{id}` | Task detail (plan, evidence, approvals, audit) |
| POST | `/api/tasks` | Create (+ optionally auto-run) supervised task |
| POST | `/api/tasks/{id}/run` | Run / resume pipeline |
| POST | `/api/tasks/{id}/approvals/{approval_id}` | Human approve/deny |

## Create task body

```json
{
  "request": "main is red again, can someone check the payments pipeline?",
  "requester": "console-user",
  "project_id": "sample-payments-api",
  "pack": "delivery-core",
  "workflow": "ci-failure-diagnosis",
  "auto_run": true
}
```

## Approval body

```json
{
  "approve": true,
  "decided_by": "console-lead",
  "note": "Approved from console"
}
```

## Expected happy path states

1. `awaiting_approval` + `evidence_status: verified`
2. After approve → `completed` with approval `token`
3. After deny → `rejected`
