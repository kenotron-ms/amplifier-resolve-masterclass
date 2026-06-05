---
title: "Appendix: Glossary & Invariants"
chapter: "A"
---

# Appendix: Glossary & Cross-Repo Invariants

## A.1 Glossary

| Term | Meaning |
|---|---|
| **Instance** | The unit of work: one run of one resolver against one request (§1, §4). |
| **Resolver** | A pluggable strategy that satisfies the 12-member protocol and resolves a request (§5). |
| **Resolver Protocol** | The structural contract every resolver implements: 4 properties + 8 methods (§5). |
| **Platform / daemon** | The FastAPI service (`amplifier-resolve`) that owns lifecycle, isolation, transport, and validation (§2, §3). |
| **Worker container** | The sealed Incus/Docker box one instance runs in, named `resolve-{id}` (§6). |
| **`.resolve/`** | The in-container coordination directory: the filesystem bus between host and resolver (§6.3). |
| **Event vocabulary** | The eight `resolver:*` events every resolver agrees to emit (§7). |
| **A2UI** | The v0.9 wire format for all interaction schemas; validated structurally, never interpreted (§8). |
| **Three surfaces** | Instantiation, input-requests, messages — the three interaction channels (§8.2). |
| **Data bus** | `GET /instances/{id}/data/{path}` — fetch-on-demand for large artifacts (§8.4). |
| **SessionFactory** | The SDK's prepare-once / create-many session engine (§9.1). |
| **EventEmitter** | The per-instance channel for events, state, and input-requests; never raises (§9.3). |
| **Viewport** | A resolver-authored `viewport.js` UI plugin loaded dynamically by the SPA (§11). |
| **`ViewportProps`** | The stable shell↔viewport boundary contract (§11.3). |
| **GenericViewport** | The domain-agnostic fallback UI every resolver gets for free (§11.5). |
| **DTU** | Digital Twin Universe — an Incus container that stands up the whole stack for development (§12.1). |
| **`DEV_RESOLVERS`** | Mechanism that mirrors the local working tree into a Gitea sidecar once, at launch (§12.2). |
| **Capability** | A named thing a resolver declares it needs (`capabilities_required`) and the platform provisions generically. |
| **Bridge** | `amplifier-app-resolve-bridge-github` — translates GitHub comments into `POST /instances`. |
| **Three concerns** | Triage → Implement (Resolve) → Review, joined by the `/resolve new_instance(...)` string (§2.4). |

## A.2 The eight statuses

`created → starting → running → completed | failed | cancelled`, with `running ⇄
awaiting_input` and `running ⇄ paused`. Eight total (§4.1).

## A.3 The event chain

`resolver:created → resolver:phase → resolver:artifact → resolver:completed` is the
required four-event chain. `progress`, `health`, `input_requested`, and
`input_responded` round out the eight; the last two are SDK-emitted (§7.2).

## A.4 Cross-repo invariants — the pitfalls that burn

These are the traps that pass unit tests and break reality. Each maps to a section.

1. **`merge_state` ≠ `update_state`.** The notification loop calls `merge_state` for
   partial updates; `update_state` overwrites the whole document. Regression-trap test
   exists (§7.4).
2. **`resolver:completed` at *every* exit path.** Success, failure, exception. One
   missed path = one silent hang at `_notification_loop` (§4.4, §7.3).
3. **`DEV_RESOLVERS` is a one-time snapshot.** Post-launch edits are not in Gitea;
   re-push or re-launch (§12.2).
4. **Gitea is addressed by `DTU_INCUS_IP`, not `HOST_GW`.** Workers are Incus siblings;
   the sidecar lives in the DTU's Docker (§12.3).
5. **`dev_source_overrides` must be present** in `manifest.json` or DTU runs silently use
   upstream `main` (§12.4).
6. **Worker bind-mount sources must be HOST paths.** Workers do not inherit DTU
   bind-mounts (§12.5).
7. **Two distinct `phase` vocabularies in understudy.** `resolver:phase` (4 values, to
   the platform) vs `UnderstudyVisionState.phase` (11 values, to the viewport). No
   platform validation catches a mix-up (§10.3).
8. **`__RESOLVE_WORKER_COMPLETE__` is removed *as the resolver completion signal*** —
   replaced by `resolver:completed`. It still exists at a lower layer as a
   worker-subprocess done-marker in the orchestrator's `launch_worker` path
   (`routes/internal.py`, `incus.py`, `docker.py`); do not re-introduce it as a
   *resolver-level* completion contract (§7.3).
9. **React must be externalized.** Never bundle React/react-dom in a viewport — the
   dual-React problem crashes hooks. The dev CJS shim is load-bearing (§11.4).
10. **Built viewport bundles must be force-committed** (`git add -f dist/viewport.js`) —
    they are gitignored by default (§11).
11. **`_state_mirror` (understudy) and `resolver_state` (platform) are gone.** Both have
    regression-trap tests; do not re-introduce them (§7.4).
12. **`routing_tier` is the understudy verifier routing key.** Freeform-prose routing is
    dead; new journey-producing code must populate it (§10.3).
13. **`graph.dot` write path is load-bearing** (`/project/.resolve/data/graph.dot`); the
    `via_parallel=True` marker must be preserved (§10.1).
14. **The smoke-test gate** (`smoke-test-dev-resolvers.sh`) is required for any change to
    `amplifier-bundle-resolve` scripts (§12.6).

## A.5 Authoritative sources

When in doubt, the code wins over any doc. Primary references:

- `amplifier-resolve/docs/ARCHITECTURE.md` — host-layer architecture (note: its
  `ResolveCore` model predates the containerized worker; treat the event vocabulary as
  the authoritative completion contract — §5.2).
- `amplifier-resolve/docs/designs/resolver-event-vocabulary.md` — the event contract and
  its known gaps (G-1…G-5).
- `amplifier-resolve/docs/INSTANCE_LIFECYCLE.md`, `EVENTS_CONSUMER_GUIDE.md`,
  `RESOLVER_REALITY_CHECK_GUIDE.md`, `ROADMAP.md`.
- Per-repo `AGENTS.md` — the pitfall lists and verification gradients that must be
  honored.
- `amplifier-bundle-resolve/docs/edges/edge-08a…c` — the viewport state schemas.
- The workspace root `AGENTS.md` — cross-repo invariants and current work focus.

---

*This appendix is a quick-reference. Every entry has a fuller treatment in its section.
When the platform changes, update both the section and the relevant invariant here.*
