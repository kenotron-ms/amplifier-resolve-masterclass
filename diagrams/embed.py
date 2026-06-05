#!/usr/bin/env python3
"""Inline the themed SVGs into the chapter markdown as <figure> blocks.

Idempotent via HTML-comment markers: <!-- diagram:NAME --> ... <!-- /diagram:NAME -->.
First run finds the fenced ASCII block (by signature) and replaces it; later runs
replace whatever is between the markers. The ASCII is preserved as a collapsible
"text version" for accessibility / terminal readers.
"""
from __future__ import annotations
import pathlib, re, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
CH = ROOT / "src" / "content" / "chapters"
SVG = ROOT / "diagrams" / "svg"
ASCII = ROOT / "diagrams" / "ascii"

# (chapter file, fence signature, diagram name, caption)
JOBS = [
    ("02-architecture-map.md", "POST /instances", "architecture-map",
     "The Resolve platform, end to end. Any consumer reaches the daemon the same way "
     "(POST /instances); the daemon launches one isolated resolver container per instance."),
    ("02-architecture-map.md", "1 triage", "three-concern",
     "A worked example: the GitHub-driven triage \u2192 implement \u2192 review loop. "
     "One integration of the event-driven consumer pattern \u2014 not the architecture."),
    ("04-instance-lifecycle.md", "awaiting_input", "instance-status",
     "The eight instance statuses and their transitions."),
    ("12-provisioning-and-inner-loop.md", "Incus bridge", "dtu-topology",
     "DTU topology: workers and reality-check are Incus siblings of the DTU; "
     "the Gitea sidecar is a Docker container that lives inside it."),
    ("13-complete-picture.md", "EDGE", "six-layer-stack",
     "The six layers. Each depends only on the one below; the platform (layer 2) is the still center."),
]


def figure(name: str, caption: str) -> str:
    svg = (SVG / f"{name}.svg").read_text().strip()
    ascii_txt = (ASCII / f"{name}.txt").read_text().rstrip("\n")
    cap = html.escape(caption)
    pre = html.escape(ascii_txt)
    # NOTE: a single HTML block — no blank lines inside (CommonMark requirement).
    return (
        f"<!-- diagram:{name} -->\n"
        f'<figure class="diagram">\n{svg}\n'
        f'<figcaption>{cap}</figcaption>\n'
        f'<details class="diagram-text"><summary>Text version</summary>'
        f'<pre class="diagram-ascii">{pre}</pre></details>\n'
        f"</figure>\n"
        f"<!-- /diagram:{name} -->"
    )


def replace_between_markers(text: str, name: str, block: str) -> str | None:
    pat = re.compile(rf"<!-- diagram:{re.escape(name)} -->.*?<!-- /diagram:{re.escape(name)} -->",
                     re.S)
    if pat.search(text):
        return pat.sub(lambda _: block, text, count=1)
    return None


def replace_fence(text: str, signature: str, block: str) -> str | None:
    lines = text.splitlines()
    fences = [i for i, ln in enumerate(lines) if ln.strip() == "```"]
    for a, b in zip(fences[0::2], fences[1::2]):
        if signature in "\n".join(lines[a + 1:b]):
            return "\n".join(lines[:a] + [block] + lines[b + 1:]) + "\n"
    return None


def main() -> int:
    ok = True
    for fname, sig, name, caption in JOBS:
        md = CH / fname
        text = md.read_text()
        block = figure(name, caption)
        new = replace_between_markers(text, name, block)
        if new is None:
            new = replace_fence(text, sig, block)
        if new is None:
            print(f"NO TARGET for {name} in {fname}"); ok = False; continue
        md.write_text(new)
        print(f"embedded {name} -> {fname}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
