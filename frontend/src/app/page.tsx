"use client";

import { useEffect, useMemo, useState, useTransition } from "react";
import { Button } from "@/components/ui/button";
import { api, type PlatformStatus, type ProjectBrief, type Task } from "@/lib/api";
import {
  CheckCircle2,
  CircleAlert,
  FileSearch,
  GitPullRequest,
  Loader2,
  ShieldCheck,
  Sparkles,
  Workflow,
} from "lucide-react";

const DEMOS = [
  {
    label: "CI failure on main",
    request: "main is red again, can someone check the payments pipeline?",
    pack: "delivery-core",
  },
  {
    label: "Flaky cart test",
    request: "flaky cart total assertion keeps failing in CI",
    pack: "delivery-core",
  },
  {
    label: "Requirement → stories",
    request:
      "Users need to pause a recurring payment and receive an email confirmation. Admins must see the pause reason in the audit log.",
    pack: "ba-product",
  },
];

function stateColor(state: string) {
  if (state === "completed" || state === "approved") return "var(--good)";
  if (state === "awaiting_approval") return "var(--warn)";
  if (state === "failed" || state === "rejected") return "var(--bad)";
  return "var(--ink-muted)";
}

export default function HomePage() {
  const [status, setStatus] = useState<PlatformStatus | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [brief, setBrief] = useState<ProjectBrief | null>(null);
  const [request, setRequest] = useState(DEMOS[0].request);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();
  const [booting, setBooting] = useState(true);

  const selected = useMemo(
    () => tasks.find((t) => t.id === selectedId) || tasks[0] || null,
    [tasks, selectedId]
  );

  async function refresh() {
    const [s, t, b] = await Promise.all([api.status(), api.tasks(), api.briefs()]);
    setStatus(s);
    setTasks(t);
    setBrief(b[0] || null);
    if (!selectedId && t[0]) setSelectedId(t[0].id);
  }

  useEffect(() => {
    (async () => {
      try {
        await api.onboard();
        await refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to reach runtime");
      } finally {
        setBooting(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function runDemo(text: string, pack?: string) {
    setRequest(text);
    setError(null);
    startTransition(async () => {
      try {
        const task = await api.createTask({
          request: text,
          pack,
          project_id: "sample-payments-api",
        });
        await refresh();
        setSelectedId(task.id);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Task failed");
      }
    });
  }

  function decide(approve: boolean) {
    if (!selected) return;
    const apr = selected.approvals.find((a) => a.status === "pending");
    if (!apr) return;
    startTransition(async () => {
      try {
        const updated = await api.decide(selected.id, apr.id, approve);
        await refresh();
        setSelectedId(updated.id);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Approval failed");
      }
    });
  }

  return (
    <main className="relative mx-auto min-h-screen max-w-7xl px-4 pb-16 pt-8 sm:px-6 lg:px-8">
      <header className="rise mb-10 flex flex-col gap-6 border-b border-[var(--line)] pb-8 md:flex-row md:items-end md:justify-between">
        <div className="max-w-2xl">
          <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-[0.22em] text-[var(--accent)]">
            <span className="live-dot" />
            Local runtime · Phase 1 slice
          </div>
          <h1
            className="text-4xl leading-[1.05] text-[var(--ink)] sm:text-5xl"
            style={{ fontFamily: "var(--font-display), serif" }}
          >
            Local Agentic AI Platform
          </h1>
          <p className="mt-4 max-w-xl text-base leading-relaxed text-[var(--ink-muted)]">
            Supervised agents on infrastructure you control. Work is accepted only with
            deterministic evidence — and irreversible actions wait for a human.
          </p>
        </div>
        <div className="rise rise-delay-1 flex flex-col items-start gap-2 rounded-sm border border-[var(--line)] bg-[var(--panel)]/70 px-4 py-3 backdrop-blur-sm md:items-end">
          <div className="flex items-center gap-2 text-sm text-[var(--ink)]">
            <ShieldCheck className="h-4 w-4 text-[var(--good)]" />
            Evidence gating · Policy engine · Team Packs
          </div>
          <div className="font-mono text-xs text-[var(--ink-muted)]">
            {status?.version || "connecting…"} · {status?.tasks ?? 0} tasks ·{" "}
            {status?.packs?.length ?? 0} packs
          </div>
        </div>
      </header>

      {error && (
        <div className="mb-6 flex items-start gap-2 border border-[var(--bad)]/40 bg-[var(--bad)]/10 px-4 py-3 text-sm text-[#ffd2ca]">
          <CircleAlert className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <section className="rise rise-delay-1 mb-8 grid gap-4 md:grid-cols-3">
        {(status?.gap_closed || [
          "Company-controlled runtime",
          "Evidence gating",
          "Human-approval policy",
        ]).slice(0, 3).map((item) => (
          <div
            key={item}
            className="border border-[var(--line)] bg-[var(--panel)]/60 px-4 py-4"
          >
            <div className="mb-2 flex items-center gap-2 text-[var(--accent)]">
              <CheckCircle2 className="h-4 w-4" />
              <span className="text-xs uppercase tracking-[0.16em]">Gap closed</span>
            </div>
            <p className="text-sm leading-relaxed text-[var(--ink)]">{item}</p>
          </div>
        ))}
      </section>

      <div className="grid gap-6 lg:grid-cols-[1.05fr_1.4fr]">
        <section className="rise rise-delay-2 space-y-4">
          <div className="border border-[var(--line)] bg-[var(--panel)]/70 p-5">
            <div className="mb-3 flex items-center gap-2 text-[var(--accent)]">
              <Sparkles className="h-4 w-4" />
              <h2 className="text-sm font-semibold uppercase tracking-[0.14em]">
                New supervised task
              </h2>
            </div>
            <textarea
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              rows={4}
              className="w-full resize-y border border-[var(--line)] bg-[var(--bg)]/80 px-3 py-2 text-sm text-[var(--ink)] outline-none focus:border-[var(--accent)]"
              placeholder="Describe the work…"
            />
            <div className="mt-3 flex flex-wrap gap-2">
              {DEMOS.map((d) => (
                <Button
                  key={d.label}
                  size="sm"
                  variant="secondary"
                  onClick={() => runDemo(d.request, d.pack)}
                  disabled={pending || booting}
                >
                  {d.label}
                </Button>
              ))}
            </div>
            <div className="mt-4 flex gap-2">
              <Button
                onClick={() => runDemo(request)}
                disabled={pending || booting || !request.trim()}
              >
                {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Workflow className="h-4 w-4" />}
                Run through runtime
              </Button>
            </div>
          </div>

          <div className="border border-[var(--line)] bg-[var(--panel)]/70 p-5">
            <div className="mb-3 flex items-center gap-2 text-[var(--accent)]">
              <FileSearch className="h-4 w-4" />
              <h2 className="text-sm font-semibold uppercase tracking-[0.14em]">
                Project Brief
              </h2>
            </div>
            {brief ? (
              <div className="space-y-2 text-sm text-[var(--ink-muted)]">
                <p className="text-[var(--ink)]">
                  <span style={{ fontFamily: "var(--font-display), serif" }} className="text-lg">
                    {brief.name}
                  </span>{" "}
                  <span className="font-mono text-xs">({brief.project_id})</span>
                </p>
                <p>
                  {brief.languages.join(", ") || "—"} · {brief.frameworks.join(", ") || "—"} ·{" "}
                  {brief.ci_system || "CI unknown"}
                </p>
                <p className="font-mono text-xs">
                  build: {brief.build_command || "—"} · test: {brief.test_command || "—"}
                </p>
                <p className="text-xs leading-relaxed opacity-80">{brief.provenance_note}</p>
              </div>
            ) : (
              <p className="text-sm text-[var(--ink-muted)]">Onboarding…</p>
            )}
          </div>

          <div className="border border-[var(--line)] bg-[var(--panel)]/70 p-5">
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-[0.14em] text-[var(--accent)]">
              Task queue
            </h2>
            <div className="max-h-72 space-y-2 overflow-auto">
              {tasks.length === 0 && (
                <p className="text-sm text-[var(--ink-muted)]">No tasks yet. Run a demo above.</p>
              )}
              {tasks.map((t) => (
                <button
                  key={t.id}
                  onClick={() => setSelectedId(t.id)}
                  className={`block w-full border px-3 py-2 text-left transition-colors ${
                    selected?.id === t.id
                      ? "border-[var(--accent)] bg-[var(--panel-2)]"
                      : "border-[var(--line)] bg-[var(--bg)]/40 hover:bg-[var(--panel-2)]"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate text-sm text-[var(--ink)]">{t.raw_request}</span>
                    <span
                      className="shrink-0 font-mono text-[10px] uppercase"
                      style={{ color: stateColor(t.state) }}
                    >
                      {t.state.replaceAll("_", " ")}
                    </span>
                  </div>
                  <div className="mt-1 font-mono text-[10px] text-[var(--ink-muted)]">
                    {t.pack} · {t.workflow}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="rise rise-delay-3 border border-[var(--line)] bg-[var(--panel)]/75 p-5 sm:p-6">
          {!selected ? (
            <div className="flex h-full min-h-80 items-center justify-center text-sm text-[var(--ink-muted)]">
              {booting ? "Starting runtime…" : "Select or run a task to inspect the evidence trail."}
            </div>
          ) : (
            <TaskDetail task={selected} onDecide={decide} busy={pending} />
          )}
        </section>
      </div>
    </main>
  );
}

function TaskDetail({
  task,
  onDecide,
  busy,
}: {
  task: Task;
  onDecide: (approve: boolean) => void;
  busy: boolean;
}) {
  const pendingApproval = task.approvals.find((a) => a.status === "pending");

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-[var(--line)] pb-4">
        <div>
          <p className="font-mono text-xs text-[var(--ink-muted)]">{task.id}</p>
          <h2
            className="mt-1 text-2xl text-[var(--ink)]"
            style={{ fontFamily: "var(--font-display), serif" }}
          >
            {task.structured?.goal?.slice(0, 80) || task.raw_request}
          </h2>
          <p className="mt-2 text-sm text-[var(--ink-muted)]">{task.raw_request}</p>
        </div>
        <div
          className="rounded-sm border px-3 py-1 font-mono text-xs uppercase tracking-wide"
          style={{ borderColor: stateColor(task.state), color: stateColor(task.state) }}
        >
          {task.state.replaceAll("_", " ")}
        </div>
      </div>

      {task.error && (
        <div className="border border-[var(--bad)]/40 bg-[var(--bad)]/10 px-3 py-2 text-sm text-[#ffd2ca]">
          {task.error}
        </div>
      )}

      {task.structured && (
        <Block title="Prompt Architect">
          <p className="text-sm text-[var(--ink)]">{task.structured.diff_summary}</p>
          {task.structured.assumptions?.length > 0 && (
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[var(--ink-muted)]">
              {task.structured.assumptions.map((a) => (
                <li key={a}>{a}</li>
              ))}
            </ul>
          )}
          <div className="mt-3 flex flex-wrap gap-2">
            {task.structured.evidence_required?.map((e) => (
              <span
                key={e}
                className="border border-[var(--line)] bg-[var(--bg)]/50 px-2 py-1 text-xs text-[var(--ink-muted)]"
              >
                {e}
              </span>
            ))}
          </div>
        </Block>
      )}

      <Block title="Plan">
        <ol className="space-y-2">
          {task.plan.map((step, i) => (
            <li
              key={step.id}
              className="flex items-center justify-between gap-3 border border-[var(--line)] bg-[var(--bg)]/40 px-3 py-2 text-sm"
            >
              <span>
                <span className="mr-2 font-mono text-xs text-[var(--ink-muted)]">{i + 1}</span>
                <span className="text-[var(--ink)]">{step.agent}</span>
                <span className="text-[var(--ink-muted)]"> · {step.action}</span>
                {step.needs_approval && (
                  <span className="ml-2 text-xs text-[var(--warn)]">needs approval</span>
                )}
              </span>
              <span className="font-mono text-[10px] uppercase text-[var(--ink-muted)]">
                {step.status}
              </span>
            </li>
          ))}
        </ol>
      </Block>

      {task.diagnosis && (
        <Block title="Diagnosis">
          <p className="text-sm text-[var(--ink)]">{String(task.diagnosis.root_cause)}</p>
          <p className="mt-2 font-mono text-xs text-[var(--ink-muted)]">
            category={String(task.diagnosis.category)} · confidence=
            {String(task.diagnosis.confidence)}
          </p>
          {task.diagnosis.explanation && (
            <p className="mt-2 text-sm leading-relaxed text-[var(--ink-muted)]">
              {String(task.diagnosis.explanation)}
            </p>
          )}
        </Block>
      )}

      {task.stories && (
        <Block title="User stories">
          <div className="space-y-3">
            {task.stories.map((s) => (
              <div key={String(s.id)} className="border border-[var(--line)] bg-[var(--bg)]/40 p-3">
                <p className="text-sm font-medium text-[var(--ink)]">
                  {String(s.id)} · {String(s.title)}
                </p>
                <p className="mt-1 text-sm text-[var(--ink-muted)]">{String(s.user_story)}</p>
              </div>
            ))}
          </div>
        </Block>
      )}

      <Block title={`Evidence · ${task.evidence_status}`}>
        <div className="mb-3 flex flex-wrap gap-2">
          {task.validations.map((v) => (
            <span
              key={v.validator_id}
              className="inline-flex items-center gap-1 border px-2 py-1 text-xs"
              style={{
                borderColor: v.passed ? "var(--good)" : "var(--bad)",
                color: v.passed ? "var(--good)" : "var(--bad)",
              }}
            >
              {v.passed ? <CheckCircle2 className="h-3 w-3" /> : <CircleAlert className="h-3 w-3" />}
              {v.validator_id}: {v.detail}
            </span>
          ))}
        </div>
        <ul className="space-y-2">
          {task.evidence.map((e) => (
            <li key={e.id} className="border border-[var(--line)] bg-[var(--bg)]/40 px-3 py-2">
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono text-[10px] uppercase text-[var(--accent)]">
                  {e.kind}
                  {e.deterministic ? " · deterministic" : ""}
                </span>
                <span className="font-mono text-[10px] text-[var(--ink-muted)]">{e.source}</span>
              </div>
              <p className="mt-1 text-sm text-[var(--ink)]">{e.summary}</p>
            </li>
          ))}
        </ul>
      </Block>

      {pendingApproval && (
        <Block title="Human approval required">
          <div className="flex items-start gap-3">
            <GitPullRequest className="mt-1 h-5 w-5 text-[var(--warn)]" />
            <div className="flex-1">
              <p className="text-sm text-[var(--ink)]">{pendingApproval.reason}</p>
              <p className="mt-1 font-mono text-xs text-[var(--ink-muted)]">
                action={pendingApproval.action}
              </p>
              <pre className="mt-3 max-h-40 overflow-auto border border-[var(--line)] bg-[var(--bg)]/60 p-3 font-mono text-[11px] text-[var(--ink-muted)]">
                {JSON.stringify(pendingApproval.arguments, null, 2)}
              </pre>
              <div className="mt-4 flex gap-2">
                <Button onClick={() => onDecide(true)} disabled={busy}>
                  Approve
                </Button>
                <Button variant="danger" onClick={() => onDecide(false)} disabled={busy}>
                  Deny
                </Button>
              </div>
            </div>
          </div>
        </Block>
      )}

      {task.approvals.some((a) => a.status === "approved") && (
        <div className="border border-[var(--good)]/40 bg-[var(--good)]/10 px-3 py-2 text-sm text-[#c8f0dc]">
          Approval granted
          {task.approvals.find((a) => a.token) && (
            <span className="ml-2 font-mono text-xs">
              token={task.approvals.find((a) => a.token)?.token}
            </span>
          )}
        </div>
      )}

      <Block title="Audit trail">
        <ul className="max-h-48 space-y-1 overflow-auto font-mono text-[11px] text-[var(--ink-muted)]">
          {task.audit.map((a) => (
            <li key={a.id}>
              {new Date(a.at).toLocaleTimeString()} · {a.actor} · {a.event}
            </li>
          ))}
        </ul>
      </Block>
    </div>
  );
}

function Block({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-[var(--accent)]">
        {title}
      </h3>
      {children}
    </div>
  );
}
