#!/usr/bin/env bash
# Download, build and install the latest ZombieBuddy Java agent.
#
# It updates:
#   - the game agent used by normal launches;
#   - the PersonalKnox test cache agent, when present;
#   - ProjectZomboid64.json with -javaagent:ZombieBuddy.jar.
#
# It never starts or stops the game. Run it while the game is closed.
set -euo pipefail

GAME="${PZ_GAME:-/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid}"
SRC="${ZOMBIE_BUDDY_SRC:-$GAME/work/ZombieBuddy-src}"
JDK="${PZ_JDK:-$GAME/work/toolchain/oracle-jdk-25}"
CONFIG="${PZ_CONFIG:-$GAME/projectzomboid/ProjectZomboid64.json}"
AGENT="$GAME/projectzomboid/ZombieBuddy.jar"

if [ ! -d "$SRC/.git" ]; then
  echo "ZombieBuddy source not found: $SRC" >&2
  exit 1
fi
if [ ! -x "$JDK/bin/java" ]; then
  echo "JDK 25 not found: $JDK" >&2
  exit 1
fi
if [ ! -f "$CONFIG" ]; then
  echo "launch config not found: $CONFIG" >&2
  exit 1
fi

echo "== update source =="
git -C "$SRC" fetch --all --prune
git -C "$SRC" pull --ff-only

echo "== build ZombieBuddy =="
(
  cd "$SRC/java"
  JAVA_HOME="$JDK" ./gradlew --no-daemon \
    -PjavaVersion=25 \
    -PgameClasspath="$GAME/projectzomboid/projectzomboid.jar" \
    shadowJar
)

JAR=$(find "$SRC/java/build" -type f -name 'ZombieBuddy*.jar' \
  ! -name '*plain*' ! -name '*sources*' ! -name '*javadoc*' \
  -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
if [ -z "${JAR:-}" ] || [ ! -f "$JAR" ]; then
  echo "built ZombieBuddy jar not found" >&2
  exit 1
fi

echo "== install agent =="
STAMP=$(date +%Y%m%d-%H%M%S)
if [ -f "$AGENT" ]; then cp -a "$AGENT" "$AGENT.bak-$STAMP"; fi
install -m 0644 "$JAR" "$AGENT"

# Test cache(s) used by PersonalKnox/dev launches.
for dst in "$GAME"/work/pz-cache/mods/*/libs/ZombieBuddy.jar; do
  [ -f "$dst" ] || continue
  cp -a "$dst" "$dst.bak-$STAMP" 2>/dev/null || true
  install -m 0644 "$JAR" "$dst"
  echo "updated test cache: $dst"
done

echo "== add javaagent =="
python3 - "$CONFIG" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text())
args = data.setdefault("vmArgs", [])
if not any(str(x).startswith("-javaagent:ZombieBuddy.jar") for x in args):
    args.append("-javaagent:ZombieBuddy.jar")
    path.write_text(json.dumps(data, indent="\t") + "\n")
    print("added -javaagent:ZombieBuddy.jar")
else:
    print("-javaagent:ZombieBuddy.jar already present")
PY

echo "agent: $AGENT"
echo "built: $JAR"
echo "config: $CONFIG"
echo "restart the game completely to load the new agent."
