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
