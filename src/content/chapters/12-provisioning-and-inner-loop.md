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

<!-- diagram:dtu-topology -->
<figure class="diagram">
<svg xmlns="http://www.w3.org/2000/svg" class="rdiagram" width="584" height="275" viewBox="-10 -10 584 275" preserveAspectRatio="xMidYMid meet" role="img">
<defs><filter id="nshadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="1.6" stdDeviation="2.6" flood-color="#2a2622" flood-opacity="0.16"/></filter><marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse"><path d="M0,0.6 L9,5 L0,9.4 L2.4,5 Z" fill="#6b6359"/></marker></defs>
<path d="M 252.9 41.1 C 240.1 46.8 226.2 53.0 213.5 59.0 C 194.5 67.9 174.0 78.0 155.4 87.4" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="213.5" y="61.2" width="49.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="238.0" y="73.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">sibling</text>
<path d="M 286.2 41.2 C 277.3 55.4 265.3 74.6 255.4 90.4" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="273.5" y="61.2" width="49.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="298.0" y="73.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">sibling</text>
<path d="M 313.8 41.0 C 318.1 46.7 322.6 53.0 326.5 59.0 C 333.1 69.1 339.7 80.4 345.4 90.6" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="335.5" y="61.2" width="49.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="360.0" y="73.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">sibling</text>
<path d="M 348.4 41.2 C 361.6 46.7 375.7 52.8 388.5 59.0 C 410.9 69.8 435.3 83.1 455.3 94.4" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="416.5" y="61.2" width="49.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="441.0" y="73.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">sibling</text>
<path d="M 93.5 148.0 C 93.5 160.3 93.5 175.0 93.5 188.4" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="100.0" y="168.2" width="91.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="145.5" y="180.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">hosts (Docker)</text>
<g filter="url(#nshadow)">
<rect x="232.5" y="0.0" width="132.0" height="41.0" rx="14.0" fill="#e9e7e0" stroke="#9b9484" stroke-width="1.5"/>
</g>
<text x="298.5" y="24.4" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#5d564a">Incus bridge</text>
<g filter="url(#nshadow)">
<rect x="20.5" y="92.0" width="146.0" height="56.0" rx="14.0" fill="#f6e7d0" stroke="#b07a3f" stroke-width="1.5"/>
</g>
<text x="93.5" y="115.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#8a5a2b">DTU</text>
<text x="93.5" y="132.2" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="11.5" font-weight="500" fill="#6b6359">(resolve stack)</text>
<g filter="url(#nshadow)">
<rect x="185.0" y="99.5" width="105.0" height="41.0" rx="14.0" fill="#f1ead8" stroke="#b89a63" stroke-width="1.5"/>
</g>
<text x="237.5" y="123.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#6f5a2e">worker-1</text>
<g filter="url(#nshadow)">
<rect x="308.0" y="99.5" width="105.0" height="41.0" rx="14.0" fill="#f1ead8" stroke="#b89a63" stroke-width="1.5"/>
</g>
<text x="360.5" y="123.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#6f5a2e">worker-2</text>
<g filter="url(#nshadow)">
<rect x="431.0" y="99.5" width="133.0" height="41.0" rx="14.0" fill="#f1ead8" stroke="#b89a63" stroke-width="1.5"/>
</g>
<text x="497.5" y="123.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#6f5a2e">reality-check</text>
<g filter="url(#nshadow)">
<rect x="0.0" y="199.0" width="187.0" height="56.0" rx="14.0" fill="#efe9dc" stroke="#a99c80" stroke-width="1.5"/>
</g>
<text x="93.5" y="222.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#7a6f55">resolve-{id}-gitea</text>
<text x="93.5" y="239.2" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="11.5" font-weight="500" fill="#6b6359">(Docker, inside DTU)</text>
</svg>
<figcaption>DTU topology: workers and reality-check are Incus siblings of the DTU; the Gitea sidecar is a Docker container that lives inside it.</figcaption>
<details class="diagram-text"><summary>Text version</summary><pre class="diagram-ascii">                             ┌──────────────────────┐
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
                             └──────────────────────┘</pre></details>
</figure>
<!-- /diagram:dtu-topology -->

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
