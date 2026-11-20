#!/usr/bin/env python3
"""Run a road/ground cleanup pass over every compiled cell of a PZ map.

    python3 tools/roadpass_map.py --source-map MAP --out OUT

The original cell headers (rooms, buildings, objects) are copied verbatim. Only
roads/sidewalks that PZMapStudio classified from tiles are rewritten. Cells with
no road changes are copied unchanged.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pzmapstudio.export import apply_scene_roads
from pzmapstudio.scene import import_pz_region


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-map", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    source = Path(args.source_map)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    headers = sorted(source.glob("*.lotheader"))
    print(f"cells: {len(headers)}")
    for index, header in enumerate(headers, 1):
        parts = header.stem.split("_")
        cx, cy = int(parts[-2]), int(parts[-1])
        scene = import_pz_region(source, cx * 256, cy * 256, 256, 256,
                                 name=f"{source.name} {cx}_{cy}", clean=True)
        scene.apply({"op": "clean_roads"})
        # Rewrite to a temporary per-cell folder, then copy the cell over.
        before = set(out.glob("*"))
        apply_scene_roads(source, scene, out, cx * 256, cy * 256)
        generated = {p for p in out.glob("*") if p.suffix in (".lotheader", ".lotpack")}
        if not (out / f"{cx}_{cy}.lotheader").exists():
            for suffix in (".lotheader", ".lotpack"):
                name = (f"{cx}_{cy}" if suffix == ".lotheader" else f"world_{cx}_{cy}") + suffix
                shutil.copy2(source / name, out / name)
        if index % 20 == 0 or index == len(headers):
            print(f"{index}/{len(headers)}")
    for name in ("map.info", "spawnpoints.lua", "objects.lua", "worldmap.xml",
                 "worldmap-annotations.lua", "worldmap.xml.bin", "streets.xml"):
        if (source / name).exists():
            shutil.copy2(source / name, out / name)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
