# PZ file-format compatibility

PZMapStudio isolates the binary lot format in `pzmapstudio/pzlot.py`.

## .lotheader

- magic `LOTH`;
- version (currently 1);
- tile-name table;
- 8x8 chunk size;
- min/max level;
- rooms;
- buildings.

The reader exposes `Header.version`. The writer copies an existing header when
editing real cells, so a future PZ build can change room/object fields without
losing them during a road/object pass.

## .lotpack

- magic `LOTP`;
- version (currently 1);
- 1024 chunk offsets;
- per-chunk records in z/x/y order.

## Terrain-only export

`write_cell` emits version 1 and no rooms/buildings. Use it only for new terrain
tests, not for replacing a real populated cell; use `rewrite_cell` for existing
maps.

## Future game updates

When a new PZ build changes the format:

1. inspect a new cell with `read_header`/`read_header_full`;
2. add a version branch in `pzlot.py`;
3. keep `rewrite_cell` copying unknown header bytes verbatim;
4. add fixture cells from the new build under `tests/fixtures/`;
5. never overwrite a save or compiled map without a backup.
