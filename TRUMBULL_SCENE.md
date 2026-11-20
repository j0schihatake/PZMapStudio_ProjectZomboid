# Trumbull Valley scene foundation

`tools/build_trumbull_scene.py` builds the first layout scene:

```text
7500 x 7800 tiles
3 town grids
2 fairground loops
river
highway and farm access roads
3 spawn points
```

Run:

```bash
python3 tools/build_trumbull_scene.py
python3 -m pzmapstudio.cli render --scene examples/trumbull-scene.json --out examples/trumbull-scene.png
```

This is a terrain/roads foundation, not a finished playable map. Town grids still
need real buildings, interiors, fair structures, farms, fences and roof access.
The scene file is large (~87 MB) because it contains every road/water tile.
