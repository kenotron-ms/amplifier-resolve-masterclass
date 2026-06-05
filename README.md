# Amplifier Resolve — Masterclass

An Astro static site presenting a first-principles → implementation → future
reading of **Amplifier Resolve**: the platform that turns a request ("resolve
this issue") into an isolated, observable, long-lived run of a pluggable
resolver — and delivers a pull request at the other end.

The through-line: **the platform provides mechanism; the resolver provides
policy.**

Published as a GitHub Pages project site at
<https://kenotron-ms.github.io/amplifier-resolve-masterclass/>.

## Develop & build

Requires Node 20+ (developed on Node 24) and npm.

```bash
npm install        # install pinned deps (creates package-lock.json)
npm run build      # produce the static site in dist/
npm run preview    # serve the built site locally
npm run dev        # live-reloading dev server
```

The build is fully static; `dist/` can be served by any static host.

## Source of truth

- **Chapters live in `src/content/chapters/`** — 14 markdown files
  (`01-introduction.md` … `13-complete-picture.md` plus
  `appendix-glossary-and-invariants.md`). Each has YAML frontmatter with
  `title` (string) and `chapter` (number, or the string `"A"` for the
  appendix). Edit these to change the content; the site, sidebar, table of
  contents, and prev/next links all regenerate from this collection
  (`src/content/config.ts`).
- Routes: `/` (landing + auto-generated TOC) and `/chapters/<slug>` (one per
  chapter), defined under `src/pages/`.
- Layout, sidebar, and styling live in `src/layouts/BaseLayout.astro` and
  `src/styles/global.css`.

## Diagrams

Structural diagram sources are Graphviz `.dot` files under `diagrams/src/`.
They are rendered two ways by the toolchain (no hand placement):

- `dot -Tsvg` → `diagrams/svg/*.svg` (used on the site; copied to
  `public/diagrams/` and surfaced as the landing hero figure).
- `graph-easy --as_boxart` → ASCII box-art, applied inline into the chapter
  markdown as fenced code blocks.

To regenerate after editing a `.dot` source:

```bash
bash diagrams/build.sh          # render .dot → SVG + ASCII
python3 diagrams/apply-ascii.py # splice ASCII blocks back into the chapters
```

> **Requirement:** the ASCII renderer uses Perl's `Graph::Easy`, installed
> locally (no root) under `~/perl5`. The build script expects it on
> `PERL5LIB`/`PATH` via `~/perl5` (e.g. `eval "$(perl -I$HOME/perl5/lib/perl5 -Mlocal::lib)"`).
> Graphviz (`dot`) must also be installed. After regenerating, re-run
> `npm run build` so `public/diagrams/` picks up the new SVGs (or re-copy them).

## Deployment

`.github/workflows/deploy.yml` builds the site with the official
`withastro/action` and publishes to GitHub Pages on every push to `main`.
The base path (`/amplifier-resolve-masterclass`) and site URL are set in
`astro.config.mjs`; all internal links are base-aware via
`import.meta.env.BASE_URL`.

## Repository layout

```
src/content/chapters/   # the masterclass chapters (source of truth)
src/content/config.ts   # content collection schema
src/pages/              # routes (landing + chapter template)
src/layouts/            # shell: sidebar, header, typography
src/styles/global.css   # parchment theme + scrollable code/diagram blocks
public/diagrams/        # rendered SVG diagrams (served)
diagrams/               # diagram toolchain (.dot sources, build.sh, apply-ascii.py)
```
