# One world vs. detailed cities

Project Zomboid stores room/building state for **all maps in one world** in one
`map_meta.bin` buffer (~10.49 MB). The current six-city pack is:

```text
rooms:      2,640,354
buildings:    227,724
state:       31.67 MB
with reserve 34.84 MB
over budget  3.32x
```

Therefore these three goals cannot all be true at once:

1. one world;
2. every city fully accessible;
3. every building has full interior/loot/alarm state.

## Option A — one world, all cities visible, light interiors

Keep every city on one map and reduce room/building metadata for most buildings:

- streets, terrain, buildings, props and lootable tile objects remain;
- only selected "hero" buildings keep full room/building state;
- all cities can be visited in one save;
- most interiors become shells rather than fully tracked rooms.

This is the best fit for "all cities available in the game world". It needs a
`lighten-map`/room-budget tool: strip selected header rooms/buildings while
keeping the terrain and object tiles.

## Option B — full detail, separate worlds

Keep the current interiors and publish per-city mods/worlds:

```text
Isilkul + villages
Omsk
Krasnodar
Novosibirsk (trimmed or rescaled)
Moscow (trimmed or rescaled)
```

Full detail, but only one city group per save. A portal/transfer mod would be a
separate project; native PZ cannot seamlessly travel between saves.

## Option C — one world, trimmed cities

Use `trim-map` to keep central districts until the combined audit is under 90%.
All cities remain in one save, but outskirts and some content are removed.

## Recommended path

Build **Option A** as the public "one world" edition and keep per-city detailed
editions as optional mods:

```text
OmskExpansion-World      all cities, light room budget
OmskExpansion-Detailed-* per-city full interiors
```

The next tool is a room/building budget pruner with a hard target below the save
buffer; it must preserve headers/objects where possible and report exactly what
was dropped.
