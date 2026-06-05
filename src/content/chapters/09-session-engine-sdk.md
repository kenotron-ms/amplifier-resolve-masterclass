---
title: "The Session Engine (SDK)"
chapter: 9
---

# Section 9: The Session Engine (SDK)

A resolver decides *strategy* (§5). But to execute that strategy it needs to run
Amplifier sessions — and running sessions well, cheaply, and observably is a hard
problem the platform solves once, in the SDK, so every resolver inherits the
solution. This section is the layer beneath every resolver.

## 9.1 Prepare once, create many

Preparing a bundle — downloading modules, resolving dependencies, composing
configuration — is expensive. Creating a session from an already-prepared bundle is
cheap. The `SessionFactory` splits these deliberately:

- **`startup()`** runs once. It loads the base worker bundle, composes the caller and
  default bundles, and calls `.prepare()` to produce a singleton `PreparedBundle`.
  This is the slow step, paid a single time per worker.
- **`create_phase_session()`** runs per phase, cheaply. It mints a session id
  (`resolve-{phase}-{uuid8}`) and calls `prepared.create_session()`.

**Design Decision — Bundle preparation is paid once; session creation is paid per
phase.**
A resolver that runs five phases would otherwise pay the full preparation cost five
times. Splitting "prepare" (expensive, once) from "create" (cheap, many) makes
multi-phase and multi-session resolvers practical. This is the same expensive-setup,
cheap-instantiation pattern the Foundation layer uses for its `PreparedBundle` in
Core — Resolve consumes it directly.

## 9.2 Parent-id propagation — stitching the session graph

A resolver run is rarely one session. dot-graph runs a session per node; orchestrator
spawns workers; understudy dispatches verifiers. For observability to mean anything,
all those sessions must stitch back to the run that spawned them. That is what
`parent_id` does.

`create_phase_session()` locates the context-intelligence hook in the bundle's mount
plan and stamps runtime config — `parent_id`, `resolve_instance_id`, and the CI
server URL/key/workspace — so the cross-session graph links a spawned phase session
to its parent (§7.1). A resolver that passes `parent_id=self.session_id` gets a
correctly stitched tree; one that omits it gets today's flat behavior, unchanged.

> **Implementation status.** The resolver-side change landed (`c2fa831`); the
> CI-bundle side — teaching `hook-context-intelligence`'s config resolver to
> recognize `parent_id` and stamp it into `metadata.json` — is a ~30 LOC change still
> pending in `amplifier-bundle-context-intelligence`. Until it lands, the resolver
> side is a forward-compatible no-op. This is gap **G-1** in the event-vocabulary
> design doc.

The factory also registers a `session.spawn` capability that resolves an agent name
to a bundle and delegates to `prepared.spawn()` — the machinery behind the `delegate`
tool, recipes, and the attractor pipeline's per-node sessions.

## 9.3 The EventEmitter

One `EventEmitter` per instance threads through the whole run. Its discipline is
worth knowing precisely:

- **`emit()`** appends one JSON line to `events.jsonl` under a lock and flushes
  immediately (so `tail -f` works), and *never raises* — a logging failure must not
  crash a run.
- **`update_state()`** writes `state.json` atomically via temp-file + `os.replace`;
  it **replaces** the document and stamps `instance_id` + `updated_at` (§7.4).
- **`merge_state()`** reads, overlays, and writes back — the accumulation primitive
  (§7.4).
- **`request_input()`** writes the input-request schema and returns the awaitable
  future (§8.3).

A subtle but important property: if `work_dir` is `None`, every emitter method is a
silent no-op. The same resolver code runs identically in a real container (writing
files) and in a unit test (writing nothing), with no branching.

**Design Decision — The emitter never raises and degrades to a no-op without a work
dir.**
Observability must never be the thing that breaks a run, and a resolver must be
testable without a container. A non-raising, work-dir-optional emitter delivers both:
production writes files, tests write nothing, and a flaky disk never takes down an
agent mid-task.

## 9.4 Disposable sessions and antagonistic review

The SDK offers two higher-order primitives that encode hard-won quality lessons.

**`dispatch_session()`** runs a fresh session for a bounded sub-task: it injects an
optional structured `## Session Context` block, executes, captures output, emits the
`session_dispatched` / `session_completed` events, and **always tears the session
down in a `finally`**. It never raises — failures become a `SessionOutcome(success=
False)`. Sessions are disposable: spin one up, get an answer, throw it away.

**`dispatch_antagonistic_review()`** is the quality keystone. It captures
`git diff HEAD` to **bound a reviewer to only the changes** (not pre-existing code),
forwards the spec as the definition of correctness, and instructs a P0/P1/P2
classification with file/line specificity.

**Design Decision — Quality comes from an adversarial reviewer bounded to the diff,
not from trusting the author.**
An agent reviewing its own work, or reviewing the whole repo, is unreliable: it
rationalizes its choices or drowns in unrelated code. A *separate* session, shown
*only the diff* and the spec, and told to find problems, produces actionable,
scoped findings. Bounding the reviewer to `git diff HEAD` is what keeps the review
about *this change*. The understudy makes this an architectural centerpiece (§10).

## 9.5 Deterministic convergence gates

LLM judgment decides strategy; *deterministic checks* decide done. `resolver_support`
provides `run_build_test()` — build → test → lint, each required to exit 0, plus a
regression check against a `baseline_failures` count so a change cannot quietly add
failures. `auto_detect_trial_config()` finds the project type (pyproject → Cargo →
package.json → Makefile); `build_delivery_prompt()` standardizes branch/commit/push/
PR with mandatory artifact files; `consume_messages()` pulls the numbered-JSON inbox
(§8).

**Design Decision — "Done" is gated on real build/test/lint exit codes, not on the
model's say-so.**
A model will happily declare success. A non-zero `pytest` exit will not. Routing the
final go/no-go through deterministic commands turns "I think it works" into "the
tests pass," and the regression check turns "no *new* failures" into a measured fact.
This is where autonomous work earns trust: the convergence criterion is executable.

The SDK gives every resolver the same engine. §10 shows three radically different
strategies built on top of it.
