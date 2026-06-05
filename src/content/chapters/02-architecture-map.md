---
title: "Architecture Map"
chapter: 2
---

# Section 2: Architecture Map

## A map of the territory before we walk it

This section is the city map. You do not need every building yet — you need the
neighborhoods and the roads between them. Every box here gets its own section
later.

```
                                      ┌─────────────────────┐                    ┌──────────────────────────┐
                                      │   agent / script    │                    │        CI bridge         │
                                      │                     │                    │      (e.g. GitHub)       │
                                      └─────────────────────┘                    └──────────────────────────┘
                                        │                                          │
                                        │ POST /instances                          │
                                        ▼                                          ▼
┌─────┐┌────────────────────────┐     ┌─────────────────────────────────────────────────────────────────────┐     ┌──────────────────────┐
│ CLI ││ resolver: orchestrator │ ◀── │                                                                     │ ──▶ │ resolver: understudy │
└─────┘└────────────────────────┘     │                                                                     │     └──────────────────────┘
  │      │                            │                          amplifier-resolve                          │       │
  │      │                            │                       FastAPI platform daemon                       │       │
  │      │                            │                                                                     │       │
  │      │                            │                                                                     │       │
  └──────┼──────────────────────────▶ │                                                                     │       │
         │                            └─────────────────────────────────────────────────────────────────────┘       │
         │                              │                      ▲                   ▲                                │
         │                              │ launch container     │ POST /instances   ╵ stands up                      │
         │                              ▼                      │                   ╵                                │
         │                            ┌─────────────────────┐  │                 ┌──────────────────────────┐       │
         │                            │ resolver: dot-graph │  │                 │ amplifier-bundle-resolve │       │
         │                            │                     │  │                 │    provisioning / DTU    │       │
         │                            └─────────────────────┘  │                 └──────────────────────────┘       │
         │                              │                      │                                                    │
         │                              │ events / state       │                                                    │
         │                              ▼                      │                                                    │
         │                            ┌─────────────────────┐  │                                                    │
         │                            │ resolver viewports  │  │                                                    │
         └──────────────────────────▶ │    (viewport.js)    │ ◀┼────────────────────────────────────────────────────┘
                                      └─────────────────────┘  │
                                        │                      │
                                        │ loaded by            │
                                        ▼                      │
                                      ┌─────────────────────┐  │
                                      │    SPA (browser)    │ ─┘
                                      └─────────────────────┘
```

## Reading the diagram

- **Arrows are control + data flow**, top to bottom: a request enters at the top
  from *some* consumer, and the resolver's artifacts (a PR, a review, a report)
  flow back out to whoever is watching.
- **The top row is any consumer, not one privileged path.** The SPA, an agent or
  script, a CLI, a CI bridge — all reach the platform the same way: `POST
  /instances`. The GitHub bridge shown here is one consumer among several (§1,
  "Who drives Resolve"), included because the worked example below uses it.
- **The platform daemon is the still center.** Everything above it — any consumer
  that can call the API — is *how work arrives*. Everything below it (resolvers,
  viewports, the SPA-as-renderer) is *how work gets done and shown*. The platform
  depends on neither — it exposes contracts and lets the edges move.
- **Each instance gets its own container.** No instance shares memory, process
  space, or filesystem with another. The only link between runs is a `parent_id`
  (§4), exactly as in Core's parent/child sessions.
- **The viewport and the SPA are pure consumers.** They read the platform's HTTP,
  SSE, and data-bus surfaces. Remove them entirely and every instance still runs
  identically — there is simply nothing watching.

## The repositories

Nine repositories make up the platform. Knowing which owns what is half of
mastery.

| Repo | Role |
|---|---|
| `amplifier-resolve` | The platform daemon (FastAPI). Owns instance lifecycle, the monitor/notification loop, the event-vocabulary contract, and `state.json` accumulation. |
| `amplifier-resolver-dot-graph` | DOT-pipeline resolver. Executes a `.dot` graph node-by-node via the attractor `PipelineEngine`. |
| `amplifier-resolver-orchestrator` | Orchestrator resolver. A long-lived session that spawns worker sub-containers and coordinates them. |
| `amplifier-resolver-understudy` | Understudy resolver. A 4-phase governed workflow with intent alignment, independent verification, and HITL gates. |
| `amplifier-app-resolve` | The React 19 / Vite / TypeScript SPA. Hosts the generic viewport and loads resolver viewports dynamically. |
| `amplifier-resolver-{dot-graph,orchestrator,understudy}-viewport` | Three custom viewport UIs, one per resolver, each serving a `viewport.js` bundle. |
| `amplifier-bundle-resolve` | Provisioning bundle. The DTU, the `DEV_RESOLVERS` mechanism, the Gitea sidecar, the resolve-stack scripts. |

## How work reaches Resolve

Before the worked example, hold the general shape in mind. Resolve is API-first,
so the consumer patterns are open-ended:

| Pattern | Who calls | Shape |
|---|---|---|
| **Interactive** | a person in the SPA | pick a resolver, fill the A2UI form, watch, steer |
| **Programmatic** | another agent or script | `POST /instances` headless, read events/state/artifacts |
| **Command-line** | a developer or job | a CLI wrapping the same API |
| **Event-driven** | a bridge (e.g. GitHub) | an external event becomes an instance |
| **Scheduled** | a timer / cron | the same `POST /instances`, on a clock |

None of these is *the* way to use Resolve. They are all the same act — a caller
selecting a resolver and submitting input — seen from different angles. The rest
of this section walks one concrete instance of the **event-driven** pattern.

## A worked example: GitHub-driven triage → implement → review

This is **one integration**, not the architecture. It wires Resolve into a larger
GitHub loop and is currently the flagship deployment, which makes it a good
illustration of how the platform plugs into the outside world. Read it as an
*example*, not a definition — swap GitHub for any other event source and the
platform does not change.

The loop organizes a real deployment's work into three independently-evolving
concerns:

```
┌────────────────────┐
│    issue.opened    │
└────────────────────┘
  │
  │ 1 triage
  ▼
┌────────────────────┐
│  triage pipeline   │
└────────────────────┘
  │
  │
  ▼
┌────────────────────┐
│      /resolve      │
│ new_instance(...)  │
└────────────────────┘
  │
  │ 2 implement
  ▼
┌────────────────────┐
│    Resolve API     │
│ resolver container │
└────────────────────┘
  │
  │
  ▼
┌────────────────────┐
│     PR created     │
└────────────────────┘
  │
  │ 3 review
  ▼
┌────────────────────┐
│  review pipeline   │
└────────────────────┘
  │
  │
  ▼
┌────────────────────┐
│ PR review comments │
└────────────────────┘
```

Resolve — everything in the map above — is **Concern 2**. Triage decides *what*
to resolve and with which resolver; the bridge translates a comment into an
instance; Resolve runs it; review closes the loop on the resulting PR. Keeping
these as three separate concerns means each can evolve independently: a smarter
triage pipeline does not touch the platform, and a new resolver does not touch
triage.

**Design Decision — Triage, implementation, and review are separate concerns
joined by a text command, not one monolith.**
The seam between them is a comment string (`/resolve new_instance(...)`). A string
is the loosest possible coupling: anything that can post a comment can drive the
platform, and the platform never needs to know who asked. Fusing the three would
make the triage logic and the review logic into platform features — exactly the
policy-in-the-kernel mistake the whole design exists to avoid (§3).

With the territory mapped, §3 explains the principles that shaped it.
