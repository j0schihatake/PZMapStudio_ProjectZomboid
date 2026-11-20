# Trumbull Valley compiled map

Pipeline:

```bash
python3 tools/build_trumbull_district.py --district marshall
python3 tools/build_trumbull_district.py --district spencers-mill
python3 tools/build_trumbull_district.py --district third-town
python3 tools/build_trumbull_district.py --district county-fair
python3 tools/build_trumbull_district.py --district rural-fair
python3 tools/build_trumbull_district.py --district farm
python3 tools/build_trumbull_map.py
python3 -m pzmapstudio.cli export-worlded-map \
  --scene examples/trumbull-map.json \
  --out examples/trumbull-export \
  --cell-x 110 --cell-y 0
```

The districts are merged with:

```text
Marshall        (2200, 700)
Spencer's Mill  (800, 3500)
Third Town      (4000, 5400)
County Fair     (5000, 1500)
Rural Fair      (4500, 4300)
Farm            (6200, 5900)
```

The compiled map is 30x31 cells at origin `x=110, y=0`.

Rooms/buildings are written by the experimental `worlded` bridge. Wall/door
orientation and interior visuals still need a game test.
