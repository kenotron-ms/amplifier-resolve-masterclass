---
title: "Design Philosophy"
chapter: 3
---

# Section 3: Design Philosophy

Three ideas shape Resolve. Like Core's principles, they were not whiteboarded
first — they emerged from the same decision, made over and over: *does this
belong to the platform, or to the resolver?* Every time the answer was "the
resolver," the platform got smaller and more durable.

## 3.1 Mechanism, not policy — one layer up

Amplifier Core's kernel fires events and lets modules decide what happens. Resolve
applies the identical discipline to autonomous work. The platform provides:

- **Lifecycle** — create, track, pause, resume, cancel, destroy an instance.
- **Isolation** — a container per instance, with hard resource limits.
- **Transport** — the filesystem coordination bus, event mirroring, SSE, the data
  bus.
- **Structural validation** — A2UI payloads are checked against the resolver's
  declared rules.

The platform decides *none* of the following:

- What inputs a request needs, or what they mean.
- How many phases the work has, or what they are called.
- What counts as "done," "verified," or "good."
- Which repos to clone, which model to call, how to plan.

Those are policy. Policy lives in the resolver.

**Design Decision — The platform validates structure; it never interprets
meaning.**
This is *the bright line*. The platform confirms the required fields are present
and the check rules pass. It never asks whether a repo URL makes sense for this
task, whether a "spec" is a good spec, or whether a phase name is reasonable.
Weaving meaning into the platform would make every new resolver a platform change.
Holding the line makes the platform a constant and resolvers a free variable.

## 3.2 The center stays still

A new resolver ships. Someone writes a package, registers it, and points a request
at it. The platform does not know or care what strategy it implements. New phases,
new artifact kinds, new interaction forms, new verification regimes: all handled
at the edges. The daemon does not move.

This is why the three in-tree resolvers can be as different as a compiled pipeline,
a live delegation manager, and a contract-governed apprentice (§10) while the
platform code that runs them is identical. The asymmetry is the architecture in one
sentence:

> Resolvers depend on the platform. The platform depends on no resolver.

When a resolver needs something genuinely new from the platform, that is a signal —
and usually it can be expressed as a *capability* the resolver declares and the
platform provisions generically, not as a special case baked into the daemon.

## 3.3 Ruthless isolation

Core's third principle is *ruthless simplicity* (zero file I/O in the kernel).
Resolve's analogue is **ruthless isolation**: nothing a resolver does may escape
its container, and no two instances may touch each other.

This is not abstract. The container-safety design (§6) exists because of a real
incident — 4,269 runaway `pytest` processes consumed 103 GiB of RAM and triggered
OOM kills. The response was three independent, redundant layers of defense, none
trusted to be sufficient alone. Autonomous agents *will* do surprising things;
isolation is what makes "surprising" survivable.

**Design Decision — Every instance runs in its own sealed container, and the
defenses are deliberately redundant.**
Kernel-enforced resource limits, an application-layer process guardian, and a
periodic watchdog each catch a *different* failure mode. A single layer would be a
single point of failure for the one property — containment — that the platform
cannot compromise on.

## 3.4 Observability is a contract, not a convenience

A run you cannot see is a run you cannot trust, resume, or debug. But the platform
cannot interpret a resolver's internals (3.1). The resolution is a small, fixed
**vocabulary** of events that every resolver agrees to emit (§7), riding on the
existing context-intelligence envelope. The platform reads only `resolver:*`
events for cross-resolver views; everything else is the resolver's private
business, available to its own viewport but never interpreted by the platform.

The keystone of that contract is completion:

**Design Decision — A run is complete when it *says* it is complete, with process
exit as a fallback — never a magic string in stdout.**
The platform recognizes completion via the `resolver:completed` event first, the
process exit code second, and a watchdog timeout last. The old approach — grepping
stdout for a magic marker (`__RESOLVE_WORKER_COMPLETE__`) — was removed. A typed,
explicit terminal event is observable, carries structured outcome and error data,
and cannot be accidentally printed by an unrelated log line. The cost is an
invariant resolver authors must honor: *emit it at every exit path, or the platform
assumes the worst* (§7).

## 3.5 Why this matters in practice

Picture adding a brand-new resolution strategy — say, a "pair-programming" resolver
that interleaves two models in debate. In a platform without these principles you
would be editing the daemon: new status semantics, new event types, new UI code,
new validation. Every edit risks the runs that already work.

Under Resolve's principles you write a package that satisfies the protocol (§5),
emit the standard vocabulary (§7), declare your A2UI surfaces (§8), and optionally
ship a viewport (§11). The platform runs it without a single line changing. The
strategy is new; the mechanism is old.

That is the whole game: **keep the mechanism old so the strategies can be new.**
The rest of this masterclass is that sentence, made concrete subsystem by
subsystem.
