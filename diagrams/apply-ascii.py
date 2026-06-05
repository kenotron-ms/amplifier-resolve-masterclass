#!/usr/bin/env python3
"""Swap hand-drawn ASCII diagram blocks in the section markdown for the
tool-generated ASCII under diagrams/ascii/.

A diagram block is a ``` fenced block whose body contains a unique SIGNATURE
string. We replace the body with the matching generated .txt, preserving the
fences. Idempotent: re-running with already-swapped content is a no-op because
the signature still matches and we just rewrite the same content.
"""
from __future__ import annotations
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SECTIONS = ROOT / "content" / "sections"
ASCII = ROOT / "diagrams" / "ascii"

# (section file, signature substring, ascii file)
JOBS = [
    ("02-architecture-map.md", "GitHub Issues / PRs", "architecture-map.txt"),
    ("02-architecture-map.md", "Concern 1", "three-concern.txt"),
    ("04-instance-lifecycle.md", "created", "instance-status.txt"),
    ("12-provisioning-and-inner-loop.md", "Incus bridge", "dtu-topology.txt"),
    ("13-complete-picture.md", "EDGE", "six-layer-stack.txt"),
]


def swap(md_path: pathlib.Path, signature: str, ascii_text: str) -> bool:
    lines = md_path.read_text().splitlines()
    # find fenced blocks (plain ``` only, ignore ```lang code blocks)
    fences = [i for i, ln in enumerate(lines) if ln.strip() == "```"]
    for a, b in zip(fences[0::2], fences[1::2]):
        body = "\n".join(lines[a + 1 : b])
        if signature in body:
            new = lines[: a + 1] + ascii_text.rstrip("\n").splitlines() + lines[b:]
            md_path.write_text("\n".join(new) + "\n")
            return True
    return False


def main() -> int:
    ok = True
    for fname, sig, afile in JOBS:
        md = SECTIONS / fname
        atxt = (ASCII / afile).read_text()
        if swap(md, sig, atxt):
            print(f"swapped {afile:24s} -> {fname} (sig: {sig!r})")
        else:
            print(f"NO MATCH for {sig!r} in {fname}", file=sys.stderr)
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
