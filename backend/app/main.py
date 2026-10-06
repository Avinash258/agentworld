"""FastAPI entrypoint for the Local Agentic AI Platform runtime."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import ApprovalDecision, CreateTaskRequest, OnboardRequest
from .packs import get_pack, list_packs
from . import runtime as rt
from .store import store

app = FastAPI(
    title="Local Agentic AI Platform",
    description="Supervised multi-agent runtime with evidence gating and human approvals.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    rt.ensure_sample_brief()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/status")
def status():
    return rt.platform_status()


@app.get("/api/packs")
def packs():
    return list_packs()


@app.get("/api/packs/{name}")
def pack(name: str):
    p = get_pack(name)
    if not p:
        raise HTTPException(404, "Pack not found")
    return p


@app.get("/api/briefs")
def briefs():
    return store.list_briefs()


@app.post("/api/onboard")
def onboard(req: OnboardRequest):
    return rt.onboard(req)


@app.get("/api/tasks")
def tasks():
    return store.list_tasks()


@app.get("/api/tasks/{task_id}")
def task(task_id: str):
    t = store.get_task(task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    return t


@app.post("/api/tasks")
def create_task(req: CreateTaskRequest):
    return rt.create_and_run(req)


@app.post("/api/tasks/{task_id}/run")
def run_task(task_id: str):
    if not store.get_task(task_id):
        raise HTTPException(404, "Task not found")
    return rt.run_task(task_id)


@app.post("/api/tasks/{task_id}/approvals/{approval_id}")
def decide(task_id: str, approval_id: str, body: ApprovalDecision):
    try:
        return rt.decide_approval(task_id, approval_id, body)
    except KeyError:
        raise HTTPException(404, "Task or approval not found") from None
