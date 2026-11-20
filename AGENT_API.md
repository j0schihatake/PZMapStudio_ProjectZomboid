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
{"op":"undo"}
{"op":"redo"}
```

`GET /api/scene` returns the whole scene, `GET /api/render.png?floor=0`
returns a preview, `POST /api/command` mutates it, `POST /api/save` persists it.

This is the contract a browser or Unity-like client should implement against.
