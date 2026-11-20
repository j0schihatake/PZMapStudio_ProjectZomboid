# Trimming a map to fit the save buffer

If a city exceeds the `map_meta.bin` budget, keep a central cell rectangle and
drop the outer cells:

```bash
python3 -m pzmapstudio.cli trim-map \
  --source ~/Zomboid/mods/omsk-expansion/common/media/maps/"Москва" \
  --out moscow-central \
  --cells 52,99,70,115
```

The tool copies only matching `.lotheader`/`.lotpack`/`chunkdata` files and
drops spawn points outside the rectangle. It does not merge or rewrite rooms;
cells outside are simply absent.

Then audit:

```bash
python3 -m pzmapstudio.cli map-save-audit --map moscow-central
```

Trimming creates a smaller city, not a seamless full map; keep a connector/edge
design in mind. For a one-world pack, trim each oversized city until the combined
audit is below 90% of the save buffer.
