#!/usr/bin/env bash
# Stage a mod for Project Zomboid's Workshop uploader.
# Usage: stage_workshop.sh <source-mod-folder> <workshop-item-name> [mod-folder-name]
set -euo pipefail
SRC="${1:?source mod folder}"
ITEM="${2:?workshop item folder name}"
MODNAME="${3:-$ITEM}"
DEST="$HOME/Zomboid/Workshop/$ITEM"
rm -rf "$DEST"
mkdir -p "$DEST/Contents/mods/$MODNAME"
cp -a "$SRC"/. "$DEST/Contents/mods/$MODNAME"/
if [ -f "$SRC/preview.png" ]; then
  cp "$SRC/preview.png" "$DEST/preview.png"
fi
echo "$DEST"
find "$DEST" -maxdepth 4 -type f | head -20
