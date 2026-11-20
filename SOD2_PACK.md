# State of Decay 2 optional pack

The six-map base pack already occupies 4069 cells and ~5.7 GB. Do not put all
SoD2 maps into the base item by default.

## Space

Free block starts at `x=110`. Candidate layout on the 300-cell grid:

```text
Trumbull Valley   x=110, y=0
Meagher Valley    x=110, y=30
Drucker County    x=110, y=60
Cascade Hills     x=110, y=90
Providence Ridge  x=110, y=120
```

All use 25x26 cells at 2.0 m/tile and the same room/forest/furniture settings.

## Packaging

Recommended: a separate Workshop item `State of Decay Maps`, containing the
SoD2 maps only. This keeps the base 5.7 GB download unchanged and limits
save-state risk.

If the maps are merged into one item, run a new-save test and check
`map_meta.bin` before publishing; the audit is a conservative upper bound.

No copyrighted State of Decay assets are imported. Layouts are manual
reconstructions inspired by the games.
