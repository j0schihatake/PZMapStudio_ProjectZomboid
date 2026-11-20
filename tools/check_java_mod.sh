#!/usr/bin/env bash
# Verify the PZMapStudio Java/Lua mod folder.
set -euo pipefail
MOD="${1:-dist/PZMapStudioMod}"
test -f "$MOD/mod.info" || { echo "missing mod.info"; exit 1; }
test -f "$MOD/42/media/java/PZMapStudio.jar" || { echo "missing jar"; exit 1; }
test -f "$MOD/common/media/lua/client/PZMapStudio.lua" || { echo "missing Lua"; exit 1; }
grep -q 'javaJarFile=media/java/PZMapStudio.jar' "$MOD/mod.info" || { echo "bad javaJarFile"; exit 1; }
grep -q 'javaPkgName=pzmapstudio.mod' "$MOD/mod.info" || { echo "bad javaPkgName"; exit 1; }
forbidden=$(find "$MOD" \( -name '*.sh' -o -name '*.bat' -o -name '*.zip' -o -name '*.exe' -o -name '*.dll' \) -print)
if [ -n "$forbidden" ]; then echo "forbidden:"; echo "$forbidden"; exit 1; fi
echo "PZMapStudio mod OK"
