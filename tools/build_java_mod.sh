#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JAVA=/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/toolchain/oracle-jdk-25/bin
GSON=/home/j0schi/.m2/repository/com/google/code/gson/gson/2.11.0/gson-2.11.0.jar
cd "$ROOT"
rm -rf java/build java/PZMapStudio.jar
mkdir -p java/build
"$JAVA/javac" -cp "$GSON" -d java/build $(find java -name '*.java')
(cd java/build && "$JAVA/jar" xf "$GSON")
"$JAVA/jar" --create --file java/PZMapStudio.jar -C java/build .
rm -rf dist/PZMapStudioMod
mkdir -p dist/PZMapStudioMod/42/media/java dist/PZMapStudioMod/common/media/lua/client
cp java/PZMapStudio.jar dist/PZMapStudioMod/42/media/java/
if [ -f common/media/lua/client/PZMapStudio.lua ]; then
  cp common/media/lua/client/PZMapStudio.lua dist/PZMapStudioMod/common/media/lua/client/
fi
cp /home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/omsk-expansion/poster.png dist/PZMapStudioMod/42/poster.png
cat > dist/PZMapStudioMod/42/mod.info <<'INFO'
name=PZMapStudio
id=PZMapStudio
modversion=0.1.0
versionMin=42.22
versionMax=42.22
description=Agent-first Java map toolkit for Project Zomboid. Core loads as a Java mod; standalone CLI/HTTP and in-game editing are the next layers.
poster=poster.png
javaJarFile=media/java/PZMapStudio.jar
javaPkgName=pzmapstudio.mod
INFO
cp dist/PZMapStudioMod/42/mod.info dist/PZMapStudioMod/mod.info
cp dist/PZMapStudioMod/42/mod.info dist/PZMapStudioMod/common/mod.info
cp dist/PZMapStudioMod/42/poster.png dist/PZMapStudioMod/poster.png
printf 'PZMapStudio Java mod preview.\nSee README.txt in the repository.\n' > dist/PZMapStudioMod/README.txt
echo "$ROOT/dist/PZMapStudioMod"
