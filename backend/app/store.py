"""In-memory store for the Phase 1 demo runtime."""

from __future__ import annotations

from threading import Lock

from .models import ProjectBrief, Task


class Store:
    def __init__(self) -> None:
        self._lock = Lock()
        self.tasks: dict[str, Task] = {}
        self.briefs: dict[str, ProjectBrief] = {}
        self.approvals_index: dict[str, str] = {}  # approval_id -> task_id

    def save_task(self, task: Task) -> Task:
        with self._lock:
            self.tasks[task.id] = task
            for apr in task.approvals:
                self.approvals_index[apr.id] = task.id
            return task

    def get_task(self, task_id: str) -> Task | None:
        return self.tasks.get(task_id)

    def list_tasks(self) -> list[Task]:
        return sorted(self.tasks.values(), key=lambda t: t.created_at, reverse=True)

    def save_brief(self, brief: ProjectBrief) -> ProjectBrief:
        with self._lock:
            self.briefs[brief.project_id] = brief
            return brief

    def get_brief(self, project_id: str) -> ProjectBrief | None:
        return self.briefs.get(project_id)

    def list_briefs(self) -> list[ProjectBrief]:
        return list(self.briefs.values())


store = Store()
