# Experimental WorldEd bridge

`pzmapstudio.worlded.export_scene_cell` writes a compiled PZ cell with:

- real `LOTH` header with rooms and buildings;
- `LOTP` records with a room id and multiple tile names per square;
- generic B42 tiles for grass, road, pavement, interior floor, wall, door and stairs.

CLI:

```bash
python3 -m pzmapstudio.cli build-typed \
  --scene city.json --kind church --x 20 --y 20 --w 120 --h 100

python3 -m pzmapstudio.cli export-worlded-cell \
  --scene city.json --out cell-test --cell-x 0 --cell-y 0
```

Read-back check:

```text
rooms:    nave, entrance
buildings: [[0, 1]]
```

## Limits

This is experimental. It proves the header/pack bridge, not final art or
gameplay validation. Wall orientation, multi-tile doors, roof access and
furniture are still generic and must be verified in a new save.
