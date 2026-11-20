#!/usr/bin/env python3
"""Add practical street furniture to a compiled map, cell by cell.

For each road-adjacent grass square, place a bench every N road tiles and a
lamp/bin near some benches. Headers and buildings are preserved.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pzmapstudio.export import apply_scene_objects
from pzmapstudio.scene import Scene, import_pz_region

BENCH = "furniture_seating_outdoor_01_0"
LAMP = "lighting_outdoor_01_0"
BIN = "d_trash_1_0"
BENCH_EVERY = 25
LAMP_EVERY = 75


def beautify(scene: Scene) -> int:
    roads = list(scene.layers.get("roads", {}).keys())
    placed = 0
    occupied = set(scene.layers.get("objects", {}))
    # Road squares in a stable order; place on an adjacent non-road, non-wall tile.
    for index, (x, y) in enumerate(sorted(roads)):
        if index % BENCH_EVERY:
            continue
        candidates = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
        spot = None
        for cx, cy in candidates:
            if not (0 <= cx < scene.width and 0 <= cy < scene.height):
                continue
            if (cx, cy) in roads or (cx, cy) in scene.layers.get("walls", {}):
                continue
            if (cx, cy) in occupied:
                continue
            spot = (cx, cy)
            break
        if spot is None:
            continue
        tile = BENCH if index % LAMP_EVERY else LAMP
        scene.layers["objects"][spot] = tile
        occupied.add(spot)
        placed += 1
        if index % LAMP_EVERY == 0:
            bx, by = spot
            for tx, ty in ((bx + 1, by), (bx - 1, by), (bx, by + 1), (bx, by - 1)):
                if (tx, ty) not in roads and (tx, ty) not in occupied and 0 <= tx < scene.width and 0 <= ty < scene.height:
                    scene.layers["objects"][(tx, ty)] = BIN
                    occupied.add((tx, ty))
                    break
    return placed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-map", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    source = Path(args.source_map)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    headers = sorted(source.glob("*.lotheader"))
    total = 0
    for index, header in enumerate(headers, 1):
        parts = header.stem.split("_")
        cx, cy = int(parts[-2]), int(parts[-1])
        scene = import_pz_region(source, cx * 256, cy * 256, 256, 256,
                                 name=f"{source.name} {cx}_{cy}", clean=False,
                                 include_buildings=False)
        total += beautify(scene)
        apply_scene_objects(source, scene, out, cx * 256, cy * 256)
        if not (out / f"{cx}_{cy}.lotheader").exists():
            for name in (f"{cx}_{cy}.lotheader", f"world_{cx}_{cy}.lotpack",
                         f"chunkdata_{cx}_{cy}.bin"):
                source_file = source / name
                if source_file.exists():
                    shutil.copy2(source_file, out / name)
        if index % 20 == 0 or index == len(headers):
            print(f"{index}/{len(headers)} props={total}")
    for name in ("map.info", "spawnpoints.lua", "objects.lua", "worldmap.xml",
                 "worldmap-annotations.lua", "worldmap.xml.bin", "streets.xml"):
        if (source / name).exists():
            shutil.copy2(source / name, out / name)
    print(out, "props", total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
