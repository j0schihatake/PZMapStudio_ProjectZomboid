#!/usr/bin/env python3
"""Add practical street furniture to a compiled map, cell by cell.

For each road-adjacent grass square, place a bench every N road tiles and a
lamp/bin near some benches. Headers and buildings are preserved.

Supports resumable and parallel passes so large cities can be processed in
chunks without redoing finished cells.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

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


def process_cell(source_name: str, out_name: str, cx: int, cy: int) -> int:
    source = Path(source_name)
    out = Path(out_name)
    scene = import_pz_region(source, cx * 256, cy * 256, 256, 256,
                             name=f"{source.name} {cx}_{cy}", clean=False,
                             include_buildings=False)
    placed = beautify(scene)
    apply_scene_objects(source, scene, out, cx * 256, cy * 256)
    if not (out / f"{cx}_{cy}.lotheader").exists():
        for name in (f"{cx}_{cy}.lotheader", f"world_{cx}_{cy}.lotpack",
                     f"chunkdata_{cx}_{cy}.bin"):
            source_file = source / name
            if source_file.exists():
                shutil.copy2(source_file, out / name)
    return placed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-map", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--resume", action="store_true",
                        help="skip cells whose output lotheader already exists")
    parser.add_argument("--limit", type=int, default=0,
                        help="process at most this many cells (0 = all)")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    source = Path(args.source_map)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    headers = sorted(source.glob("*.lotheader"))
    if args.resume:
        headers = [h for h in headers if not (out / h.name).exists()]
    if args.limit > 0:
        headers = headers[:args.limit]
    cells = []
    for header in headers:
        parts = header.stem.split("_")
        cells.append((int(parts[-2]), int(parts[-1])))
    print(f"cells: {len(cells)} workers={args.workers}", flush=True)
    total = 0
    if args.workers <= 1:
        for index, (cx, cy) in enumerate(cells, 1):
            total += process_cell(str(source), str(out), cx, cy)
            if index % 20 == 0 or index == len(cells):
                print(f"{index}/{len(cells)} props={total}", flush=True)
    else:
        done = 0
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(process_cell, str(source), str(out), cx, cy)
                       for cx, cy in cells]
            for future in as_completed(futures):
                total += future.result()
                done += 1
                if done % 20 == 0 or done == len(cells):
                    print(f"{done}/{len(cells)} props={total}", flush=True)
    for name in ("map.info", "spawnpoints.lua", "objects.lua", "worldmap.xml",
                 "worldmap-annotations.lua", "worldmap.xml.bin", "streets.xml"):
        if (source / name).exists():
            shutil.copy2(source / name, out / name)
    print(out, "props", total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
