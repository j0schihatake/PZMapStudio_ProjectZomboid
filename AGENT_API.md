# Agent API

Start:

```bash
python3 -m pzmapstudio.cli serve --scene map.json --port 8765
```

Commands are JSON objects with an `op`:

```json
{"op":"paint","layer":"roads","x":100,"y":100,"w":200,"h":16,"tile":"asphalt"}
{"op":"build_house","x":40,"y":40,"w":80,"h":60,"floors":3,"rooms":6,"furnish":true}
{"op":"add_floor","building":"house-1","z":3,"rooms":4}
{"op":"place_furniture","building":"house-1","x":50,"y":50,"z":3,"kind":"bed"}
{"op":"add_spawn","x":60,"y":90,"z":0}
{"op":"add_story","x":10,"y":10,"w":20,"h":10,"kind":"murder_scene","name":"Murder scene"}
{"op":"add_roof_access","building":"house-1","x":50,"y":50,"z":0,"to_z":3,"kind":"ladder"}
{"op":"add_road","x":100,"y":100,"w":300,"h":12,"material":"asphalt","sidewalk":true}
{"op":"add_fence","x":100,"y":130,"length":80,"axis":"x","kind":"picket","gate":true}
{"op":"undo"}
{"op":"redo"}
```

`GET /api/scene` returns the whole scene, `GET /api/render.png?floor=0`
returns a preview, `POST /api/command` mutates it, `POST /api/save` persists it.

This is the contract a browser or Unity-like client should implement against.


## Asset catalog

Build from the installed game:

```bash
python3 -m pzmapstudio.cli build-catalog \
  --pz-root /path/to/ProjectZomboid/projectzomboid \
  --out pz-catalog.json.gz
python3 -m pzmapstudio.cli search-catalog \
  --catalog pz-catalog.json.gz --kind items --query axe
```

The catalog exposes tile names, item names and randomized-story clutter tables
from the current game build. The current B42 install yields about 32k tile names,
5k item names and 49 story clutter tables.
