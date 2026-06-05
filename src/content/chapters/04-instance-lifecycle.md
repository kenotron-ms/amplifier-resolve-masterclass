---
title: "The Instance Lifecycle"
chapter: 4
---

# Section 4: The Instance Lifecycle

The instance is the unit of work (§1). Everything the platform does is in service
of moving one instance through its lifecycle and reporting where it is. Master the
lifecycle and you have the spine of the whole platform.

## 4.1 Eight statuses

An instance is always in exactly one of eight statuses (`InstanceStatusEnum`):

```
                                 ┌───────────┐
                                 │  paused   │ ─┐
                                 └───────────┘  │
                                   ▲            │
                                   │ suspend    │ resume
                                   │            ▼
┌─────────┐     ┌──────────┐     ┌───────────────────────────────────┐  request_input   ┌────────────────┐
│ created │ ──▶ │ starting │ ──▶ │                                   │ ───────────────▶ │ awaiting_input │
└─────────┘     └──────────┘     │                                   │                  └────────────────┘
                                 │                                   │  response          │
                                 │              running              │ ◀──────────────────┘
                                 │                                   │
                ┌──────────┐     │                                   │
                │  failed  │ ◀── │                                   │
                └──────────┘     └───────────────────────────────────┘
                                   │                       │
                                   │                       │
                                   ▼                       ▼
                                 ┌───────────┐           ┌───────────┐
                                 │ cancelled │           │ completed │
                                 └───────────┘           └───────────┘
```

| Status | Meaning |
|---|---|
| `created` | Instance persisted; container not yet provisioned. |
| `starting` | Container being created, configured, and launched. |
| `running` | Worker executing the resolver. |
| `awaiting_input` | Resolver opened an A2UI input-request and is blocked on a human (§8). |
| `paused` | Resolver suspended execution; resumable via `POST /instances/{id}/resume`. |
| `completed` | Terminal. Finished successfully. |
| `failed` | Terminal. Finished with an error. |
| `cancelled` | Terminal. Stopped by request. |

`awaiting_input` and `paused` are the two states that distinguish a *governed run*
from a plain script. They are why an instance is not a session: a session does not
suspend itself for an hour waiting on a person and then carry on.

**Design Decision — `awaiting_input` and `paused` are first-class platform
statuses, but *what* triggers them is the resolver's call.**
The platform models "blocked on a human" and "suspended" as states it can report
and act on (route a response, resume on request). It does not decide *when* a
resolver should block or pause — that is policy. The status vocabulary is
mechanism; the transitions are the resolver's.

## 4.2 Four phases of the lifecycle

Underneath the statuses, the platform moves every instance through four phases.
The parallel to Core's session lifecycle (Create, Initialize, Execute, Cleanup) is
exact and intentional.

**1. Intake.** `POST /instances` arrives with `{resolver, input}`. The platform
validates `input` against the resolver's A2UI check rules — `422` on failure,
*before any container exists*. On success the `InstanceStore` persists the
instance as `created`. A background task takes over and the status moves to
`starting`.

**2. Provision.** The orchestrator creates the container (`resolve-{id}`), writes
`/project/.resolve/config.json` (the serialized `InstanceConfig`), injects worker
files, bundle configs, forwarded credentials, and the provider-agnostic `create-pr`
wrapper, clones the workspace repos, and launches the worker. Two paths exist: a
cached fast path (~15s, pre-baked image) and a cold path (~5min, full install).

**3. Execute.** The worker runs the resolver. The resolver does its work, emitting
events and state snapshots to the `.resolve/` directory (§6, §7), opening
input-requests and consuming messages as needed. This phase is where the resolver's
*strategy* plays out, and it is opaque to the platform by design — the platform
sees only the event stream, never the reasoning.

**4. Finalize.** Cleanup. The platform recognizes terminal state (§4.4), transitions
the instance to `completed`/`failed`/`cancelled`, and tears down the container. As
in Core, cleanup is not optional and not best-effort for the things that matter:
the watchdog and lifecycle sweep ensure containers do not leak even after crashes.

## 4.3 The monitor loop — how the platform *sees* a run

The platform does not live inside the worker. It observes from outside, through a
background poller started at app lifespan (`monitor.py` → `monitor_loop`). On each
pass it:

- **Mirrors events** — reads the container's `events.jsonl` and `state.json` and
  pushes them onto the EventBus for SSE streaming.
- **Discovers input-requests** — scans `.resolve/input-requests/` for new request
  files and exposes them via the API.
- **Extracts status** — reads resolver-reported status checkpoints.
- **Reconciles completion** — detects terminal state and finalizes (§4.4).

This is the same shape as Core's "file output comes from modules": the *worker*
writes the files; the *platform* reads them. The coordination medium is the
filesystem (§6), which is simple, inspectable (`tail -f events.jsonl` just works),
and survives a daemon restart.

## 4.4 Completion reconciliation

How does the platform know a run is over? In strict priority order:

1. **`resolver:completed` event** — primary and authoritative. Carries `outcome`,
   `summary`, `duration_s`, `artifact_count`, and optional structured `error` (§7).
2. **Process exit code** — fallback. Exit 0 → `success`; non-zero → `failed`. No
   structured error is available on this path.
3. **Watchdog timeout** — last resort. SIGTERM → SIGKILL escalation; the run is
   marked `crashed`.

**Design Decision — Completion is reconciled from a dual signal (event + process
state), with the event authoritative.**
Relying on the event alone would hang on any resolver bug that skips the emit.
Relying on exit code alone would discard the structured outcome and error a
well-behaved resolver provides. Reading both — event first, exit second — gives a
clean exit when the resolver cooperates and a safe fallback when it does not. This
is the platform-side mirror of the resolver-side invariant in §7: *emit
`resolver:completed` at every exit path.*

## 4.5 Cancellation, pause, resume

- **Cancel** (`DELETE /instances/{id}`) stops the run and tears down the container.
- **Stop** (`POST /instances/{id}/stop`) requests a *graceful* stop; the resolver's
  `stop(reason)` method is invoked so it can wind down cleanly.
- **Pause / resume** (`POST /instances/{id}/resume`) is only meaningful for
  resolvers that advertise `supports_resume = True` (§5). dot-graph can resume from
  checkpointed pipeline status; understudy cannot, because its conversational state
  is too rich to checkpoint faithfully.

Whether a run *can* resume is a property the resolver declares — mechanism the
platform offers, policy the resolver opts into. The pattern repeats at every level,
which is exactly the point. Next, §5 makes the resolver contract itself precise.
