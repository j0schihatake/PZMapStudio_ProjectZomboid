#!/usr/bin/env bash
# Stage a mod for Project Zomboid's Workshop uploader.
# Usage: stage_workshop.sh <source-mod-folder> <workshop-item-name> [mod-folder-name]
set -euo pipefail
SRC="${1:?source mod folder}"
ITEM="${2:?workshop item folder name}"
MODNAME="${3:-$ITEM}"
DEST="$HOME/Zomboid/Workshop/$ITEM"
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
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
  python3 - "$DEST/workshop.txt" "$ITEM" "$SCRIPT_DIR/workshop_titles.json" <<'PYTITLE'
import json, sys
from pathlib import Path
path, item, title_file = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
titles = json.loads(title_file.read_text()) if title_file.exists() else {}
lines = path.read_text().splitlines()
out = []
for line in lines:
    if line.startswith("title="):
        line = "title=" + titles.get(item, item)
    out.append(line)
path.write_text("\n".join(out) + "\n")
PYTITLE
else
  python3 - "$ITEM" "$DEST/workshop.txt" "$SCRIPT_DIR/workshop_ids.json" "$SCRIPT_DIR/workshop_titles.json" <<'PYID'
import json, sys
from pathlib import Path
item, out, id_file, title_file = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
ids = json.loads(id_file.read_text())
titles = json.loads(title_file.read_text()) if title_file.exists() else {}
if item in ids:
    out.write_text(f"version=1\nid={ids[item]}\ntitle={titles.get(item, item)}\n")
PYID
fi
echo "$DEST"
find "$DEST" -maxdepth 4 -type f | head -20
