#!/usr/bin/env bash
# Verify a local map mod and/or Workshop staging folder.
set -euo pipefail
MAP="${1:-}"
WS="${2:-}"
if [ -n "$MAP" ]; then
  echo "== map mod =="
  test -f "$MAP/mod.info" || { echo "missing mod.info"; exit 1; }
  find "$MAP/common/media/maps" -maxdepth 1 -type d | wc -l | xargs echo "map folders:"
  find "$MAP/common/media/maps" -name '*.lotheader' | wc -l | xargs echo "cells:"
  python3 - "$MAP" <<'PY'
import sys
from pathlib import Path
root=Path(sys.argv[1])/'common/media/maps'
seen={}
for cell in root.glob('*/*.lotheader'):
    key=cell.stem
    seen.setdefault(key,[]).append(cell.parent.name)
dups={k:v for k,v in seen.items() if len(v)>1}
print('duplicate cells:',len(dups))
PY
fi
if [ -n "$WS" ]; then
  echo "== workshop =="
  test -d "$WS/Contents/mods" || { echo "missing Contents/mods"; exit 1; }
  test -f "$WS/preview.png" || { echo "missing preview.png"; exit 1; }
  python3 - "$WS/preview.png" <<'PY'
import sys
from PIL import Image
im=Image.open(sys.argv[1])
print('preview:', im.size)
assert im.size==(256,256), 'preview must be 256x256'
PY
  find "$WS/Contents/mods" -maxdepth 2 -name mod.info -print
fi
echo OK
