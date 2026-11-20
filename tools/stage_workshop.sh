#!/usr/bin/env bash
# Stage a mod for Project Zomboid's Workshop uploader.
# Usage: stage_workshop.sh <source-mod-folder> <workshop-item-name> [mod-folder-name]
set -euo pipefail
SRC="${1:?source mod folder}"
ITEM="${2:?workshop item folder name}"
MODNAME="${3:-$ITEM}"
DEST="$HOME/Zomboid/Workshop/$ITEM"
OLD_WORKSHOP=""
if [ -f "$DEST/workshop.txt" ]; then
  OLD_WORKSHOP=$(mktemp)
  cp "$DEST/workshop.txt" "$OLD_WORKSHOP"
fi
rm -rf "$DEST"
mkdir -p "$DEST/Contents/mods/$MODNAME"
cp -a "$SRC"/. "$DEST/Contents/mods/$MODNAME"/
if [ -f "$SRC/preview.png" ]; then
  cp "$SRC/preview.png" "$DEST/preview.png"
fi
if [ -n "$OLD_WORKSHOP" ] && [ -f "$OLD_WORKSHOP" ]; then
  cp "$OLD_WORKSHOP" "$DEST/workshop.txt"
  rm -f "$OLD_WORKSHOP"
else
  python3 - "$ITEM" "$DEST/workshop.txt" <<'PYID'
import json, sys
from pathlib import Path
item, out = sys.argv[1], Path(sys.argv[2])
ids = json.loads(Path(__file__).resolve().parent.joinpath("workshop_ids.json").read_text())
if item in ids:
    out.write_text(f"version=1\nid={ids[item]}\ntitle={item}\n")
PYID
fi
echo "$DEST"
find "$DEST" -maxdepth 4 -type f | head -20
