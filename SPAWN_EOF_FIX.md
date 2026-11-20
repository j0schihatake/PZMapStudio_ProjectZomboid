# Spawn/load fix: lotheader zombie intensity

New cells written by `pzstudio.worlded` were missing the 1024-byte zombie
intensity table that `IsoMetaGrid` reads after rooms/buildings.

Symptom in `console.txt`:

```text
ERROR loading .../Providence Ridge/147_102.lotheader
java.io.EOFException: wx=147, wy=102, nBytes=0,
this.zombieIntensity.length=1024
```

Fix:

- append exactly 1024 zero bytes to generated `.lotheader` files;
- `worlded.export_scene_cell` now writes the table automatically.

Patched builds:

```text
Trumbull_Valley   930 headers
Cascade Hills     650
Drucker County    650
Meagher Valley    650
Providence Ridge  650
```

Recopy the mods and use a new save.
