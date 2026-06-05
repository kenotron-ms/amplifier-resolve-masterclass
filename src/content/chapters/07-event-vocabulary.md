---
title: "The Event Vocabulary"
chapter: 7
---

# Section 7: The Event Vocabulary

This is the observability contract — the small, fixed set of events every resolver
agrees to emit so that a run becomes legible without the platform ever
understanding the run's internals. If you internalize one technical section, make
it this one. The completion invariant here is the difference between a platform
that works and one that silently hangs.

## 7.1 A vocabulary, not a schema

The events ride on the *existing* context-intelligence envelope — there is no new
transport, no sidecar log:

```json
{
  "event": "<event-name>",
  "workspace": "<workspace-slug>",
  "timestamp": "<ISO-8601 UTC>",
  "data": { "session_id": "…", "parent_id": "…", "…": "…" }
}
```

The design is deliberately a **vocabulary**, not a schema. A schema would lock down
the shape of `data` per event. A vocabulary defines only: the set of event *names* a
cross-resolver consumer may rely on, the fields inside `data` those consumers may
read, and which fields a resolver SHOULD vs MAY provide. Resolver authors stay free
to add their own keys; cross-resolver consumers ignore what they do not recognize.

**Design Decision — Define a vocabulary of names, not a schema of payloads.**
A schema would force every resolver into one rigid `data` shape and make every new
field a breaking change. A vocabulary fixes only the *names* the platform interprets
and lets `data` grow freely underneath. It is forward-compatible by construction —
the same reason Core defines event *names* and lets hooks decide what the payload
means.

## 7.2 Eight events, all `resolver:*`

Two mandatory fields inside `data` come from the kernel, not the resolver:
`session_id` (the emitting session) and `parent_id` (the parent session, which must
propagate through `SessionFactory.create_phase_session` so the cross-session graph
stitches a resolver run to its phases — §9).

| # | Event | When | Required `data` fields |
|---|---|---|---|
| 1 | `resolver:created` | once, before any work | `resolver_name`, `resolver_version`, `instance_id`, `params` (sanitized), `capabilities_granted` |
| 2 | `resolver:phase` | at each phase boundary | `phase` (free-form), `previous_phase` (opt) |
| 3 | `resolver:progress` | when meaningful (opt) | `milestone`, `fraction` (`[0,1]` or `null`) |
| 4 | `resolver:artifact` | per output produced | `kind` (`pr`\|`branch`\|`commit`\|`file`\|`summary`\|`verdict`\|`error`\|`other`), `value` |
| 5 | `resolver:input_requested` | on `request_input()` (SDK-emitted) | `request_id`, `surface_id`, `prompt` |
| 6 | `resolver:input_responded` | on response/timeout (SDK-emitted) | `request_id`, `outcome`, `duration_s` |
| 7 | `resolver:health` | under stress (opt) | `signals` (free-form) |
| 8 | `resolver:completed` | exactly once, before exit | `outcome` (`success`\|`partial_success`\|`failed`\|`cancelled`), `summary`, `duration_s`, `artifact_count` |

The **four-event chain** — `created → phase → artifact → completed` — is the minimum
a resolver must emit for the platform to track it correctly. Events 5 and 6 are
emitted by the SDK on the resolver's behalf, so resolver authors get them "for free"
by calling `request_input()`. Events 3 and 7 are optional signal you add when you
have something worth surfacing.

The platform reads phase to show "running phase X," progress for "N% done,"
artifacts for "produced these outputs," an unmatched `input_requested` for "blocked
on input," and `health` to flag at-risk runs. It reads **only** `resolver:*` events
for cross-resolver views. Internal events under `{resolver_name}:*` are the
resolver's private business and the platform never interprets them.

## 7.3 The completion invariant

**Design Decision — `resolver:completed` must be emitted at *every* exit path —
success, failure, and exception — or the platform assumes the worst.**

This is the single most important invariant in the platform. The platform's
notification loop (`orchestrator.py:_notification_loop`) routes on
`resolver:completed`. If it is not emitted on some code path, the loop waits until a
fallback fires — and one missed exit path is one silent hang.

The contract, in priority order (the platform-side view is §4.4):

1. **`resolver:completed`** — authoritative, structured.
2. **Process exit** — fallback. Exit 0 → `success`; non-zero → `failed`; no
   structured error.
3. **Watchdog timeout** — SIGTERM → SIGKILL; marked `crashed`.

The legacy `__RESOLVE_WORKER_COMPLETE__` stdout magic string was removed **as the
resolver completion signal** (PR #51, `376b915`) and replaced by `resolver:completed`.
**Do not re-introduce it in that role.** A typed terminal event cannot be accidentally
printed by a log line, carries structured outcome and error, and is observable as data
rather than text.

> **Precision, because the string still exists in the tree.** The marker survives at a
> *lower* layer — as a worker-subprocess done-marker in the orchestrator's
> `launch_worker` sub-container path (`routes/internal.py`) and the container-level
> exec-completion detection in `incus.py` / `docker.py`. That is a different concern
> (has *this shell command* finished?) from resolver completion (has *the run*
> finished, and how?). The contract that moved to `resolver:completed` is the
> resolver-level one; the low-level process marker is not it. Conflating the two is the
> trap.

> **Where this bites, concretely.** dot-graph has *four* exit paths that must each
> emit `resolver:completed`: factory-startup failure, success, pipeline failure, and
> the exception handler. Understudy's remediation loop legitimately re-enters phase
> code, so it guards coarse-phase emission with a `_phases_announced: set[str]`
> idempotency set — without it, duplicate `resolver:phase` events corrupt the
> platform's phase tracking. The invariant is simple to state and easy to violate;
> respect it at every `return` and every `except`.

## 7.4 State: `merge_state` vs `update_state`

Alongside events, a resolver publishes a live `state.json` snapshot the viewport
renders (§11). Two methods write it, and confusing them is a classic regression:

- **`update_state(**kwargs)`** — *atomically overwrites* `state.json` (write to a
  temp file, `os.replace`). It **replaces** the whole document. Anything not in this
  call is gone.
- **`merge_state(**kwargs)`** — read-modify-write: read the existing state, overlay
  the new keys, write back. It **preserves** accumulated fields.

The platform's `_notification_loop` calls `merge_state(**safe_data)` for partial
`state_update` payloads — **not** `update_state` — precisely so that resolvers
sending incremental updates (narrative, timeline, the worker roster) do not wipe out
everything sent before. A regression-trap test guards this (PR #52, `d4e30ab`).

**Design Decision — Partial state updates merge; full snapshots replace; the daemon
merges so resolvers don't have to.**
`update_state` is atomic and safe for a single writer publishing a complete
snapshot. `merge_state` is the accumulation primitive for incremental progress. The
daemon doing the merge is what let understudy *delete* its old `_state_mirror`
workaround (PR #18) — once the daemon merges correctly, the resolver stops
re-emitting all accumulated state on every update. Re-introducing a resolver-side
mirror is a regression with its own trap test
(`test_update_state_not_overridden_post_state_mirror_removal`).

## 7.5 The three event tiers

Zooming out, all events fall into three tiers:

- **Tier 1 — Platform-level** (host-emitted, stable contract):
  `resolve.container.creating`, `resolve.setup.*`, `resolve.worker.*`,
  `resolve.instance.status_changed`, `resolve.input.requested`,
  `resolve.resolver.session_*`. These are *the platform narrating its own work*.
- **Tier 2 — SDK infrastructure events:** currently empty; no active emit sites.
- **Tier 3 — Resolver-specific** (`{resolver_name}.{event}`): the resolver's private
  vocabulary. The platform makes no assumptions about these.

The `resolver:*` vocabulary of §7.2 is the agreed cross-resolver layer that sits
between Tier 1 (platform) and Tier 3 (private): emitted by resolvers, interpreted by
the platform. It is the one place the two worlds meet — and the discipline that
keeps the bright line (§3) intact while still making every run legible.

Events make a run *observable*. §8 covers how a run becomes *interactive*.
