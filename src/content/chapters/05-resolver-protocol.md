---
title: "The Resolver Protocol"
chapter: 5
---

# Section 5: The Resolver Protocol

A resolver is whatever satisfies the resolver contract. Like Core's modules, the
contract is *structural*: implement the right members with the right signatures and
you are a resolver. No base class to inherit, no registry to declare yourself in
beyond a one-line install (§5.4). The contract lives in
`amplifier-resolve/src/amplifier_resolve/core/resolver.py` as a `Protocol`.

## 5.1 Twelve members

The protocol has **12 members: 4 properties and 8 methods.** That is the entire
surface a resolver must present to the platform.

```python
class Resolver(Protocol):
    # --- Properties (4) ---
    name: str             # unique id, e.g. "dot-graph"; matches manifest.json.name
    version: str          # e.g. "0.1.0"; matches manifest.json.version
    description: str      # human-readable, shown in the resolver listing
    supports_resume: bool # True if a paused run can be resumed (§4.5)

    # --- Methods (8) ---
    def instantiation_schema(self, params=None) -> dict: ...
    def workspace_spec(self, params, available_credentials=None) -> WorkspaceSpec: ...
    def container_setup(self, params) -> ContainerSetup: ...
    def message_types(self, instance_state) -> list[dict]: ...

    async def run(self, config, session_factory, emitter, *, resume=False) -> ResolverResult: ...
    async def on_input_response(self, config, request_id, payload) -> None: ...
    async def on_message(self, config, message_type, payload) -> None: ...
    async def stop(self, reason) -> None: ...
```

Read the methods as answers to a sequence of platform questions:

| Method | The platform is asking… | When |
|---|---|---|
| `instantiation_schema(params)` | "What do I need to ask the user to create an instance?" | before the instance exists |
| `workspace_spec(params, creds)` | "What repos do I clone, and how do I set up git?" | during provisioning |
| `container_setup(params)` | "What extra setup, mounts, and bundles does the container need?" | during provisioning |
| `run(config, session_factory, emitter, resume)` | "Do the work." | execute phase |
| `message_types(instance_state)` | "What unsolicited messages will you accept right now?" | anytime after creation |
| `on_input_response(config, rid, payload)` | "The user answered your input-request." | during execution |
| `on_message(config, type, payload)` | "The user sent you a message." | during execution |
| `stop(reason)` | "Wind down gracefully." | on graceful-stop request |

The single most important method is `run()`. It receives three things and that
triad is the resolver's entire world:

- **`config: InstanceConfig`** — the per-instance data: `instance_id`, `params`,
  `work_dir`, bundles. The serialized form of this is the `config.json` the platform
  wrote into the container.
- **`session_factory: SessionFactory`** — the engine for minting Amplifier sessions
  cheaply (§9). This is how a resolver actually runs an LLM.
- **`emitter: EventEmitter`** — the channel for events, state snapshots, and
  input-requests (§7, §8).

**Design Decision — A resolver is structural, not nominal.**
Anything with these twelve members *is* a resolver. There is no `BaseResolver` to
subclass and no inheritance chain to fight. Small, stable contracts beat base
classes that accumulate baggage — and a structural contract means a resolver can be
written in any style, by anyone, as long as it presents the right shape. This is the
exact inheritance-free philosophy Core uses for its six module types, applied to the
one module type Resolve adds.

## 5.2 `ResolverResult` — and the move to event-driven completion

Historically, `run()` returned a `ResolverResult`:

```python
@dataclass
class ResolverResult:
    status: Literal["completed", "paused", "failed"]
    output: str | None = None
    error: str | None = None
    sessions_used: int = 0
```

This is the model the committed `ARCHITECTURE.md` still documents. **The running
code has moved ahead of it.** The in-process `ResolveCore` engine has been retired;
resolvers now run as worker processes that signal terminal state through the *event
vocabulary* and SDK calls (`self.complete()` / `self.fail()`), not a return value
(§7, §9). The conceptual contract is unchanged — *a run reaches one of completed /
paused / failed* — but the **mechanism** of reporting it is now the
`resolver:completed` event, reconciled by the platform as in §4.4.

> **Flagged divergence.** When a design doc and the code disagree, the code wins.
> `ARCHITECTURE.md`'s `ResolveCore` description predates the containerized worker
> model. Treat the *event vocabulary* (§7) as the authoritative completion contract.

## 5.3 Platform owns / resolver owns

The protocol is the bright line (§3) made into an interface. Here is the full split.

**The platform owns:** instance lifecycle and status; the resolver registry; A2UI
*structural* validation; input-request tracking and routing; the session factory as
infrastructure; container orchestration, volumes, and credential forwarding; event
mirroring, SSE, state snapshots; delivering responses and messages to the right
container.

**The resolver owns:** all semantic inputs (what to ask, what it means, how to use
it); repo access decisions (whether, how many, which provider, what credentials);
the instantiation schema; input-request forms and *when* to ask; the message
catalog; status/state semantics and vocabulary; blocking behavior (wait, continue,
or time out).

> **The bright line, stated once more:** the platform validates *structure* (are the
> required fields present, do the check rules pass). The platform never interprets
> *meaning* (what "spec" means, whether a repo URL is valid for this task, whether
> the user's steering input makes sense).

## 5.4 Validation-as-registration

A resolver is installed as a separate Python package and registered via
`amplifier-resolve resolver add`. Registration *is* validation: the catalog at
`~/.amplifier/resolve/resolvers.json` is the single source of truth, and a resolver
that does not satisfy the contract does not register. `GET /resolvers` lists what is
registered; `GET /resolvers/{name}/schema?params=…` returns the dynamic
instantiation schema for progressive discovery.

**Design Decision — Registration is validation; the catalog is the only source of
truth.**
There is no implicit discovery that might surface a half-built resolver, and no way
for the catalog and reality to drift — if it is in the catalog, it validated. The
platform reads one file and trusts it, which keeps resolver discovery boringly
deterministic. With the contract clear, §6 shows where a resolver actually *lives*
when it runs: the sealed container.
