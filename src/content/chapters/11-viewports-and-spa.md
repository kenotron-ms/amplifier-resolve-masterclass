---
title: "Viewports & The SPA"
chapter: 11
---

# Section 11: Viewports & The SPA

Three resolvers as different as a compiled pipeline, a delegation manager, and a
governed apprentice (§10) each need a *face* — a UI that shows what *this* resolver
is doing. But the platform must not understand any resolver's domain (§3). The
viewport system resolves this tension: a resolver ships its own UI as a plugin, and
the SPA loads it without ever knowing what it renders.

## 11.1 The SPA is a shell

`amplifier-app-resolve` (React 19 / Vite / TypeScript / Zustand) is a **shell**. It
provides a stable host — navigation, auth, the event stream, the state poll — into
which resolver-authored **viewports** are injected at runtime. The shell knows
exactly one thing about any resolver: the `ViewportProps` contract (§11.3). It knows
nothing about pipelines, workers, or journeys.

## 11.2 Dynamic viewport loading

Each resolver may ship a `viewport.js` ES-module bundle (a single default-exported
React component). The platform serves it at `GET /api/resolvers/{name}/viewport.js`
via Python entry points (`amplifier_resolve.viewports`). The SPA loads it through a
three-step path:

1. **`useViewport(resolverName)`** derives the URL, gated on auth readiness.
2. **`importViewport(url)`** does a `fetch()` *first* (so a missing viewport returns
   `null` quietly instead of a red console error), then dynamically `import()`s the
   module. Results are cached at module scope.
3. **`ViewportHost`** renders a loading skeleton, then the resolved component — or the
   fallback (§11.5). It keys on `resolverName` to force a full unmount/remount when
   switching resolvers, preventing a stale viewport (e.g. a dot-graph view firing
   `fetchData('graph.dot')` against an orchestrator instance).

**Design Decision — Viewports are loaded dynamically from the backend, keyed to the
resolver, behind an error boundary.**
Bundling every resolver's UI into the shell would couple the shell's release to every
resolver's. Serving `viewport.js` per resolver and importing it at runtime keeps the
shell a constant and viewports free variables — the §3 philosophy carried all the way
to the browser. The `key={resolverName}` remount and the error boundary make a broken
or mismatched viewport a contained failure, not a crashed app.

## 11.3 `ViewportProps` — the stable boundary

A viewport is a **pure function of props**. The contract (canonically in
`amplifier-app-resolve/src/types/index.ts`) is the entire surface between shell and
viewport:

```typescript
interface ViewportProps {
  instanceId:   string
  resolverName: string
  events:       ResolverEvent[]            // SSE history
  state:        Record<string, unknown>    // state.json snapshot
  status:       InstanceStatusEnum         // the 8 statuses (§4)
  inputRequests: InputRequest[]
  sendMessage:  (type: string, data?) => void
  fetchData:    (path: string) => Promise<string>   // the data bus (§8.4)
  fetchWorkspaceFile?: (path: string) => Promise<string>
  containerReady?: boolean
  onDecisionOverride?: (topic, new_choice) => void   // understudy only; preview, never authoritative
}
```

Data flows *in* (`events`, `state`, `status`, `inputRequests`); capabilities flow
*out* (`sendMessage`, `fetchData`). The shell wires these to the platform: SSE streams
events into the Zustand store; state is *polled*, not pushed; `containerReady` is
derived from the `resolve.worker.ready` event. A viewport never talks to the platform
directly — it only receives props and calls the capabilities it was handed.

**Design Decision — The viewport is a pure function of `ViewportProps`; it never
calls the platform itself.**
A fixed, narrow props contract is the seam that lets the shell and every viewport
evolve independently. Because a viewport only reads props and calls injected
capabilities, the shell can change how it fetches state, swap transports, or sandbox a
viewport without touching viewport code — and a viewport can be tested by simply
passing it props.

## 11.4 The dual-React problem

React must be **externalized** — the shell and every viewport must share *one* React
instance, or hooks crash (`Cannot read properties of null (reading 'useState')`)
because each copy has its own internal dispatcher.

- **Production:** `index.html` ships an import map pinning `react`, `react-dom`,
  `react-dom/client`, and `react/jsx-runtime` to a single CDN build; `vite.config.ts`
  marks them `external`, so the shell and every viewport resolve the bare specifiers
  to the same module.
- **Dev:** Vite pre-bundles React as CJS with only a `default` export, so a viewport's
  `import { useState } from "react"` fails. Two coordinated shims fix this: a Vite
  plugin serves dev shims and rewrites the import map, and `importViewport.ts` builds
  Blob-URL CJS shims that re-export each named binding off Vite's default and rewrites
  the viewport's bare specifiers to them. Both resolve to the *same* fully-qualified
  `react.js?v=HASH` URL — one module-cache entry, one dispatcher.

**Design Decision — React is externalized and shared; the dev-mode CJS shim is
load-bearing.**
Two React copies is the single most common way a plugin UI architecture fails. The
import map (prod) and the Blob-URL shim (dev) both exist to guarantee exactly one
React instance across shell and viewports. The shim looks like incidental complexity;
it is the opposite — do not "simplify" it away.

## 11.5 The GenericViewport fallback

When no bundle exists (404 → null) or a viewport throws (caught by
`ViewportErrorBoundary`), `GenericViewport` renders. It is domain-agnostic, driven
purely by `events` / `state` / `status`: a pulse strip (rate, errors, heartbeat), a
current-activity readout, and **adaptive state cards** that *infer* a display type per
state key (phase, progress, fraction, number, boolean, string, array, object).

**Design Decision — Every resolver gets a usable UI for free.**
A resolver author should be able to ship a working resolver with *no* frontend code
and still have consumers see meaningful progress. The GenericViewport guarantees a
baseline by interpreting only the universal contract (events, state, status). A custom
viewport is an *upgrade*, never a prerequisite — which keeps the barrier to a new
resolver low (§3.2).

## 11.6 Schema-ownership inversion

Here is the subtle, important inversion: **the viewport owns the state schema; the
resolver conforms.** The platform's delivery mechanism is generic — the resolver calls
`update_state(**kwargs)`, the daemon writes `state.json`, the shell polls it, and the
full snapshot arrives in `props.state`. Each viewport then defines its *own* typed
shape (`DotGraphState`, `OrchestratorState`, `UnderstudyVisionState`) in
`ui/src/types.ts` and parses `props.state` into it. The edge contracts
(`amplifier-bundle-resolve/docs/edges/edge-08a…c`) record these schemas.

So when you change what understudy writes to `update_state()`, the change is *driven
by* the understudy viewport's `types.ts`, not the other way around. This is why the
AGENTS.md calls the ownership "inverted."

**Design Decision — The consumer of the state defines its schema; the producer
conforms.**
The viewport is what *renders* the state, so it is best placed to define what shape it
needs. Inverting ownership — consumer defines, producer conforms — keeps the schema and
its single renderer in one repository and prevents a resolver from drifting its state
shape away from the only thing that displays it.

## 11.7 The dev override

`useViewport` reads a `?viewport_override=<url>` query param to load a viewport from an
arbitrary URL (e.g. a viewport's own Vite dev server with hot reload) — but **strictly
same-origin**. A cross-origin override would be `import()`'d as JavaScript in the app's
origin: a one-click XSS. The same-origin check is the guardrail that makes a developer
convenience safe. §12 turns to the rest of the inner development loop.
