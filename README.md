# PZMapStudio

Agent-friendly map studio for Project Zomboid.

This is a separate project from KnoxMap. It starts with a command-driven scene
model: an agent can paint terrain and roads, build multi-storey houses, add
furniture and spawn markers, render a preview, undo/redo, and export a
PZ-oriented bundle. It also has a small HTTP API so a human UI and an agent can
work on the same scene in real time.

## What works now

- sparse tile layers (terrain, roads, water, walls, floors, objects);
- `build_house` with arbitrary floors, rooms, doors and furniture;
- `add_floor`, `place_furniture`, `paint`, `erase`;
- spawn markers;
- undo/redo;
- JSON scene persistence;
- PNG preview;
- PZ bundle export (`map.info`, `spawnpoints.lua`, `objects.lua`, scene JSON);
- import of a KnoxMap `.pzw` project's dimensions and `spawnpoints.lua`;
- CLI and HTTP command API.

It does **not** yet write binary `.lotheader`/`.lotpack` files. A scene is
exported as a bundle that the PZ/WorldEd compiler can be attached to; that
adapter is the next milestone.

## Quick start

```bash
python3 -m pzmapstudio.cli new --name demo --width 512 --height 512 --out demo.json
python3 -m pzmapstudio.cli paint --scene demo.json --layer roads \
  --rect 0,240,512,24 --tile asphalt
python3 -m pzmapstudio.cli build-house --scene demo.json \
  --x 100 --y 100 --w 80 --h 60 --floors 3 --rooms 6
python3 -m pzmapstudio.cli add-spawn --scene demo.json --x 140 --y 180
python3 -m pzmapstudio.cli render --scene demo.json --out demo.png
python3 -m pzmapstudio.cli export --scene demo.json --out demo-bundle
```

## HTTP API

```bash
python3 -m pzmapstudio.cli serve --scene demo.json --port 8765
```

Endpoints:

```text
GET  /api/scene
GET  /api/render.png?floor=0
POST /api/command   {"op":"build_house", ...}
POST /api/save
```

Example command:

```json
{
  "op": "build_house",
  "x": 100,
  "y": 100,
  "w": 80,
  "h": 60,
  "floors": 3,
  "rooms": 6,
  "furnish": true
}
```

## Importing a generated KnoxMap map

```bash
python3 -m pzmapstudio.cli import-knoxmap \
  --pzw /path/to/output/omsk-city/omsk-city.pzw \
  --spawnpoints /path/to/spawnpoints.lua \
  --out omsk-scene.json
```

The importer reads the world dimensions and spawn points. Terrain/buildings
from compiled cells are a later adapter; the scene is an editable overlay on
the generated world.

## Design

The scene is intentionally independent of PZ's binary lot format. Commands are
small JSON objects, so an agent can issue them through the API while a human
uses the same operations from a UI.
