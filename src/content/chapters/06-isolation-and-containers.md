---
title: "Isolation & The Container Model"
chapter: 6
---

# Section 6: Isolation & The Container Model

A resolver is code the platform did not write, driving a model that does
unpredictable things, often against real repositories with real credentials. The
only safe place to run that is a sealed box. The container *is* the isolation
boundary, and the filesystem inside it *is* the coordination bus. This section is
about both.

## 6.1 Incus primary, Docker fallback

Worker containers run on **Incus** (the primary runtime) or **Docker** (the
fallback), chosen at runtime by `detect_runtime()`. The `ContainerProvider`
abstraction (`containers/provider.py` as the Protocol, `incus.py` and
`docker_provider.py` as implementations) hides the difference: the orchestrator
asks for "a container" and gets one, regardless of which engine is present.

**Design Decision — The runtime is an abstraction with a detected default, not a
hard dependency.**
Incus gives system-container semantics that suit long-lived, repo-cloning,
sub-spawning workloads; Docker is the universally available fallback. Coding to a
`ContainerProvider` Protocol means a new runtime is a new implementation, not a
platform rewrite — the same structural-contract move the rest of the platform uses
(§5). One permanent exception: Gitea sidecars always use Docker (§12).

## 6.2 Container naming

Names are a coordination protocol, not cosmetics:

| Container | Purpose |
|---|---|
| `resolve-{id}` | The main resolver container for instance `{id}`. |
| `resolve-{id}-gitea` | The per-instance Gitea sidecar for workspace git hosting. |
| `resolve-{id}-env-{uuid}` | An ephemeral sub-container for a sandboxed step or worker. |

The naming scheme is what lets the watchdog, the lifecycle sweep, and the
orchestrator find and reason about every container belonging to an instance without
a side database. The name encodes the relationship.

## 6.3 The `.resolve/` filesystem as the coordination bus

Inside every worker container:

```
/project/
├── .resolve/                       # platform-managed coordination directory
│   ├── config.json                 # InstanceConfig, written by the host
│   ├── events.jsonl                # append-only event log (emitter writes)
│   ├── state.json                  # atomic state snapshot (emitter writes)
│   ├── status.json                 # resolver-reported status checkpoint
│   ├── input-requests/
│   │   ├── {request_id}.json          # A2UI schema + metadata (emitter writes)
│   │   └── {request_id}.response.json # response payload (host writes)
│   ├── messages/
│   │   └── 001.json, 002.json, …      # numbered, host writes
│   └── data/                       # on-demand data bus (resolver writes, host serves)
└── workspace/
    └── {repo-name}/                # cloned repos
```

The directory is a **two-writer mailbox** with a strict ownership split:

- **Host writes:** `config.json`, response files into `input-requests/`, numbered
  files into `messages/`.
- **Resolver (emitter) writes:** `events.jsonl`, `state.json`, `status.json`,
  input-request schema files, and anything under `data/`.
- **Host reads** what the resolver writes (the monitor loop, §4.3). **Resolver
  reads** what the host writes (responses, messages).

**Design Decision — The coordination medium is the filesystem, not a socket or a
queue.**
A file-based bus is inspectable (`tail -f events.jsonl`), append-only where it
matters, atomic where it must be (§7.4), and it survives a daemon restart with no
reconnection logic. The platform observes a run by reading files a process happens to
be writing — the same "observe from outside" stance as Core's session files. The
cost is single-writer discipline per file, which the ownership split above enforces.

## 6.4 Container safety — defense in depth

This is not theoretical. A real incident — **4,269 runaway `pytest` processes
consuming 103 GiB of RAM**, triggering OOM kills — produced the current
three-layer defense. No single layer is trusted to be sufficient.

**Layer 1 — Kernel-enforced resource limits.** Set at container creation:

| Flag | Value | Purpose |
|---|---|---|
| `--pids-limit` | `256` | hard cap on process count |
| `--memory` / `--memory-swap` | `8g` / `8g` | hard memory limit, no swap |
| `--cpus` | `2.0` | CPU quota |
| `--init` | — | Tini init for zombie reaping |

These are the last line of defense. Even if everything above fails, the kernel
contains the blast.

**Layer 2 — The process-guardian hook.** The `hooks-process-guard` module (from
amplifier-foundation) runs at the application layer inside the container. It hooks
`tool:pre` and can: block new tool execution above a process threshold (128), warn
above 64, kill orphaned `pytest` / `node.*test` processes before each exec, and
detect runaway loops (the same command 5+ times in 60 seconds). It is a hook, not a
tool — the model cannot see it, forget it, or decline to use it. This is Core's
"code quality as a hook, not an if-statement" pattern applied to safety.

**Layer 3 — The periodic watchdog.** The orchestrator's `watchdog_loop` runs
continuously and monitors PID count (warns at 200, kernel kills at 256), memory
(warns at 80% of 8 GiB), and instance lifetime (a 12-hour hard maximum,
`MAX_INSTANCE_LIFETIME_SECONDS`).

**Design Decision — Three independent layers, each catching a different failure
mode.**
The guardian stops most fork bombs before they reach the kernel limit (128 < 256).
The watchdog catches slow-burn exhaustion that happens *between* tool calls, where
the guardian is not watching. The kernel limit catches anything that slips past both.
Redundancy here is not waste — it is the design. Containment is the one property the
platform may never compromise (§3.3), so it is defended in depth.

## 6.5 Startup paths

Provisioning offers two paths, traded off against latency:

- **Cached fast path** (`amplifier-cache:python`, ~15s) — pre-baked dependencies.
- **Cold path** (`uv:python3.13-trixie-slim`, ~5min) — full install of apt
  packages, CLI tools, provider SDKs, pipeline engine modules, git identity/auth,
  repo clone, and bundle activation.

`AMPLIFIER_SETUP_COMMANDS` is selected at runtime based on image availability. The
cached path is the common case; the cold path is the guarantee that a fresh
environment can always bootstrap from nothing.

With the box sealed and the bus laid down, §7 covers the messages that flow across
it — the event vocabulary that makes a run legible.
