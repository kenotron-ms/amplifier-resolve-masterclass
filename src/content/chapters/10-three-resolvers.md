---
title: "Three Resolvers, Three Theories of Correctness"
chapter: 10
---

# Section 10: Three Resolvers, Three Theories of Correctness

Here is where the whole architecture pays off. Three resolvers ship in-tree. They
satisfy the same protocol (§5), emit the same vocabulary (§7), and run on the same
SDK (§9). The platform cannot tell them apart. Yet each answers a different — almost
philosophical — question:

> **How should an AI agent be governed so that its output can be trusted?**

dot-graph, orchestrator, and understudy are three incompatible answers. Studying
them side by side is the fastest way to understand both the design space and why the
platform refuses to take a side.

## 10.1 dot-graph — resolution as a *compiled artifact*

**The metaphor:** the pipeline-as-program. A Graphviz `.dot` file is a code-first
DSL in which **every node compiles to an independent Amplifier agent session**. The
resolver itself is a thin loader; the intelligence lives in the graph.

**The theory of correctness:** *author the strategy ahead of time, then execute it
deterministically.* Fan-out/fan-in, multi-model consensus (a different `llm_provider`
per node), and human gates are all expressed as **graph structure**, not runtime
control flow. Execution is delegated to the attractor `PipelineEngine` /
`AmplifierBackend` (from `amplifier-bundle-attractor`, itself extending
`strongdm/attractor`). Correctness is a property of *graph design* — reproducible,
inspectable, and resumable.

**How it works:** `run()` loads the `.dot` source (pipeline name → `.resolver.yaml`
manifest → bundled `.dot`, with path/`dot_content` fallbacks), auto-discovers
provider profiles by scanning node `llm_provider` attributes, **writes `graph.dot`
to the data dir and emits it as the first `resolver:artifact`**, then hands control
to the engine. An `_EventEmitterHookBridge` adapts the engine's async hooks
(`pipeline:node_start` / `node_complete` / `stage_failed`) into `emit()` /
`update_state()` calls, maintaining a per-node status dict so the viewport shows live
progress. The `resolver:phase` chain is `pipeline_setup → session_setup → executing`.
`supports_resume` is **true** — pipeline status is checkpointed.

> **Invariants that burn.** `graph.dot` is written to `/project/.resolve/data/graph.dot`;
> changing that path silently breaks the live-graph endpoint mid-run. `_write_data_file`
> must `mkdir(parents=True, exist_ok=True)` because the platform does not pre-create
> `data/`. Per-branch events from `ParallelHandler` carry a `via_parallel=True` marker
> that downstream observability and attractor depend on — do not change the event
> shape without coordinating with attractor. There are **four exit paths** that must
> each emit `resolver:completed` (§7.3).

**Design Decision — dot-graph puts the strategy in a versioned artifact, not in
code.**
A `.dot` file is data: it can be reviewed, diffed, reused, and reasoned about before
anything runs. Pushing the resolution strategy into an inspectable graph trades
runtime flexibility for reproducibility and auditability — the right trade when you
want the *same* resolution to happen the same way every time.

## 10.2 orchestrator — resolution as *live delegation*

**The metaphor:** the manager who never touches the code. A single long-lived LLM
session is a *coordinator*, not an executor. It plans, delegates, monitors, and
synthesizes.

**The theory of correctness:** *decompose at runtime and apply judgment.* The
orchestrator agent receives a free-text `task` and a five-tool suite — `launch_worker`,
`get_worker_result`, `send_to_worker`, `destroy_worker`, `ask_user` — and figures out
the decomposition as it goes. Workers are autonomous Amplifier sessions in **isolated
Incus/Docker sub-containers** (`resolve-{id}-env-{uuid}`, §6), spawned via the
platform's internal broker API, capped at `MAX_WORKERS`, and auto-destroyed once their
results are collected.

**How it works:** `launch_worker` POSTs to the broker, registers a `WorkerInfo`, and
spins a **non-blocking background polling task** (5s interval) so independent
sub-tasks make progress in parallel; worker status flows `launched → running →
completed/failed`, and truncated output is surfaced inline (`[OUTPUT TRUNCATED AT
50KB]`) so the model does not misdiagnose. A `WorkerRegistry` tracks every worker's
lifecycle under a lock. A `StateAccumulator` (the viewport contract,
`OrchestratorState`) maintains a capped `narrative` ring, a `timeline` of lane spans,
and a `workers` roster with **merge-not-replace** semantics so a completed worker
never blanks out. **Completion is the LLM session returning** — its final response
becomes the summary artifact, and a `finally` always tears down workers.

> **Invariants that burn.** The worker-stdout `truncated` marker is load-bearing — the
> model depends on it; do not suppress it. In tests, patch `SessionFactory` at its lazy
> import site (`amplifier_resolve.core.session_factory.SessionFactory`), not at a name
> that does not exist until `run()` defers the import. The tool is `launch_worker`,
> never `spawn_worker`.

**Design Decision — orchestrator trusts runtime judgment and escalates to a human,
rather than committing to a plan up front.**
Maximum flexibility, minimum guarantees: there is no fixed pipeline and no pre-committed
success criteria. When the agent is unsure it calls `ask_user`. This is the right trade
when the task is open-ended and the shape of the work cannot be known before it starts —
the inverse of dot-graph's pre-authored determinism.

## 10.3 understudy — resolution as a *governed contract*

**The metaphor:** the disciplined apprentice who agrees on the goal *before* acting
and proves the result *after*. The most opinionated strategy: **trust nothing
unverified.**

**The theory of correctness:** *align on intent, commit to verifiable success, then
prove it independently.* A 4-phase state machine — **aligning → executing → verifying
→ completing** — is bracketed by two human approval gates.

1. **Aligning (mind-meld).** Pull codebase signals, synthesize a `VisionSpec` (with
   redaction passes), and present a 4-panel **review-vision gate**. During this phase
   the viewport renders an `InitOverlay` driven by `init_steps` the resolver writes to
   state (`Reading codebase`, `Looking at profile`, `Drafting vision`, `Forming
   questions`).
2. **Theory of Success.** Generate 2–4 verifiable **`Journey`** commitments *before*
   execution. Each `Journey` has a prose `verification_method` and a controlled
   **`routing_tier`** (`code_inspection` / `command_execution` / `browser_automation`).
3. **Executing.** Do the work (agentic mode drives multi-turn workers via an
   `OrchestratorBrain` with bounded mailboxes; deterministic mode is the fallback).
4. **Verifying.** An **independent `understudy-verifier` session** — a *different*
   phase name, so a fresh session, never the worker's — checks each journey. The
   router partitions journeys by `routing_tier`: behavioral tiers go to a reality-check
   DTU container; the rest run in-process. Results are PASS/FAIL/**UNKNOWN** with an
   honest `failure_class` (blocked vs notrun) — the design refuses to overstate
   confidence.
5. **Completing.** A completion gate approves the result against the *original* intent,
   with a bounded remediation loop.

**Two distinct phase vocabularies — do not conflate them.** The coarse SDK
`resolver:phase` stream (`aligning`/`executing`/`verifying`/`completing`) goes to the
platform; a fine-grained `understudy.phase_transition` stream (an 11-value
`UnderstudyVisionState.phase` enum: `mind-melding`, `dialoguing`, `synthesizing`,
`awaiting-approval`, `approved`, `rejected`, `executing`, `verifying`, `completing`,
`completed`, `failed`) goes to the viewport via `update_state`. Writing one into the
other's channel silently produces either an invalid viewport state or a non-canonical
event — and there is no platform-level validation for either mistake.

> **Invariants that burn.** The `_phases_announced: set[str]` idempotency guard is
> load-bearing: the remediation loop re-enters phase code, and without the guard
> duplicate `resolver:phase` events corrupt platform tracking (§7.3). `routing_tier`
> is *the* verifier routing key — freeform-prose routing is dead; new journey-producing
> code must populate it. The `_state_mirror` workaround is **gone** (PR #18); do not
> re-add it (§7.4). `supports_resume` is **false** — the conversational state is too
> rich to checkpoint.

**Design Decision — understudy makes verification a first-class peer to execution and
the human approve twice.**
Commitments are made *before* work and bind both the worker and the verifier; the
verifier is a separate session shown the journeys, not the author's reasoning; and a
person signs off on both the plan and the result. Correctness here is *contractual and
proven*, never assumed. It is the most expensive strategy and the right one when the
cost of a wrong-but-confident result is high.

## 10.4 Three answers, one platform

| | dot-graph | orchestrator | understudy |
|---|---|---|---|
| Metaphor | compiled artifact | live delegation | governed contract |
| Strategy decided | ahead of time | at runtime | aligned, then committed |
| Correctness from | graph design | runtime judgment | independent verification |
| Human role | gates in the graph | `ask_user` on demand | two approval gates |
| Resumable | yes | (session-bound) | no |
| Best when | reproducibility matters | the task is open-ended | a wrong answer is costly |

**Design Decision — The platform ships three opposing strategies and endorses none.**
If the platform had an opinion about how resolution *should* work, two of these three
could not exist. Because it validates structure and routes events (§3) and nothing
more, all three coexist — and a fourth, yet unimagined, can join them without a
platform change. The three resolvers are not just features; they are the proof that
the bright line holds. §11 shows how each ships its own face to the user.
