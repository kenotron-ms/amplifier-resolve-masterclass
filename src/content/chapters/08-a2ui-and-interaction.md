---
title: "A2UI & The Interaction Surfaces"
chapter: 8
---

# Section 8: A2UI & The Interaction Surfaces

Events make a run observable (§7). But autonomous work is not fire-and-forget — a
resolver needs to *ask* the user things, and the user needs to *steer*. The
question is how to let a resolver define rich, dynamic interactions without the
platform understanding any of them. The answer is **A2UI**.

## 8.1 A2UI: a wire format the platform never interprets

A2UI (v0.9) is the external wire format for every interaction schema in the
platform. A resolver describes a form, a table, a status surface, or a decision as
an A2UI component tree. Consumer UIs render that tree as native forms; agent
consumers interpret it programmatically. The platform's only job is to validate
that an *incoming payload* satisfies the resolver's declared A2UI **check rules** —
never to interpret what the form means.

**Design Decision — A2UI is validated structurally and never interpreted
semantically.**
The platform confirms required fields are present and check rules pass, then routes
the payload to the resolver. It does not know that a field is a repo URL, a branch
name, or an approval decision. This is the bright line (§3) expressed as a protocol:
the resolver owns meaning, the platform owns structure. It is also what lets a
resolver invent an entirely new interaction — a multi-panel review gate, a decision
override — without the platform changing.

## 8.2 The three interaction surfaces

There are exactly three ways a resolver and a consumer exchange structured
information, distinguished by *when* they happen and *who* initiates.

| Surface | When | Who initiates | A2UI source |
|---|---|---|---|
| **Instantiation** | before the instance exists | consumer | `resolver.instantiation_schema(params)` |
| **Input Requests** | during execution | resolver | `emitter.request_input(schema=…)` |
| **Messages** | anytime after creation | consumer | `resolver.message_types(instance_state)` |

**1. Instantiation — "what do I need to start?"** The consumer asks
`GET /resolvers/{name}/schema?params=…`; the resolver returns an A2UI surface.
`params` enables *progressive discovery* — the schema can change based on partial
input (e.g. once you pick a pipeline, the form reveals that pipeline's fields). The
filled form becomes the `input` of `POST /instances`, validated *before any
container exists* (§4.2).

**2. Input Requests — "I need an answer to continue."** Mid-run, the resolver calls
`request_input(request_id, prompt, schema)`. The SDK writes the A2UI schema to
`.resolve/input-requests/{rid}.json`, the platform emits `resolve.input.requested`
(and the SDK auto-emits `resolver:input_requested`, §7), and the instance typically
moves to `awaiting_input` (§4). The consumer fetches pending requests, submits a
response, the platform validates it against the A2UI checks, writes
`{rid}.response.json`, and calls `resolver.on_input_response()`.

**3. Messages — "I want to steer."** Unsolicited, consumer-initiated. The consumer
asks `GET /instances/{id}/message-types`; the resolver returns the catalog *for the
current state* via `message_types(instance_state)` — so what you can say depends on
where the run is. The consumer posts `{message_type, payload}`; the platform
validates and calls `resolver.on_message()`.

**Design Decision — Interaction is split by initiator and timing into exactly three
surfaces.**
Instantiation is consumer-first and pre-instance. Input-requests are resolver-first
and mid-run. Messages are consumer-first and any-time. Collapsing them would blur
*who is waiting on whom* — and that distinction is exactly what the platform must
track to model `awaiting_input` correctly. Three clean surfaces keep the routing
unambiguous.

## 8.3 `request_input` as an awaitable

`request_input()` does more than write a file — it returns a **future**. A resolver
can `await` it to block until the human answers, store it to handle the response
later, or ignore it and keep working. The understudy's `InputRequestInterviewer`
builds the A2UI schema, calls `request_input`, and blocks on the returned future;
its `async_ask` variant awaits natively to avoid a sync/async bridge deadlock.

This is what makes human-in-the-loop *composable*: a gate is just an `await` on a
future that the platform completes when a response file lands. `status.json` and the
`awaiting_input` status are the consumer-facing shadow of that pending future.

**Design Decision — A human gate is an awaitable future, not a special control-flow
mode.**
Modeling "wait for a person" as a future the platform resolves means a resolver
expresses approval gates, clarifying questions, and steering pauses with ordinary
`await`. Blocking behavior — wait, continue, or time out — stays the resolver's
policy (§5.3), while the platform provides only the mechanism that completes the
future.

## 8.4 The on-demand data bus

A2UI handles *structured interaction*. Large or arbitrary artifacts — a rendered
`graph.dot`, a diff, a generated file — use a separate, equally resolver-agnostic
channel: the **data bus**.

```
GET /instances/{instance_id}/data/{path}
```

The endpoint reads from `/project/.resolve/data/{path}` inside the running container
via `container exec`. Any resolver can write there; any consumer can fetch. Path
traversal is blocked (`..` and absolute paths → `400`), content-type is detected
from the extension, missing files return `404`, and an unreachable container returns
`502`. The companion convention is the `data_changed` event: the resolver emits it
with the affected paths so consumers re-fetch *only* what changed.

**Design Decision — Large data is never pushed, never polled — only fetched on
demand.**
Streaming every artifact through the event log would bloat it; polling would waste
both ends. Instead the resolver writes files and emits a tiny `data_changed`
pointer; the consumer pulls exactly the paths it cares about, exactly when they
change. The data bus is resolver-agnostic plumbing — the platform serves bytes from
a directory and never looks inside them. It is the §3 philosophy applied to payload
size: the platform moves data it does not interpret.

Interaction handled, §9 goes beneath the resolver to the engine that actually runs
the models: the SDK.
