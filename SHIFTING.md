# Shifting a compiled map

Move a map by whole **256-tile compiled cells** without rebuilding it:

```bash
python3 -m pzmapstudio.cli shift-map \
  --source ~/Zomboid/mods/omsk-expansion/common/media/maps/"Омск, Омская область" \
  --out omsk-shifted \
  --dx-cells 20 --dy-cells 27 \
  --shift-objects
```

What moves:

- `X_Y.lotheader` -> `(X+dx)_(Y+dy).lotheader`;
- `world_X_Y.lotpack` and `chunkdata_X_Y.bin`;
- `spawnpoints.lua` (`posX/posY` shift by `dx*256`, `dy*256`);
- `worldmap.xml` cell coordinates;
- optional simple `x,y` pairs in `objects.lua` / `worldmap-annotations.lua`.

What is copied unchanged:

- room rectangles inside headers (they are cell-local);
- terrain, buildings, furniture, roads;
- worldmap binary; regenerate it if needed.

A shifted map still needs a road/connector map to look continuous. Use
`find-space` to choose a free block, then `shift-map`, then apply the road pass
or add a connector map.
