#!/usr/bin/env bash
# Usage: ./diff_all.sh <root>         (root is the directory you ran lovethedocs on)

root=${1:-src}
improved='_improved'

# Find every file living under “…/_improved/…”. For each, open VS Code’s diff.
find "$root" -type f -path "*/${improved}/*.py" | while read -r imp; do
    # Strip the “…/_improved/” segment to get the original path.
    orig=${imp/${improved}\//}
    # Skip if the original file vanished or was renamed.
    [ -f "$orig" ] || continue
    echo "→ diff $orig"
    code -d "$orig" "$imp" &
done

wait

# ---- lovethedocs diff helper ----
# accept () {
#   imp="$1"                               # path inside _improved/…
#   orig="${imp/_improved\//}"             # strip that segment
#   cp "$orig" "${orig}.bak"               # 1-shot backup
#   cp "$imp"  "$orig"                     # overwrite original
#   echo "✔ accepted $imp → $orig"
# }
# ----------------------------------