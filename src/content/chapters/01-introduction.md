---
title: "Introduction"
chapter: 1
---

# Section 1: Introduction

## From one session to a platform of runs

If you have used Amplifier, you have run a single session: you type a request, an
orchestrator drives a loop, tools fire, and a response comes back. One process.
One conversation. One harness wrapped around one model. When it ends, it ends.

Amplifier Resolve answers a different question:

> What if the request did not come from a person at a terminal, but from
> somewhere else entirely — a browser form, another program, a scheduled job, a
> CI event? What if the work took an hour, not a minute? What if it needed to run
> somewhere sealed, where a runaway process could not touch anything that
> mattered? What if you needed to *watch* it the whole time — from a browser,
> from another program, from a dashboard — without ever interrupting it? And what
> if you wanted to swap the entire *strategy* of how the work gets done without
> touching any of that machinery?

That is Resolve. It is the platform that takes a unit of work, runs a pluggable
**resolver** inside an isolated container, narrates the run through a fixed
observability contract, relays human input both ways, and surfaces whatever the
resolver produces at the end — often a pull request, but just as easily a review,
a report, a verdict, or a set of files.

## Who drives Resolve

A request can originate anywhere that can speak the platform's HTTP API. A person
clicking through the SPA. Another agent or script calling `POST /instances`
headlessly. A command-line tool. A scheduled job. An event-driven bridge that
turns a GitHub issue comment into a run. Resolve does not privilege any of them —
to the platform they are all just *a caller selecting a resolver and submitting
input*.

This masterclass uses one such integration — a GitHub-driven **triage → implement
→ review** loop — as a running example, because it is concrete and currently the
flagship deployment. Treat it as an *illustration* of the platform's shape, not
its definition. The platform is the constant; the consumers, like the resolvers,
are open-ended.

**Design Decision — Resolve is consumer-agnostic; it is an API, not an app.**
The platform exposes HTTP / A2UI / SSE contracts and runs whatever instance a
caller asks for. It has no built-in notion of "the GitHub flow," "the UI flow,"
or any other privileged path. Baking one consumer's assumptions into the platform
would make every other consumer a second-class citizen and re-introduce policy
into the core. The bright line (§3) governs *who asks* exactly as it governs
*what runs*.

## The operating-system analogy, one layer up

The Core Masterclass leans on an operating-system analogy: a small kernel at the
center, modules plugging in from the outside, *mechanism not policy*. Resolve
sits directly on top of that kernel, and it is most clearly understood by
extending the same analogy upward.

| OS concept | Amplifier Core | Amplifier Resolve |
|---|---|---|
| The program you run | a module | a **resolver** |
| A running program | a session | an **instance** |
| Address space / isolation | the session boundary | a **worker container** (Incus/Docker) |
| System calls / observability | hooks & events | the **`resolver:*` event vocabulary** (§7) |
| Standard I/O with the user | the CLI | **A2UI** surfaces (§8) |
| The display driver | the terminal renderer | a **viewport** plugin (§11) |
| `init` / process supervisor | the orchestrator module | the **platform daemon** (FastAPI) |

An **instance** is the unit of work — a single run of a single resolver against a
single request. It is to Resolve what a process is to an operating system: it has
a lifecycle, an isolation boundary, a status, and a parent it can be linked to.
Everything in this document orbits the instance.

**Design Decision — The unit of work is the *instance*, not the *session*.**
A session is one AI conversation. An instance is a *governed run* that may use
many sessions, span hours, pause for a human, spawn workers, and survive a
process restart. Conflating the two would force every long-running, human-gated,
multi-session workflow back into a single chat loop. The instance is the
container concept that makes durable autonomous work expressible.

## What a resolver is — and why it is the whole point

A **resolver** is a strategy for resolving a request. "Fix this bug." "Implement
this feature." "Review this PR." A resolver decides *how* that gets done: what to
ask the user for, what repos to clone, what phases to move through, how to verify
the result, when to stop.

Three ship in-tree today, and they could not be more different in temperament:

- **dot-graph** treats resolution as a *compiled artifact* — a Graphviz pipeline
  where every node is its own agent session.
- **orchestrator** treats resolution as *live delegation* — one long-lived
  manager session that spawns and coordinates worker sub-containers at runtime.
- **understudy** treats resolution as a *governed contract* — align on intent,
  commit to verifiable success criteria, execute, then prove the result with an
  independent verifier and two human approval gates.

They all satisfy the same protocol (§5) and emit the same event vocabulary (§7).
The platform cannot tell them apart, and that is the design working. We unpack
all three in §10.

**Design Decision — The platform never knows what a resolver *means*.**
It validates that inputs are structurally well-formed and routes events,
responses, and messages to the right place. It never interprets the semantics of
a field, a phase, or an artifact. This single restraint is what lets a wildly
different third resolver appear without a single platform change. It is the
"center stays still" principle from Core, re-expressed for autonomous work.

## What this document covers

- **Architecture map** — the whole platform stack, and one example integration: a
  GitHub-driven triage → implement → review loop.
- **Design philosophy** — the bright line between platform and resolver, why
  isolation is non-negotiable, and why observability is a *contract* not a
  convenience.
- **The instance lifecycle** — eight statuses, four phases, cleanup that always
  runs.
- **The resolver protocol** — the twelve-member contract every resolver fulfills.
- **Isolation & containers** — the sealed workshop and the filesystem bus that
  coordinates it.
- **The event vocabulary** — the eight events that make a run legible, and the
  one invariant that, if broken, hangs the platform.
- **A2UI & interaction** — the three ways a resolver and a human talk.
- **The session engine** — the SDK beneath every resolver: prepare-once, dispatch
  disposable sessions, review adversarially, gate on real build/test results.
- **Three resolvers** — three theories of how an AI agent should be governed.
- **Viewports & the SPA** — how a resolver ships its own UI without the shell ever
  knowing its domain.
- **Provisioning & the inner loop** — how you actually develop and validate a
  change against a real running stack.
- **The complete picture** — six layers, the roadmap, and where new things go.

By the end, every box in the architecture map will be familiar, and you will know
not just *what* each piece does but *why it was allowed to exist*.
