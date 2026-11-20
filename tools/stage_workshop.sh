#!/usr/bin/env bash
# Stage a mod for Project Zomboid's Workshop uploader.
# Usage: stage_workshop.sh <source-mod-folder> <workshop-name>
set -euo pipefail
SRC="${1:?source mod folder}"
NAME="${2:?workshop item folder name}"
DEST="$HOME/Zomboid/Workshop/$NAME"
rm -rf "$DEST"
mkdir -p "$DEST/Contents"
cp -a "$SRC"/. "$DEST/Contents"/
if [ -f "$SRC/preview.png" ]; then
  cp "$SRC/preview.png" "$DEST/preview.png"
fi
echo "$DEST"
find "$DEST" -maxdepth 2 -type f | head
