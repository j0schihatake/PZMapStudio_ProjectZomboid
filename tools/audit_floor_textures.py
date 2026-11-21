#!/usr/bin/env python3
"""Find object-only squares with no ground/floor texture beneath them."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.pzlot import read_cell_records, read_header

GROUND = ("floors_", "blends_", "terrain_", "water_")


def is_ground(name: str) -> bool:
    return name.startswith(GROUND)


def scan_cell(args):
    path, cx, cy = args
    p = Path(path)
    h = p / f"{cx}_{cy}.lotheader"
    if not h.exists():
        return 0, []
    header = read_header(h)
    if not any(not is_ground(n) for n in header.names):
        return 0, []
    missing = 0
    samples = []
    for x, y, z, room, names in read_cell_records(p, cx, cy):
        if room <= 0:
            continue
        if all(n.startswith(("walls_", "fixtures_doors", "fixtures_stairs_")) for n in names):
            continue
        if not any(is_ground(n) for n in names):
            missing += 1
            if len(samples) < 3:
                samples.append([x, y, z, names[:6]])
    return missing, samples


def scan_map(root: Path, workers: int):
    cells = []
    for h in root.glob("*.lotheader"):
        p = h.stem.split("_")
        cells.append((str(root), int(p[-2]), int(p[-1])))
    total = 0
    samples = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(scan_cell, c) for c in cells]
        for i, f in enumerate(as_completed(futures), 1):
            n, s = f.result()
            total += n
            samples.extend(s)
            if i % 500 == 0:
                print(f"{root.name}: {i}/{len(cells)} missing={total}", flush=True)
    return {"map": str(root), "cells": len(cells), "missing": total, "samples": samples[:10]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps-root", required=True)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--out", default="examples/floor-audit.json")
    args = ap.parse_args()
    roots = [p for p in Path(args.maps_root).iterdir() if p.is_dir() and list(p.glob("*.lotheader"))]
    report = []
    for root in roots:
        print("===", root, flush=True)
        report.append(scan_map(root, args.workers))
    Path(args.out).write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
