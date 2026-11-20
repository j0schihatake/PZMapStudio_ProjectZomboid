# Trumbull building manifest

`trumbull-buildings.json` declares the required landmark footprint for each
district. The validator checks that a building with the exact footprint and
minimum floor count exists in the district scene:

```bash
python3 tools/validate_trumbull_manifest.py
```

Current result:

```text
marshall:       Marshall Courthouse 3 floors
spencers-mill:  Spencer's Mill 3 floors
third-town:     Third Town School 3 floors
county-fair:    County Fair Exhibition Hall 3 floors
rural-fair:     Rural Fair Barn 3 floors
farm:           Farmhouse 3 floors
```

This is a **structural** guarantee: coordinates, footprint and floor count are
checked. It does not yet prove architectural type or visual fidelity. Type,
entrances, roof access and interior layout need per-type builders and a render
review before calling the district finished.
