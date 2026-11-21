#!/usr/bin/env python3
"""Remove grass/bush overlays from squares that are roads."""
from __future__ import annotations

import argparse
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.pzlot import read_header, read_cell_records, rewrite_cell

ROAD = ("street", "road", "asphalt")
VEG = ("blends_natural", "blends_grassoverlays", "grass", "bush", "tree",
       "vegetation", "e_")


def is_road(name: str) -> bool:
    n = name.lower()
    return any(x in n for x in ROAD)


def is_veg(name: str) -> bool:
    n = name.lower()
    return any(x in n for x in VEG)


def clean_cell(map_name, cx, cy, out_root):
    map_dir = Path(map_name)
    header = read_header(map_dir / f"{cx}_{cy}.lotheader")
    if not any(is_road(n) for n in header.names):
        return 0
    records = list(read_cell_records(map_dir, cx, cy))
    overrides = {}
    removed = 0
    for x, y, z, _room, names in records:
        if not any(is_road(n) for n in names):
            continue
        kept = [n for n in names if not is_veg(n)]
        if len(kept) != len(names) and any(is_road(n) for n in kept):
            overrides[(x, y, z)] = kept
            removed += len(names) - len(kept)
    if not overrides:
        return 0
    out = Path(out_root) / f"{cx}_{cy}"
    if out.exists(): shutil.rmtree(out)
    rewrite_cell(map_dir, out, cx, cy, overrides)
    for name in (f"{cx}_{cy}.lotheader", f"world_{cx}_{cy}.lotpack"):
        shutil.copy2(out / name, map_dir / name)
    shutil.rmtree(out)
    return removed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out-root", default="examples/roadveg-tmp")
    args = parser.parse_args()
    map_dir = Path(args.map)
    cells=[]
    for h in map_dir.glob("*.lotheader"):
        p=h.stem.split("_"); cells.append((int(p[-2]),int(p[-1])))
    total=0
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(clean_cell,str(map_dir),cx,cy,args.out_root) for cx,cy in cells]
        for i,f in enumerate(as_completed(futures),1):
            total+=f.result()
            if i%100==0: print(f"{i}/{len(cells)} removed={total}",flush=True)
    print("removed_vegetation_tiles",total)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
