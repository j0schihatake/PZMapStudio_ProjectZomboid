# PZMapStudio as a Java mod

The tool now has a Java core and a B42 Java-mod entry point:

```text
java/pzmapstudio/core/PzLot.java       header/lot reader
java/pzmapstudio/core/PzLotWriter.java terrain lot writer
java/pzmapstudio/core/Scene.java       JSON command scene
java/pzmapstudio/mod/Main.java         B42 javaPkgName entry point
```

Build the preview mod:

```bash
bash tools/build_java_mod.sh
```

Result:

```text
dist/PZMapStudioMod/
  42/mod.info
  42/media/java/PZMapStudio.jar
  common/mod.info
  mod.info
  poster.png
```

Install:

```bash
rm -rf ~/Zomboid/mods/PZMapStudio
cp -a dist/PZMapStudioMod ~/Zomboid/mods/PZMapStudio
```

Enable in a new save and check `console.txt` for:

```text
[PZMapStudio] Java mod 0.1.0 loaded
```

This preview proves B42 Java loading and shares the lot/scene core. The in-game
editing UI (paint/build/furniture/spawn commands) is the next layer; it can call
the same Java methods from Lua. Steam Workshop can publish this mod folder once
that UI is ready; the standalone CLI/HTTP remains the agent interface.

## In-game live bridge

- **F10**: panel with scene path, JSON command, cell X/Y, Stage cell, Apply cell.
- **F11**: compact observer snapshot (player x/y/z, day, minutes, temperature).
- **Apply cell**: rewrites roads/sidewalks in a real compiled cell, copies the
  original `.lotheader`/`.lotpack` to `PZMapStudioBackup/<timestamp>/`, verifies
  the rewritten header, and preserves rooms/buildings.

Tested on an Isilkul cell: 714 rooms and 75 buildings survived the road rewrite.

## Agent queue

While the game runs, write one JSON command per line to:

```text
~/Zomboid/PZMapStudio/queue.jsonl
```

The Lua layer polls the Java queue every ~2 seconds and appends results to:

```text
~/Zomboid/PZMapStudio/responses.jsonl
```

Supported commands:

```json
{"op":"observe"}
{"op":"horde","count":5}
{"op":"loot","item":"Base.Bandage","count":3}
{"op":"story","kind":"camp","x":120,"y":80,"cooldown":30}
{"op":"weather","kind":"storm","seconds":120}
{"op":"door","x":120,"y":80,"z":0,"open":true}
```

`observe` returns player position, nearby zombie/item counts and temperature.
`story` kinds: `camp`, `crime`, `loot`, `horde`.
`weather` kinds: `clear`, `storm`, `fog`, `heat`.

F10 also exposes Horde, Loot, Story camp, Weather storm and Door buttons.
