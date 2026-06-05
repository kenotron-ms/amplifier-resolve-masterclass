#!/usr/bin/env python3
"""Render polished, editorial SVGs for the masterclass.

Technique (honors "tool computes placement, I only theme"):
  1. Graphviz `dot -Tjson` computes ALL geometry — node centres/sizes, edge
     bezier control points, label positions, bounding box.
  2. This script draws a *designed* SVG from that geometry: rounded panels with
     soft shadows, a parchment palette matching the site, two-tier labels
     (title + subtitle), smooth bezier edges with arrowheads and chips.

No element is hand-placed. Re-run: `python3 diagrams/render.py`.
"""
from __future__ import annotations
import json, re, subprocess, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SRC, OUT = ROOT / "src", ROOT / "svg"

# ---- palette (matches src/styles/global.css parchment theme) ----------------
INK, MUTED, RULE = "#2a2622", "#6b6359", "#d9cfb8"
PALETTE = {
    # class           fill        border     accent (title)
    "consumer":   ("#eaf1f4", "#3f7d99", "#1f5673"),
    "platform":   ("#f6e7d0", "#b07a3f", "#8a5a2b"),
    "resolver":   ("#f1ead8", "#b89a63", "#6f5a2e"),
    "viewport":   ("#eaf0e6", "#7e9266", "#566b3f"),
    "provision":  ("#efe9dc", "#a99c80", "#7a6f55"),
    "runtime":    ("#e9e7e0", "#9b9484", "#5d564a"),
    "start":      ("#eef2f4", "#7fa0b0", "#3f6075"),
    "active":     ("#f6e7d0", "#b07a3f", "#8a5a2b"),
    "wait":       ("#f3ead2", "#c69a4a", "#8a6a1f"),
    "good":       ("#e7efe2", "#7fa06a", "#4f6f3c"),
    "bad":        ("#f1e3da", "#c08a6a", "#8a4f2f"),
    "default":    ("#f1ead8", "#cdbf9f", "#5d564a"),
}
FONT = "'Inter','Helvetica Neue',Arial,sans-serif"

PT = 72.0  # inches -> points


def run_json(dot_path: pathlib.Path) -> dict:
    out = subprocess.run(["dot", "-Tjson", str(dot_path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def label_lines(label: str) -> list[str]:
    return [ln for ln in re.split(r"\\n|\n", label or "")]


def node_svg(o: dict, H: float) -> str:
    if "pos" not in o or o.get("shape") in (None, "point"):
        return ""
    cx, cy = (float(v) for v in o["pos"].split(","))
    cy = H - cy
    w = float(o["width"]) * PT
    h = float(o["height"]) * PT
    x, y = cx - w / 2, cy - h / 2
    fill, border, accent = PALETTE.get(o.get("class", "default"), PALETTE["default"])
    dash = ' stroke-dasharray="5 4"' if "dashed" in (o.get("style") or "") else ""
    rx = min(14, h / 2)

    lines = label_lines(o.get("label") or o.get("name", ""))
    parts = [
        f'<g filter="url(#nshadow)">',
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{rx:.1f}" fill="{fill}" stroke="{border}" stroke-width="1.5"{dash}/>',
        f'</g>',
    ]
    # vertical centering of the text block
    title_sz, sub_sz, lh = 14.0, 11.5, 16.5
    total = title_sz + lh * (len(lines) - 1) if len(lines) > 1 else title_sz
    ty = cy - total / 2 + title_sz * 0.78
    for i, ln in enumerate(lines):
        if i == 0:
            parts.append(
                f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="{title_sz}" font-weight="700" '
                f'fill="{accent}">{esc(ln)}</text>')
            ty += lh
        else:
            parts.append(
                f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="{sub_sz}" font-weight="500" '
                f'fill="{MUTED}">{esc(ln)}</text>')
            ty += lh
    return "\n".join(parts)


def bspline_points(edge: dict, H: float) -> list[tuple[float, float]]:
    for d in edge.get("_draw_", []):
        if d.get("op") == "b":
            return [(p[0], H - p[1]) for p in d["points"]]
    return []


def edge_svg(e: dict, H: float) -> str:
    pts = bspline_points(e, H)
    if len(pts) < 2:
        return ""
    d = f'M {pts[0][0]:.1f} {pts[0][1]:.1f}'
    i = 1
    while i + 2 < len(pts) + 1 and i + 2 <= len(pts):
        c1, c2, p = pts[i], pts[i + 1], pts[i + 2]
        d += f' C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p[0]:.1f} {p[1]:.1f}'
        i += 3
    # any trailing points -> straight segments
    while i < len(pts):
        d += f' L {pts[i][0]:.1f} {pts[i][1]:.1f}'
        i += 1
    dash = ' stroke-dasharray="6 5"' if "dashed" in (e.get("style") or "") else ""
    has_arrow = "_hdraw_" in e
    marker = ' marker-end="url(#arrow)"' if has_arrow else ""
    out = [f'<path d="{d}" fill="none" stroke="{MUTED}" stroke-width="1.6" '
           f'stroke-linecap="round"{dash}{marker} opacity="0.85"/>']
    # label chip
    txt = None
    for ld in e.get("_ldraw_", []):
        if ld.get("op") == "T":
            txt = ld["text"]; lx, ly = ld["pt"][0], H - ld["pt"][1]
    if not txt and e.get("label"):
        txt = e["label"]; lx, ly = (float(v) for v in e["lp"].split(",")); ly = H - ly
    if txt:
        w = 7.0 + len(txt) * 6.0
        out.append(
            f'<rect x="{lx - w/2:.1f}" y="{ly - 9:.1f}" width="{w:.1f}" height="16" '
            f'rx="8" fill="#f7f3e9" stroke="{RULE}" stroke-width="1"/>')
        out.append(
            f'<text x="{lx:.1f}" y="{ly + 3.5:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="10.5" fill="{MUTED}">{esc(txt)}</text>')
    return "\n".join(out)


DEFS = (
    '<defs>'
    '<filter id="nshadow" x="-20%" y="-20%" width="140%" height="150%">'
    '<feDropShadow dx="0" dy="1.6" stdDeviation="2.6" flood-color="#2a2622" flood-opacity="0.16"/>'
    '</filter>'
    '<marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7.5" '
    'markerHeight="7.5" orient="auto-start-reverse">'
    f'<path d="M0,0.6 L9,5 L0,9.4 L2.4,5 Z" fill="{MUTED}"/>'
    '</marker>'
    '</defs>'
)


def render(dot_path: pathlib.Path) -> str:
    j = run_json(dot_path)
    _, _, W, H = (float(v) for v in j["bb"].split(","))
    pad = 10
    body = [edge_svg(e, H) for e in j.get("edges", [])]
    body += [node_svg(o, H) for o in j.get("objects", [])]
    body = [b for b in body if b]
    vw, vh = W + 2 * pad, H + 2 * pad
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" class="rdiagram" '
        f'width="{vw:.0f}" height="{vh:.0f}" '
        f'viewBox="{-pad} {-pad} {vw:.0f} {vh:.0f}" '
        f'preserveAspectRatio="xMidYMid meet" role="img">\n'
        f'{DEFS}\n' + "\n".join(body) + "\n</svg>\n")


def main() -> int:
    OUT.mkdir(exist_ok=True)
    for f in sorted(SRC.glob("*.dot")):
        svg = render(f)
        (OUT / f"{f.stem}.svg").write_text(svg)
        print(f"rendered {f.stem}.svg  ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
