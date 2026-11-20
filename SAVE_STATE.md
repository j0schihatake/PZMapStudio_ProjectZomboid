# Map save-state audit

Project Zomboid writes per-room and per-building state into a fixed
`map_meta.bin` buffer. A map can compile fine and still fail to save which
buildings were explored/alarmed.

```bash
python3 -m pzmapstudio.cli map-save-audit --map /path/to/map
```

The report includes:

- cells, rooms and buildings;
- this map's estimated state bytes;
- the shared world/Knox County reserve;
- total against the 10,485,760-byte buffer;
- a warning above 90% of the buffer.

Known example: Isilkul is comfortably under the limit; Omsk is at about 94% and
needs trimming or a larger metres-per-tile scale before a long save.


## Whole-mod audit

```bash
python3 -m pzmapstudio.cli map-save-audit --map-root /path/to/maps
```

This sums every map that will share one world save buffer. Current generated
six-map pack is far above the limit (about 34.8 MB against 10.49 MB). A single
world with all six detailed cities cannot be save-safe without a major scale or
room-count reduction; split worlds or smaller city extents are the practical
options.


## Reality check

A real tested save with the current mod produced a `map_meta.bin` of about
**3.46 MB**, not 9.8 MB. The audit above is deliberately conservative: it counts
every room/building in all headers plus the shared world reserve. PZ does not
write the full theoretical maximum for an unvisited map.

Do not trim or rescale a map solely because this estimate is high. Confirm with
a real save/reload and a long session first. Use `trim-map`/`lighten-map` only if
the game actually throws `BufferOverflowException` or the real `map_meta.bin`
approaches the buffer.
