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

<!-- diagram:instance-status -->
<figure class="diagram">
<svg xmlns="http://www.w3.org/2000/svg" class="rdiagram" width="670" height="316" viewBox="-10 -10 670 316" preserveAspectRatio="xMidYMid meet" role="img">
<defs><filter id="nshadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="1.6" stdDeviation="2.6" flood-color="#2a2622" flood-opacity="0.16"/></filter><marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse"><path d="M0,0.6 L9,5 L0,9.4 L2.4,5 Z" fill="#6b6359"/></marker></defs>
<path d="M 96.1 127.0 C 104.6 127.0 113.7 127.0 122.5 127.0" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 232.3 127.0 C 240.8 127.0 249.7 127.0 258.4 127.0" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 327.9 106.3 C 338.1 84.3 357.4 50.6 386.0 35.0 C 418.3 17.4 458.6 13.2 493.6 14.1" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="393.5" y="2.2" width="85.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="436.0" y="14.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">request_input</text>
<path d="M 368.4 114.3 C 374.3 113.1 380.3 111.9 386.0 111.0 C 430.2 103.9 480.8 99.8 518.6 97.6" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="411.5" y="87.2" width="49.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="436.0" y="99.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">suspend</text>
<path d="M 368.2 142.2 C 374.2 143.7 380.2 145.0 386.0 146.0 C 426.2 152.8 471.8 155.6 508.2 156.7" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 358.0 147.5 C 367.1 151.9 376.8 156.4 386.0 160.0 C 432.1 178.1 486.6 193.6 525.3 203.6" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 335.1 147.6 C 347.5 162.9 366.1 183.4 386.0 197.0 C 424.6 223.5 473.7 243.3 512.2 256.4" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 513.7 45.5 C 504.4 48.4 495.0 51.3 486.0 54.0 C 441.9 67.1 427.8 61.6 386.0 81.0 C 374.7 86.3 363.2 93.4 353.0 100.5" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="408.5" y="41.2" width="55.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="436.0" y="53.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">response</text>
<path d="M 532.6 115.6 C 518.1 121.5 501.6 127.1 486.0 130.0 C 450.6 136.6 410.3 136.1 378.1 133.8" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="414.5" y="117.2" width="43.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="436.0" y="129.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">resume</text>
<g filter="url(#nshadow)">
<rect x="0.0" y="106.5" width="96.0" height="41.0" rx="14.0" fill="#eef2f4" stroke="#7fa0b0" stroke-width="1.5"/>
</g>
<text x="48.0" y="130.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#3f6075">created</text>
<g filter="url(#nshadow)">
<rect x="133.0" y="106.5" width="99.0" height="41.0" rx="14.0" fill="#eef2f4" stroke="#7fa0b0" stroke-width="1.5"/>
</g>
<text x="182.5" y="130.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#3f6075">starting</text>
<g filter="url(#nshadow)">
<rect x="269.0" y="106.5" width="99.0" height="41.0" rx="14.0" fill="#f6e7d0" stroke="#b07a3f" stroke-width="1.5"/>
</g>
<text x="318.5" y="130.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#8a5a2b">running</text>
<g filter="url(#nshadow)">
<rect x="504.0" y="4.5" width="146.0" height="41.0" rx="14.0" fill="#f3ead2" stroke="#c69a4a" stroke-width="1.5"/>
</g>
<text x="577.0" y="28.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#8a6a1f">awaiting_input</text>
<g filter="url(#nshadow)">
<rect x="529.0" y="74.5" width="96.0" height="41.0" rx="14.0" fill="#f3ead2" stroke="#c69a4a" stroke-width="1.5"/>
</g>
<text x="577.0" y="98.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#8a6a1f">paused</text>
<g filter="url(#nshadow)">
<rect x="518.5" y="136.5" width="117.0" height="41.0" rx="14.0" fill="#e7efe2" stroke="#7fa06a" stroke-width="1.5"/>
</g>
<text x="577.0" y="160.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#4f6f3c">completed</text>
<g filter="url(#nshadow)">
<rect x="535.5" y="195.5" width="83.0" height="41.0" rx="14.0" fill="#f1e3da" stroke="#c08a6a" stroke-width="1.5"/>
</g>
<text x="577.0" y="219.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#8a4f2f">failed</text>
<g filter="url(#nshadow)">
<rect x="522.0" y="254.5" width="110.0" height="41.0" rx="14.0" fill="#f1e3da" stroke="#c08a6a" stroke-width="1.5"/>
</g>
<text x="577.0" y="278.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#8a4f2f">cancelled</text>
</svg>
<figcaption>The eight instance statuses and their transitions.</figcaption>
<details class="diagram-text"><summary>Text version</summary><pre class="diagram-ascii">                                 ┌───────────┐
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
                                 └───────────┘           └───────────┘</pre></details>
</figure>
<!-- /diagram:instance-status -->

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
