# Trumbull Valley — map specification

This is a manual, State of Decay-inspired reconstruction, not an asset import.

## Size and settings

Match the existing city template instead of inventing a smaller map:

```text
tiles:       7500 x 7800
cells:       25 x 26
meters/tile: 2.0
```

Use the same settings as the other city maps:

```text
tree_density         2.2
forest_density       1.8
parking_density      1.5
fill_frontage        1
spawn_density        6
zombies_per_resident 0.8
apartment_chance     0.65
max_levels           9
room_size            24
basement_share       0.25
align_streets        0
forest_seed          2207
```

## Placement

Preferred free block:

```text
x = 110, y = 0
```
```

Check with:

```bash
python3 -m pzmapstudio.cli find-space --map-root <maps> --width 25 --height 26
```

If the save-state audit is over budget, split the map into two city-sized maps
rather than shrinking the tile scale.

## Composition

Trumbull Valley is not one generic town. The layout must contain:

```text
3 towns
2 fairgrounds
rural farms and barns between them
```

### Towns

1. **Marshall** — county seat: courthouse square, church, main street,
   two-storey brick blocks, residential grid.
2. **Spencer's Mill** — river/industrial town: mill, warehouses, silos,
   worker housing, rail spur.
3. **Third town** — southern agricultural town: market street, school,
   clinic, low houses, grain elevator. Final name to be fixed before building.

### Fairs

1. **County Fairground** — large parking, grandstand, exhibition halls,
   livestock barns, fence lines.
2. **Rural market fair** — smaller dirt lot, stalls, pens, trailers, stage.

### Countryside

- farms with farmhouse, barn, silo, fenced fields, windbreak trees;
- highway and county roads connecting all three towns and both fairs;
- river/ravine and forest edges;
- roof access on large civic/industrial buildings;
- practical fences, benches, bins, lamps and story sites.

## Validation

```bash
python3 -m pzmapstudio.cli map-save-audit --map trumbull
python3 -m pzmapstudio.cli audit --scene trumbull.json
```
