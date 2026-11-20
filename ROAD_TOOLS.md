# Road connectivity tools

## Report

```bash
python3 tools/road_connectivity.py --map-root /path/to/maps
python3 tools/road_connectivity.py --map-root /path/to/maps --json
```

Uses only edge chunks, so it is much faster than scanning every cell.

## Align

```bash
python3 tools/road_align.py --map-root /path/to/maps
python3 tools/road_align.py --map-root /path/to/maps --apply
```

Copies road positions across adjacent cell borders and extends them 8 tiles
inward. The header/buildings are preserved.

Current result after alignment:

```text
boundary pairs with roads: 16
matching pairs: 16
```

Some map pairs still have no road at the border; they need explicit connector
roads or a bridge map.

## Entrances

```bash
python3 tools/city_entrances.py --map-root /path/to/maps
```

Adds four-side road stubs to each city.
