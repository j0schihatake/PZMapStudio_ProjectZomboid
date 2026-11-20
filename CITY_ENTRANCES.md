# City entrances

`tools/city_entrances.py` adds a road stub from each of the four sides of every
compiled map:

```bash
python3 tools/city_entrances.py \
  --map-root /path/to/maps
```

Each stub is 80 tiles long and 8 tiles wide, using a real PZ street tile. The
original `.lotheader` is preserved, so rooms/buildings survive.

Current result:

```text
Isilkul       4 sides
Solntsevka    4 sides
Omsk          4 sides
Krasnodar     4 sides
Novosibirsk   4 sides
Moscow        4 sides
Trumbull      4 sides
```

This gives multiple approaches into each city. It does not yet prove that the
stubs meet the neighboring map's road at the same tile; that needs a
border-alignment pass and an in-game drive test.
