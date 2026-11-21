#!/usr/bin/env python3
"""Restore a ground tile under object-only props using neighbours."""
from __future__ import annotations

import argparse
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.pzlot import read_header, read_cell_records, rewrite_cell

PROPS = {"furniture_seating_outdoor_01_0", "lighting_outdoor_01_0",
         "d_trash_1_0", "fencing_01_0", "fixtures_doors_fences_01_17"}
FALLBACK = "floors_exterior_natural_01_16"


def ground_for(x, y, z, names_by_key):
    for radius in (1, 2, 3, 5):
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                other = names_by_key.get((x + dx, y + dy, z))
                if not other:
                    continue
                ground = [n for n in other if n not in PROPS]
                if ground:
                    return ground
    return [FALLBACK]


def repair_cell(map_name, cell_x, cell_y, out_root):
    map_dir = Path(map_name)
    header = read_header(map_dir / f"{cell_x}_{cell_y}.lotheader")
    if not any(name in PROPS for name in header.names):
        return 0, 0
    records = list(read_cell_records(map_dir, cell_x, cell_y))
    names_by_key = {(x, y, z): names for x, y, z, _room, names in records}
    overrides = {}
    holes = 0
    for x, y, z, _room, names in records:
        if not any(n in PROPS for n in names):
            continue
        if any(n not in PROPS for n in names):
            continue
        ground = ground_for(x, y, z, names_by_key)
        merged = []
        for n in ground + names:
            if n not in merged:
                merged.append(n)
        overrides[(x, y, z)] = merged
        holes += 1
    if not overrides:
        return 0, 0
    out = Path(out_root) / f"{cell_x}_{cell_y}"
    if out.exists():
        shutil.rmtree(out)
    rewrite_cell(map_dir, out, cell_x, cell_y, overrides)
    for name in (f"{cell_x}_{cell_y}.lotheader", f"world_{cell_x}_{cell_y}.lotpack"):
        shutil.copy2(out / name, map_dir / name)
    shutil.rmtree(out)
    return 1, holes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--out-root", default="examples/ground-tmp")
    args = parser.parse_args()
    map_dir = Path(args.map)
    cells = []
    for h in map_dir.glob("*.lotheader"):
        p = h.stem.split("_"); cells.append((int(p[-2]), int(p[-1])))
    total_cells = total_holes = 0
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(repair_cell, str(map_dir), cx, cy, args.out_root)
                   for cx, cy in cells]
        for i, future in enumerate(as_completed(futures), 1):
            c, h = future.result()
            total_cells += c; total_holes += h
            if i % 50 == 0:
                print(f"{i}/{len(cells)} cells_with_props={total_cells} holes={total_holes}", flush=True)
    print("repaired_cells", total_cells, "holes", total_holes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
