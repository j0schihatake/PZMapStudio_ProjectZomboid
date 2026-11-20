# Compiled Trumbull audit

```bash
python3 tools/trumbull_compiled_audit.py
```

Checks the compiled `Trumbull Valley` cells, not just scene JSON.

Current result:

```text
cells=930 rooms=149 buildings=60
nave 6
altar 2
vestibule 2
lobby 8
courtroom A 4
courtroom B 2
records 2
mill floor 8
loading dock 7
mill office 2
exhibition 6
stalls 9
barn floor 7
warehouse 6
```

All required landmark room types are present. This does not prove visual
fidelity or door/roof gameplay; it proves the compiled room metadata contains
the intended landmarks.

Home bases (SoD-inspired, manual layout):

```text
Pterodactyl Ptark     — Marshall
Tranquility Factory   — Spencer's Mill
Agricultural Complex — Third Town
Fort Marshall        — County Fair
Red Talon FOB        — Rural Fair
```

Each base currently has `compound yard`, `command`, `infirmary`, `barracks`
and `storage` rooms. Fences, gates, parking and rooftop access are next.
