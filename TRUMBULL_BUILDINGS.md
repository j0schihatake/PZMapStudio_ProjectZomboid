# Trumbull building manifest

`trumbull-buildings.json` is the source of truth for required buildings.

Each entry has:

```text
name, kind, type, x, y, w, h, floors, rooms, roof_access
```

`tools/build_trumbull_district.py` reads the manifest and calls
`build_typed` for every required building. It does **not** fill the district
with anonymous houses first.

`tools/validate_trumbull_manifest.py` checks each district scene for:

- exact footprint x/y/w/h;
- exact building name;
- building id kind prefix (`courthouse-`, `church-`, `school-`, ...);
- minimum floor count.

Current result:

```text
Marshall: Courthouse, Church, School, Clinic, Shop
Spencer's Mill: Mill, Warehouse, Worker Housing, Shop
Third Town: School, Clinic, Market, Church
County Fair: Exhibition Hall, Barn, Shop
Rural Fair: Hall, Barn
Farm: Farmhouse, Barn, Shed
```

This guarantees placement and type label. It still does not guarantee visual
fidelity or working entrances/roof access; those need game validation.
