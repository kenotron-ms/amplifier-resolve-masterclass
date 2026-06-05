#!/usr/bin/env bash
# Regenerate every diagram from its structural .dot source.
#
# Technique: we never hand-place elements. Each diagram is defined structurally
# (nodes + edges) in diagrams/src/*.dot. Two layout engines compute placement:
#   • Graphviz `dot`  -> SVG   (for the Astro site)
#   • Graph::Easy     -> ASCII (for the markdown / terminal reading)
#
# Graph::Easy is installed locally (no sudo) under ~/perl5. If it is missing,
# run:  curl -sL https://cpanmin.us | perl - -n -l ~/perl5 Graph::Easy
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/src"; SVG="$HERE/svg"; ASCII="$HERE/ascii"
mkdir -p "$SVG" "$ASCII"

export PERL5LIB="${PERL5LIB:-}:$HOME/perl5/lib/perl5"
export PATH="$HOME/perl5/bin:$PATH"

command -v dot        >/dev/null || { echo "ERROR: graphviz 'dot' not found"; exit 1; }
command -v graph-easy >/dev/null || { echo "ERROR: 'graph-easy' not found (see header)"; exit 1; }

for f in "$SRC"/*.dot; do
  name="$(basename "$f" .dot)"
  echo "• $name (ascii)"
  # Unicode box-drawing ASCII (terminal / text-version fallback)
  graph-easy --from=dot --as_boxart "$f" > "$ASCII/$name.txt" 2>/dev/null
  # Pure-ASCII fallback (no Unicode), useful for plain-text contexts
  graph-easy --from=dot --as_ascii  "$f" > "$ASCII/$name.ascii.txt" 2>/dev/null
done

# Polished, themed SVGs (graphviz computes layout; render.py applies the design).
python3 "$HERE/render.py"

echo "Done. SVG -> diagrams/svg/  ASCII -> diagrams/ascii/"
echo "Next: python3 diagrams/embed.py  (inlines SVGs into the chapters)"
