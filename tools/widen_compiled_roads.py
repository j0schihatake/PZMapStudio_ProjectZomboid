#!/usr/bin/env python3
"""Widen already-compiled roads by dilating asphalt into clear neighbours."""
from __future__ import annotations

import argparse
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.pzlot import read_header, read_cell_records, rewrite_cell

ROAD = "floors_exterior_street_01_16"
BLOCK = ("walls_", "floors_interior", "water_", "fixtures_doors")


def is_road(name: str) -> bool:
    n = name.lower()
    return n.startswith(("floors_exterior_street", "blends_street")) or "asphalt" in n


def blocked(name: str) -> bool:
    n = name.lower()
    return any(n.startswith(x) for x in BLOCK)


def work(args):
    root, cx, cy, grow, out_root = args
    p = Path(root)
    if not (p / f"{cx}_{cy}.lotheader").exists():
        return 0
    h = read_header(p / f"{cx}_{cy}.lotheader")
    if not any(is_road(n) for n in h.names):
        return 0
    recs = list(read_cell_records(p, cx, cy))
    by = {(x, y, z): names for x, y, z, _room, names in recs}
    seeds = {(x, y, z) for (x, y, z), names in by.items() if any(is_road(n) for n in names)}
    add = set()
    for x, y, z in seeds:
        for dx in range(-grow, grow + 1):
            for dy in range(-grow, grow + 1):
                k = (x + dx, y + dy, z)
                names = by.get(k)
                if not names:
                    continue
                if any(is_road(n) for n in names):
                    continue
                if any(blocked(n) for n in names):
                    continue
                add.add(k)
    if not add:
        return 0
    overrides = {}
    for k in add:
        kept = [n for n in by[k] if not n.lower().startswith(("blends_", "floors_", "vegetation_", "e_"))]
        overrides[k] = [ROAD] + kept
    out = Path(out_root) / f"{cx}_{cy}"
    if out.exists():
        shutil.rmtree(out)
    rewrite_cell(p, out, cx, cy, overrides)
    for name in (f"{cx}_{cy}.lotheader", f"world_{cx}_{cy}.lotpack"):
        shutil.copy2(out / name, p / name)
    shutil.rmtree(out)
    return len(overrides)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--grow", type=int, default=2)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out-root", default="examples/roadwiden-tmp")
    a = ap.parse_args()
    root = Path(a.map)
    cells = []
    for h in root.glob("*.lotheader"):
        p = h.stem.split("_")
        cells.append((str(root), int(p[-2]), int(p[-1]), a.grow, a.out_root))
    total = 0
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for i, f in enumerate(as_completed([ex.submit(work, c) for c in cells]), 1):
            total += f.result()
            if i % 100 == 0:
                print(f"{i}/{len(cells)} added={total}", flush=True)
    print("added_road_tiles", total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
