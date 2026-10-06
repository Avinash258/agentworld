# Local Agentic AI Platform

Supervised multi-agent runtime for software delivery teams. Runs on infrastructure you control. Agents draft and diagnose; **evidence gates** and a **human-approval policy engine** decide what counts as done.

This repository is the **Phase 1 slice** from the Project Book v2.0: runtime core, Prompt Architect, Project Onboarding, CI failure diagnosis, BA demo pack, and an operator console.

## What gap this closes

| Market / product gap | How this slice addresses it |
| --- | --- |
| Most agent products are cloud SaaS | Runtime and console run locally on your machine / VMs |
| Output trusted because the model said so | Verifier accepts work only with deterministic evidence |
| Irreversible actions happen quietly | Policy engine requires human approval (PR open, backlog write, …) |
| One-team prototypes hard to extend | Team Packs are configuration bundles, not engine forks |
| Agents don't know the project | Project Onboarding builds a provenance-aware Project Brief |
| Vague prompts cause most multi-agent failures | Prompt Architect structures every request without changing intent |

## Architecture (Phase 1)

```
Console (Next.js :43123)
        │
        ▼
Runtime API (FastAPI :8765)
  Prompt Architect → Planner → Team agent → Verifier → Policy / Approval
        │
        ├── packs/          Team Pack YAML
        ├── samples/        CI fixtures + sample project
        └── evidence + audit trail on every task
```

## Quick start

### 1. Runtime

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8765 --app-dir .
```

From `backend/` the import path is `app.main`. Prefer:

```bash
cd /workspace/backend
source .venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --host 127.0.0.1 --port 8765
```

### 2. Console

```bash
cd frontend
npm install
npm run dev
```

Open [http://127.0.0.1:43123](http://127.0.0.1:43123).

### 3. Try the demos

In the console:

1. **CI failure on main** — diagnoses the sample Postgres healthcheck regression, attaches sandbox + log citations, then waits for you to approve opening a PR.
2. **Flaky cart test** — second fixture path.
3. **Requirement → stories** — BA Team Pack drafts cited user stories; backlog write needs approval.

## API sketch

- `GET /api/status` — platform status and gap checklist
- `GET /api/packs` — Team Packs
- `POST /api/onboard` — Project Onboarding
- `POST /api/tasks` — create + run a supervised task
- `POST /api/tasks/{id}/approvals/{approval_id}` — human decision

## Design principles enforced in code

1. **Evidence over claims** — `evidence.py` validators from the Team Pack
2. **Humans own irreversible decisions** — `policy.py`
3. **Untrusted documents are data, never instructions** — onboarding quarantined reader
4. **One worker by default** — planner keeps CI diagnosis single-agent
5. **Secrets are never tools** — hard denies in the policy engine

## Layout

```
backend/          FastAPI Agent Runtime
frontend/         Next.js operator console
packs/            Team Packs (delivery-core, ba-product)
samples/          CI failure fixtures + payments-api project
uploads/          Source Project Book (reference)
```

## Notes

- No cloud LLM key is required for the demo; diagnosis uses deterministic fixtures and rules so the evidence/policy loop is always demonstrable offline.
- This is not a replacement for engineers. People own requirements, approvals, and accountability.
- Later phases (more packs, SSO, vLLM, multi-project isolation) are intentionally out of scope here.

## License

Internal project concept — align with your company policy before redistribution.
