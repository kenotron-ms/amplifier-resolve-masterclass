---
title: "Architecture Map"
chapter: 2
---

# Section 2: Architecture Map

## A map of the territory before we walk it

This section is the city map. You do not need every building yet — you need the
neighborhoods and the roads between them. Every box here gets its own section
later.

<!-- diagram:architecture-map -->
<figure class="diagram">
<svg xmlns="http://www.w3.org/2000/svg" class="rdiagram" width="798" height="382" viewBox="-10 -10 798 382" preserveAspectRatio="xMidYMid meet" role="img">
<defs><filter id="nshadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="1.6" stdDeviation="2.6" flood-color="#2a2622" flood-opacity="0.16"/></filter><marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse"><path d="M0,0.6 L9,5 L0,9.4 L2.4,5 Z" fill="#6b6359"/></marker></defs>
<path d="M 80.4 48.6 C 88.3 62.2 100.7 79.4 116.5 89.0 C 139.3 102.9 196.0 113.6 249.9 121.1" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="126.5" y="76.2" width="97.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="175.0" y="88.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">POST /instances</text>
<path d="M 233.6 48.6 C 233.4 61.4 235.3 77.8 244.5 89.0 C 248.1 93.4 252.2 97.4 256.6 101.0" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="254.5" y="76.2" width="97.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="303.0" y="88.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">POST /instances</text>
<path d="M 363.0 48.8 C 364.0 62.2 365.4 80.4 366.6 96.6" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 451.2 56.0 C 437.3 69.3 420.4 85.4 405.6 99.5" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 426.9 163.0 C 457.8 177.6 495.5 195.4 525.4 209.4" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="500.0" y="183.2" width="103.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="551.5" y="195.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">launch container</text>
<path d="M 313.2 163.0 C 282.9 177.6 245.9 195.4 216.6 209.4" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 371.2 163.2 C 371.9 175.8 372.9 190.8 373.7 203.7" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 505.7 255.1 C 452.6 269.8 379.2 290.1 320.8 306.3" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="435.5" y="275.2" width="91.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="481.0" y="287.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">events / state</text>
<path d="M 178.2 255.2 C 185.3 267.2 194.6 282.8 203.0 296.9" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 344.9 255.2 C 324.9 268.2 298.3 285.4 275.1 300.3" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 138.2 312.5 C 108.4 300.8 78.0 282.7 60.5 255.0 C 22.0 194.0 43.9 104.3 59.3 58.4" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="45.0" y="183.2" width="61.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="75.5" y="195.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">loaded by</text>
<path d="M 593.7 56.0 C 551.9 70.6 500.2 88.6 456.9 103.6" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" stroke-dasharray="6 5" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="543.0" y="76.2" width="61.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="573.5" y="88.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">stands up</text>
<g filter="url(#nshadow)">
<rect x="0.0" y="7.5" width="141.0" height="41.0" rx="14.0" fill="#eaf1f4" stroke="#3f7d99" stroke-width="1.5"/>
</g>
<text x="70.5" y="31.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#1f5673">SPA (browser)</text>
<g filter="url(#nshadow)">
<rect x="167.0" y="7.5" width="137.0" height="41.0" rx="14.0" fill="#eaf1f4" stroke="#3f7d99" stroke-width="1.5"/>
</g>
<text x="235.5" y="31.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#1f5673">agent / script</text>
<g filter="url(#nshadow)">
<rect x="328.5" y="7.5" width="66.0" height="41.0" rx="14.0" fill="#eaf1f4" stroke="#3f7d99" stroke-width="1.5"/>
</g>
<text x="361.5" y="31.9" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#1f5673">CLI</text>
<g filter="url(#nshadow)">
<rect x="412.5" y="-0.0" width="134.0" height="56.0" rx="14.0" fill="#eaf1f4" stroke="#3f7d99" stroke-width="1.5"/>
</g>
<text x="479.5" y="23.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#1f5673">CI bridge</text>
<text x="479.5" y="40.2" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="11.5" font-weight="500" fill="#6b6359">(e.g. GitHub)</text>
<g filter="url(#nshadow)">
<rect x="260.0" y="107.0" width="219.0" height="56.0" rx="14.0" fill="#f6e7d0" stroke="#b07a3f" stroke-width="1.5"/>
</g>
<text x="369.5" y="130.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#8a5a2b">amplifier-resolve</text>
<text x="369.5" y="147.2" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="11.5" font-weight="500" fill="#6b6359">FastAPI platform daemon</text>
<g filter="url(#nshadow)">
<rect x="488.0" y="214.0" width="177.0" height="41.0" rx="14.0" fill="#f1ead8" stroke="#b89a63" stroke-width="1.5"/>
</g>
<text x="576.5" y="238.4" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#6f5a2e">resolver: dot-graph</text>
<g filter="url(#nshadow)">
<rect x="70.0" y="214.0" width="193.0" height="41.0" rx="14.0" fill="#f1ead8" stroke="#b89a63" stroke-width="1.5"/>
</g>
<text x="166.5" y="238.4" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#6f5a2e">resolver: orchestrator</text>
<g filter="url(#nshadow)">
<rect x="281.0" y="214.0" width="189.0" height="41.0" rx="14.0" fill="#f1ead8" stroke="#b89a63" stroke-width="1.5"/>
</g>
<text x="375.5" y="238.4" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#6f5a2e">resolver: understudy</text>
<g filter="url(#nshadow)">
<rect x="138.5" y="306.0" width="172.0" height="56.0" rx="14.0" fill="#eaf0e6" stroke="#7e9266" stroke-width="1.5"/>
</g>
<text x="224.5" y="329.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#566b3f">resolver viewports</text>
<text x="224.5" y="346.2" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="11.5" font-weight="500" fill="#6b6359">(viewport.js)</text>
<g filter="url(#nshadow)">
<rect x="565.0" y="-0.0" width="213.0" height="56.0" rx="14.0" fill="#efe9dc" stroke="#a99c80" stroke-width="1.5"/>
</g>
<text x="671.5" y="23.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#7a6f55">amplifier-bundle-resolve</text>
<text x="671.5" y="40.2" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="11.5" font-weight="500" fill="#6b6359">provisioning / DTU</text>
</svg>
<figcaption>The Resolve platform, end to end. Any consumer reaches the daemon the same way (POST /instances); the daemon launches one isolated resolver container per instance.</figcaption>
<details class="diagram-text"><summary>Text version</summary><pre class="diagram-ascii">                                      ┌─────────────────────┐                    ┌──────────────────────────┐
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
                                      └─────────────────────┘</pre></details>
</figure>
<!-- /diagram:architecture-map -->

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

<!-- diagram:three-concern -->
<figure class="diagram">
<svg xmlns="http://www.w3.org/2000/svg" class="rdiagram" width="209" height="601" viewBox="-10 -10 209 601" preserveAspectRatio="xMidYMid meet" role="img">
<defs><filter id="nshadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="1.6" stdDeviation="2.6" flood-color="#2a2622" flood-opacity="0.16"/></filter><marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse"><path d="M0,0.6 L9,5 L0,9.4 L2.4,5 Z" fill="#6b6359"/></marker></defs>
<path d="M 94.5 41.0 C 94.5 52.9 94.5 68.2 94.5 81.5" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="95.5" y="61.2" width="55.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="123.0" y="73.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">1 triage</text>
<path d="M 94.5 133.3 C 94.5 141.2 94.5 150.6 94.5 159.7" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 94.5 226.0 C 94.5 238.3 94.5 253.0 94.5 266.4" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="103.5" y="246.2" width="73.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="140.0" y="258.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">2 implement</text>
<path d="M 94.5 333.3 C 94.5 341.8 94.5 351.1 94.5 359.8" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<path d="M 94.5 411.0 C 94.5 422.9 94.5 438.2 94.5 451.5" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<rect x="98.0" y="431.2" width="55.0" height="16" rx="8" fill="#f7f3e9" stroke="#d9cfb8" stroke-width="1"/>
<text x="125.5" y="443.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="10.5" fill="#6b6359">3 review</text>
<path d="M 94.5 503.1 C 94.5 511.2 94.5 520.9 94.5 529.9" fill="none" stroke="#6b6359" stroke-width="1.6" stroke-linecap="round" marker-end="url(#arrow)" opacity="0.85"/>
<g filter="url(#nshadow)">
<rect x="26.0" y="0.0" width="137.0" height="41.0" rx="14.0" fill="#eaf1f4" stroke="#3f7d99" stroke-width="1.5"/>
</g>
<text x="94.5" y="24.4" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#1f5673">issue.opened</text>
<g filter="url(#nshadow)">
<rect x="22.5" y="92.0" width="144.0" height="41.0" rx="14.0" fill="#f1ead8" stroke="#b89a63" stroke-width="1.5"/>
</g>
<text x="94.5" y="116.4" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#6f5a2e">triage pipeline</text>
<g filter="url(#nshadow)">
<rect x="13.5" y="170.0" width="162.0" height="56.0" rx="14.0" fill="#f6e7d0" stroke="#b07a3f" stroke-width="1.5"/>
</g>
<text x="94.5" y="193.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#8a5a2b">/resolve</text>
<text x="94.5" y="210.2" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="11.5" font-weight="500" fill="#6b6359">new_instance(...)</text>
<g filter="url(#nshadow)">
<rect x="9.5" y="277.0" width="170.0" height="56.0" rx="14.0" fill="#f6e7d0" stroke="#b07a3f" stroke-width="1.5"/>
</g>
<text x="94.5" y="300.7" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#8a5a2b">Resolve API</text>
<text x="94.5" y="317.2" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="11.5" font-weight="500" fill="#6b6359">resolver container</text>
<g filter="url(#nshadow)">
<rect x="35.0" y="370.0" width="119.0" height="41.0" rx="14.0" fill="#e7efe2" stroke="#7fa06a" stroke-width="1.5"/>
</g>
<text x="94.5" y="394.4" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#4f6f3c">PR created</text>
<g filter="url(#nshadow)">
<rect x="20.0" y="462.0" width="149.0" height="41.0" rx="14.0" fill="#f1ead8" stroke="#b89a63" stroke-width="1.5"/>
</g>
<text x="94.5" y="486.4" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#6f5a2e">review pipeline</text>
<g filter="url(#nshadow)">
<rect x="0.0" y="540.0" width="189.0" height="41.0" rx="14.0" fill="#eaf1f4" stroke="#3f7d99" stroke-width="1.5"/>
</g>
<text x="94.5" y="564.4" text-anchor="middle" font-family="'Inter','Helvetica Neue',Arial,sans-serif" font-size="14.0" font-weight="700" fill="#1f5673">PR review comments</text>
</svg>
<figcaption>A worked example: the GitHub-driven triage → implement → review loop. One integration of the event-driven consumer pattern — not the architecture.</figcaption>
<details class="diagram-text"><summary>Text version</summary><pre class="diagram-ascii">┌────────────────────┐
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
└────────────────────┘</pre></details>
</figure>
<!-- /diagram:three-concern -->

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
