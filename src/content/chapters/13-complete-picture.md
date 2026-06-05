---
title: "The Complete Picture & Where It's Going"
chapter: 13
---

# Section 13: The Complete Picture & Where It's Going

Every box in the §2 map is now familiar. This section assembles them into one layered
model, then looks honestly at the open edges — because mastery includes knowing what is
*not* finished.

## 13.1 Six layers

Read bottom-up. Each layer depends only on the ones below it; each can be replaced
without touching the layers underneath.

```
┌──────────────────────────────────────────────────────┐
│    6  EDGE — bridge + GHA triage/review + GitHub     │
└──────────────────────────────────────────────────────┘
  │
  │
  ▼
┌──────────────────────────────────────────────────────┐
│     5  CONSUMER — SPA shell + dynamic viewports      │
└──────────────────────────────────────────────────────┘
  │
  │
  ▼
┌──────────────────────────────────────────────────────┐
│ 4  RESOLVERS — dot-graph / orchestrator / understudy │
└──────────────────────────────────────────────────────┘
  │
  │
  ▼
┌──────────────────────────────────────────────────────┐
│  3  SDK — SessionFactory / EventEmitter / dispatch   │
└──────────────────────────────────────────────────────┘
  │
  │
  ▼
┌──────────────────────────────────────────────────────┐
│     2  PLATFORM — FastAPI daemon (still center)      │
└──────────────────────────────────────────────────────┘
  │
  │
  ▼
┌──────────────────────────────────────────────────────┐
│     1  RUNTIME — Incus / Docker + .resolve/ bus      │
└──────────────────────────────────────────────────────┘
```

The asymmetry from §3 is the whole picture in one glance: **layer 2 is the still
center.** Layers 1 and 6 are how work enters and is isolated; layers 3–5 are how it
gets done and shown. The platform depends on none of them and exposes contracts to all
of them — the protocol (§5), the event vocabulary (§7), A2UI (§8), and `ViewportProps`
(§11). Four contracts hold the six layers together.

## 13.2 Where new things go

The payoff of the architecture is that "where does X go?" almost always has a boring
answer:

| You want to… | You add… | What stays untouched |
|---|---|---|
| Add a new resolution strategy | a resolver package (§5) + optional viewport (§11) | the platform, the SDK, the SPA shell |
| Support a new git host | a `GitProvider` implementation | resolvers, the protocol |
| Support a new container runtime | a `ContainerProvider` implementation | everything above layer 1 |
| Add a new interaction form | an A2UI surface in your resolver (§8) | the platform's validator |
| Surface a new progress signal | a `resolver:*` event field (§7) | the platform's event reader |
| Change how a resolver looks | that resolver's viewport `types.ts` (§11.6) | the shell, other viewports |
| Trigger runs a new way | an edge integration that POSTs `/instances` | the entire platform below |

If your change requires editing the platform daemon, pause and ask whether it is really
mechanism — or whether it is policy that belongs in a resolver, a provider, or an edge.
Most of the time it is the latter.

## 13.3 Where it's going — the roadmap

**The three-concern architecture (§2.4) is the target shape.** Triage (Concern 1) and
review (Concern 3) move fully into GitHub Actions + attractor pipelines, joined to
Resolve (Concern 2) only by the `/resolve new_instance(...)` command string. Two active
build-outs:

- **Bridge `new_instance()` syntax** (`amplifier-app-resolve-bridge-github`): parse
  `new_instance(resolver="…", …)` in the bridge, add `needs-attention` label
  add/remove for HITL events, and remove the bridge's auto-triage handler (triage moves
  to GHA).
- **GHA workflows + `simple-fix.dot`**: `issue-triage.yml` and `pr-review.yml`
  workflows plus `triage-review.dot` and `simple-fix.dot` pipelines, closing the
  end-to-end chain: *issue opened → triage → `/resolve new_instance(...)` → bridge →
  resolver → PR created → `/review-pr` → review.*

**Viewport work is active** across all three viewport repos, with edge contracts
(`edge-08a/b/c`) as the schemas and the SPA shell ready to load them. The understudy's
`decision_override` message type is specified and documented in edge-08c, but the
*resolver-side* `on_message` handler does not yet exist — `props.onDecisionOverride` is
presentation-preview only until it lands.

## 13.4 Known open edges

Honest mastery means holding the unfinished parts in view:

- **`subgraph_runner` not wired (support#249).** `shape=folder` / `shape=house` nodes
  create a child `HandlerRegistry` without a `subgraph_runner`, so nested pipelines
  fail. The fix lives in `amplifier-bundle-attractor`. This blocks the real
  `resolve-router.dot` from using nested pipelines in production.
- **Router conditional edges.** The LLM returns prose, not JSON, on conditional edges;
  an unconditional fallback currently catches it. The durable fix needs an edge-condition
  format.
- **CR-1 CI-bundle side (G-1).** `parent_id` propagation landed resolver-side
  (`c2fa831`) but `hook-context-intelligence`'s config resolver does not yet recognize
  `parent_id`. A ~30 LOC change in `amplifier-bundle-context-intelligence` completes the
  cross-session stitching (§9.2).
- **Event-vocabulary versioning (deferred deliberately).** v1 has *no* version field —
  the only consumers are in-tree, so the team may break the contract at will. There is a
  **named trigger**: the moment a third-party resolver author depends on the `resolver:*`
  contract, introduce `event_vocabulary_version` in the manifest *before* merging the
  triggering change. The trigger exists so the decision is not forgotten, not because the
  policy is decided.

**Design Decision — Versioning, taxonomies, and capability contracts are deferred until a
real consumer forces them.**
v1 has no event version field, no enforced phase taxonomy, and `attractor-pipeline` is
listed as a capability without a contract. Each is deferred with a *named trigger* rather
than built speculatively. This is Core's ruthless simplicity applied to a contract: do not
pay for generality until a second consumer makes it real — but write down exactly what will
force the decision, so the deferral is a choice and not an oversight.

## 13.5 Closing

Resolve is one idea pursued without compromise: **keep the mechanism old so the strategies
can be new.** The platform validates structure and routes events; it never interprets
meaning. From that single restraint follow the instance lifecycle, the sealed container,
the event vocabulary, the three interaction surfaces, the SDK, the three opposing
resolvers, the plugin viewports, and the inner loop — each a different face of the same
bright line.

When you change the platform, your real job is to *defend that line*: to keep asking
whether the thing you are adding is mechanism the platform should own, or policy that
belongs to a resolver, a provider, or an edge. Get that judgment right, consistently, and
the center stays still while the edges move at any speed. That is what it means to be a
master of Resolve.
