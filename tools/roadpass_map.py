#!/usr/bin/env python3
"""Run a road/ground cleanup pass over every compiled cell of a PZ map.

    python3 tools/roadpass_map.py --source-map MAP --out OUT [--workers 4]

The original cell headers (rooms, buildings, objects) are copied verbatim. Only
roads/sidewalks that PZMapStudio classified from tiles are rewritten. Cells with
no road changes are copied unchanged.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pzmapstudio.export import apply_scene_roads
from pzmapstudio.scene import import_pz_region


def process_cell(source_name: str, out_name: str, cx: int, cy: int) -> tuple[int, int]:
    source = Path(source_name)
    out = Path(out_name)
    scene = import_pz_region(source, cx * 256, cy * 256, 256, 256,
                             name=f"{source.name} {cx}_{cy}", clean=False,
                             include_buildings=False)
    scene.apply({"op": "clean_roads"})
    apply_scene_roads(source, scene, out, cx * 256, cy * 256)
    if not (out / f"{cx}_{cy}.lotheader").exists():
        for suffix in (".lotheader", ".lotpack"):
            name = (f"{cx}_{cy}" if suffix == ".lotheader" else f"world_{cx}_{cy}") + suffix
            shutil.copy2(source / name, out / name)
    return cx, cy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-map", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--resume", action="store_true",
                        help="skip cells whose output .lotheader already exists")
    args = parser.parse_args()
    source = Path(args.source_map)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    headers = sorted(source.glob("*.lotheader"))
    print(f"cells: {len(headers)} workers={args.workers}")
    cells = []
    for header in headers:
        parts = header.stem.split("_")
        cx, cy = int(parts[-2]), int(parts[-1])
        if args.resume and (out / f"{cx}_{cy}.lotheader").exists():
            continue
        cells.append((cx, cy))
    print(f"todo: {len(cells)}")
    if args.workers <= 1:
        for index, (cx, cy) in enumerate(cells, 1):
            process_cell(str(source), str(out), cx, cy)
            if index % 20 == 0 or index == len(cells):
                print(f"{index}/{len(cells)}")
    else:
        done = 0
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(process_cell, str(source), str(out), cx, cy)
                       for cx, cy in cells]
            for future in as_completed(futures):
                future.result()
                done += 1
                if done % 20 == 0 or done == len(cells):
                    print(f"{done}/{len(cells)}")
    for name in ("map.info", "spawnpoints.lua", "objects.lua", "worldmap.xml",
                 "worldmap-annotations.lua", "worldmap.xml.bin", "streets.xml"):
        if (source / name).exists():
            shutil.copy2(source / name, out / name)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
