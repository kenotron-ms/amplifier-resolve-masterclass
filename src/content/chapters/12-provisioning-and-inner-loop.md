---
title: "Provisioning & The Inner Loop"
chapter: 12
---

# Section 12: Provisioning & The Inner Loop

Everything so far describes the platform *running*. This section is about *changing*
it — the development and validation loop. It is the part new maintainers most often
get wrong, because the topology is subtle and the failure modes are silent. Master it
and you can prove a change actually works; miss it and your tests pass while the
platform breaks.

## 12.1 The DTU — a Digital Twin Universe

The `amplifier-bundle-resolve` repo stands up the whole stack — backend, resolvers,
viewports — inside a canonical **DTU (Dev Test Unit)**: an Incus container provisioned
from the `resolve-stack.yaml` profile. The DTU is a faithful twin of production in a
box.

The critical topology fact: **workers and reality-check sub-instances are pure Incus
*siblings* of the DTU on the same bridge — not nested inside it.** The DTU is not a
parent container that workers live within; it is a peer. This single fact explains
almost every provisioning pitfall below.

```
                             ┌──────────────────────┐
                             │       worker-2       │
                             └──────────────────────┘
                               ▲
                               │ sibling
                               │
┌───────────────┐  sibling   ┌──────────────────────┐  sibling   ┌──────────┐
│ reality-check │ ◀───────── │     Incus bridge     │ ─────────▶ │ worker-1 │
└───────────────┘            └──────────────────────┘            └──────────┘
                               │
                               │ sibling
                               ▼
                             ┌──────────────────────┐
                             │         DTU          │
                             │   (resolve stack)    │
                             └──────────────────────┘
                               │
                               │ hosts (Docker)
                               ▼
                             ┌──────────────────────┐
                             │  resolve-{id}-gitea  │
                             │ (Docker, inside DTU) │
                             └──────────────────────┘
```

## 12.2 `DEV_RESOLVERS` — the one-time snapshot

Normally a resolver installs from upstream `main`. To test *local* changes,
`DEV_RESOLVERS` mirrors the developer's **working tree** (uncommitted files included)
into a per-DTU Gitea sidecar at stack launch (`dr_create_repo` + `dr_push_working_tree`,
which force-pushes the staged tree to Gitea `main`).

**The trap:** this push is a **one-time snapshot at launch**. Files written or edited
*after* launch — including by an agent's own `modular-builder` mid-session — are **not**
in Gitea. Workers spawned later still install the at-launch state. To exercise a
post-launch change you must manually re-push or re-launch the stack.

**Design Decision — `DEV_RESOLVERS` snapshots the working tree once, at launch.**
Mirroring continuously would mean every keystroke re-pushes to every worker's source of
truth mid-run — nondeterministic and unsafe. A single snapshot makes each stack launch a
reproducible point-in-time. The cost is a discipline: *change, then re-launch (or
re-push)* — never assume a live edit reached the workers.

## 12.3 The Gitea sidecar — `DTU_INCUS_IP`, not `HOST_GW`

Gitea is a per-instance **Docker sidecar living *inside* the DTU**, managed via the
`amplifier-gitea` CLI (never inline `docker run` — that regressed with a root-refusal
bug the CLI handles). Because workers are Incus *siblings* (§12.1), they must reach
Gitea at the **DTU's Incus bridge IP (`DTU_INCUS_IP`)**, captured post-launch via
`incus list`. Using `HOST_GW:GITEA_PORT` from a worker hits the *host's* network stack,
not the DTU's Docker container. `resolve-stack.sh` rewrites resolver manifest URLs to
`http://${DTU_INCUS_IP}:${GITEA_PORT}/admin/<repo>@main`.

**Design Decision — The Gitea sidecar lives in the DTU's Docker and is addressed by the
DTU's bridge IP.**
Workers are siblings of the DTU, so "localhost" and "the host gateway" both point at the
wrong machine. Addressing Gitea by `DTU_INCUS_IP` is the only address that resolves from
a sibling worker into the DTU's Docker. Moving Gitea to the host, or addressing it by
`HOST_GW`, breaks worker clones in ways that pass on the developer's machine and fail in
the DTU — the worst kind of bug.

## 12.4 `dev_source_overrides` — the activation guard

Mirroring local code into Gitea does nothing unless a resolver opts in. Its
`manifest.json` `setup_commands` must include `dev_source_overrides: ["sdk",
"<resolver>"]`. Without it, **DTU runs silently use upstream `main`** — your behavioral
change is never exercised, and DTU validation proves nothing.

**Design Decision — Local source is used only when the manifest explicitly opts in.**
A run should never *accidentally* pick up local code, and it should never *silently*
ignore it. An explicit `dev_source_overrides` makes the choice visible in the manifest:
present means "test my tree," absent means "use upstream." The failure of forgetting it
is loud once you know to look — a validation that proves nothing — which is why it is on
the pitfall list.

## 12.5 Worker bind-mounts are host paths

Worker containers (Incus siblings) **do not inherit the DTU's bind-mounts**. A worker's
bind-mount *source* must be a **HOST path**, translated via
`AMPLIFIER_WORKER_HOST_INSTANCES_DIR` (`containers/paths.py:to_host()`) — not a
DTU-internal path. "The DTU sees the file" does **not** imply "the worker sees it." The
default resolves into the host's Incus storage pool for the DTU's rootfs.

**Design Decision — Worker bind-mount sources are translated to host paths.**
Because workers are the host's containers (siblings), the only filesystem coordinate
they share with the DTU is the host's. Translating sources to host paths is what makes a
file the DTU wrote actually visible to a worker. Skip the translation and the worker
mounts a path that exists only inside the DTU — an empty mount, silently.

## 12.6 The merge-gate rule

The recurring theme: **unit tests pass while integration boundaries break.** Every one
of the pitfalls above is invisible to unit tests and visible only in a real DTU run.
Hence the gate.

For `amplifier-bundle-resolve`, `scripts/smoke-test-dev-resolvers.sh` is required for any
change to `scripts/`, `scripts/lib/`, or `resolve-stack.yaml`. It is an *executable
specification*: it launches a throwaway DTU, runs `DEV_RESOLVERS` end-to-end, verifies
Gitea starts **non-root**, confirms the working tree reached Gitea and the manifest was
mutated, then destroys the DTU.

Across the platform, each repo defines its own **verification gradient** — heavier
verification for heavier risk:

| Repo | Core logic | Scripts / tools | Tests / docs |
|---|---|---|---|
| `amplifier-resolve` | unit + full DTU run to completion | unit + curl smoke | unit |
| `amplifier-resolver-*` | unit + DTU run (full 4-event chain) | unit + DTU | unit |
| `amplifier-bundle-resolve` | unit + smoke gate on a real DTU | unit + smoke | unit |
| `amplifier-app-resolve` | `npm test` + manual viewport verification | — | `npm test` |

**Design Decision — Validation must *observe the new behavior*, not merely show tests
pass.**
"Tests are green" answers "did I break the units?" It does not answer "does the change
do the thing?" The merge gate requires a run that *exercises* the changed path — a DTU
to completion, a smoke test that watches the working tree reach Gitea. Because the
expensive bugs live at integration boundaries that unit tests cannot see, the gate is
placed exactly there.

With the inner loop understood, §13 assembles the whole platform and looks at where it
is headed.
