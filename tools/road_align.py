#!/usr/bin/env python3
"""Copy road edge positions across adjacent map-cell borders."""
from __future__ import annotations

import argparse
import shutil
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.pzlot import read_edge_roads, rewrite_cell

ROAD = "floors_exterior_street_01_16"
SIDES = {"west": (-1, 0), "east": (1, 0), "north": (0, -1), "south": (0, 1)}
OPPOSITE = {"west": "east", "east": "west", "north": "south", "south": "north"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-root", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = Path(args.map_root)
    maps = {p.name: p for p in root.iterdir() if p.is_dir()}
    cell_owner = {}
    for name, path in maps.items():
        for h in path.glob("*.lotheader"):
            p = h.stem.split("_"); cell_owner[(int(p[-2]), int(p[-1]))] = name
    additions: dict[tuple[str, int, int], set[tuple[int, int]]] = defaultdict(set)
    checked = 0
    for (name, cx, cy), owner in list(cell_owner.items()) if False else []:
        pass
    for (cx, cy), name in sorted(cell_owner.items()):
        for side, (dx, dy) in SIDES.items():
            neighbor = (cx + dx, cy + dy)
            if neighbor not in cell_owner:
                continue
            other = cell_owner[neighbor]
            if other == name:
                continue
            checked += 1
            here = read_edge_roads(maps[name], cx, cy, side)
            there = read_edge_roads(maps[other], neighbor[0], neighbor[1], OPPOSITE[side])
            if not here and not there:
                continue
            if here and not there:
                # add matching positions to the other cell's edge
                for pos in here:
                    if side in ("west", "east"):
                        additions[(other, neighbor[0], neighbor[1])].add((255 if OPPOSITE[side] == "east" else 0, pos))
                    else:
                        additions[(other, neighbor[0], neighbor[1])].add((pos, 255 if OPPOSITE[side] == "south" else 0))
            elif there and not here:
                for pos in there:
                    if side in ("west", "east"):
                        additions[(name, cx, cy)].add((255 if side == "east" else 0, pos))
                    else:
                        additions[(name, cx, cy)].add((pos, 255 if side == "south" else 0))
    print(f"checked adjacent pairs={checked} cells_to_patch={len(additions)}")
    if not args.apply:
        for (name, cx, cy), points in additions.items():
            print(name, cx, cy, sorted(points)[:6])
        return 0
    for (name, cx, cy), points in additions.items():
        map_dir = maps[name]
        overrides = {}
        for lx, ly in points:
            for depth in range(8):
                # extend inward from the edge by 8 tiles
                if lx == 255:
                    x = cx * 256 + 255 - depth
                elif lx == 0:
                    x = cx * 256 + depth
                else:
                    x = cx * 256 + lx
                if ly == 255:
                    y = cy * 256 + 255 - depth
                elif ly == 0:
                    y = cy * 256 + depth
                else:
                    y = cy * 256 + ly
                overrides[(x, y, 0)] = [ROAD]
        out = map_dir / ".road_align_tmp"
        if out.exists():
            shutil.rmtree(out)
        rewrite_cell(map_dir, out, cx, cy, overrides)
        for f in (f"{cx}_{cy}.lotheader", f"world_{cx}_{cy}.lotpack"):
            shutil.copy2(out / f, map_dir / f)
        shutil.rmtree(out)
        print("patched", name, cx, cy, len(points))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
