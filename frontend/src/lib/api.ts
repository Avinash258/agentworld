const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8765";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export type PlatformStatus = {
  product: string;
  version: string;
  gap_closed: string[];
  packs: { name: string; version: string; owner: string; workflows: string[] }[];
  tasks: number;
  briefs: number;
  models: string;
};

export type Task = {
  id: string;
  created_at: string;
  updated_at: string;
  requester: string;
  raw_request: string;
  state: string;
  pack: string;
  workflow: string;
  project_id?: string;
  structured?: {
    original: string;
    goal: string;
    assumptions: string[];
    questions: string[];
    evidence_required: string[];
    acceptance_criteria: string[];
    diff_summary: string;
    risk: string;
  };
  plan: {
    id: string;
    agent: string;
    action: string;
    needs_approval: boolean;
    status: string;
    result?: Record<string, unknown>;
  }[];
  evidence: {
    id: string;
    kind: string;
    summary: string;
    source: string;
    deterministic: boolean;
    payload: Record<string, unknown>;
  }[];
  evidence_status: string;
  validations: { validator_id: string; passed: boolean; detail: string }[];
  approvals: {
    id: string;
    action: string;
    arguments: Record<string, unknown>;
    reason: string;
    status: string;
    token?: string;
  }[];
  diagnosis?: Record<string, unknown>;
  stories?: Record<string, unknown>[];
  audit: { id: string; at: string; actor: string; event: string; detail: Record<string, unknown> }[];
  error?: string;
};

export type ProjectBrief = {
  project_id: string;
  name: string;
  languages: string[];
  frameworks: string[];
  build_command?: string;
  test_command?: string;
  ci_system?: string;
  conventions: string[];
  facts: Record<string, unknown>[];
  provenance_note: string;
};

export const api = {
  status: () => request<PlatformStatus>("/api/status"),
  tasks: () => request<Task[]>("/api/tasks"),
  task: (id: string) => request<Task>(`/api/tasks/${id}`),
  createTask: (body: {
    request: string;
    pack?: string;
    workflow?: string;
    project_id?: string;
  }) =>
    request<Task>("/api/tasks", {
      method: "POST",
      body: JSON.stringify({ ...body, auto_run: true, requester: "console-user" }),
    }),
  decide: (taskId: string, approvalId: string, approve: boolean) =>
    request<Task>(`/api/tasks/${taskId}/approvals/${approvalId}`, {
      method: "POST",
      body: JSON.stringify({
        approve,
        decided_by: "console-lead",
        note: approve ? "Approved from console" : "Denied from console",
      }),
    }),
  briefs: () => request<ProjectBrief[]>("/api/briefs"),
  onboard: () =>
    request<ProjectBrief>("/api/onboard", {
      method: "POST",
      body: JSON.stringify({
        project_path: "samples/projects/payments-api",
        project_id: "sample-payments-api",
        name: "Payments API",
      }),
    }),
};
