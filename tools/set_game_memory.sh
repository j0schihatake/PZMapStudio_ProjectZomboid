#!/usr/bin/env bash
# Raise the Project Zomboid heap limit to 30 GB.
set -euo pipefail

CONFIG="${1:-/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/projectzomboid/ProjectZomboid64.json}"

if [ ! -f "$CONFIG" ]; then
  echo "config not found: $CONFIG" >&2
  exit 1
fi

BACKUP="${CONFIG}.bak-$(date +%Y%m%d-%H%M%S)"
cp -a "$CONFIG" "$BACKUP"

python3 - "$CONFIG" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text())
args = data.get("vmArgs", [])
old = [x for x in args if str(x).startswith("-Xmx")]
new = [x for x in args if not str(x).startswith("-Xmx")]
new.append("-Xmx30g")
data["vmArgs"] = new
path.write_text(json.dumps(data, indent="\t") + "\n")
print("old:", old)
print("new: ['-Xmx30g']")
PY

echo "backup: $BACKUP"
echo "updated: $CONFIG"
echo "restart Project Zomboid completely for the new heap to apply."
