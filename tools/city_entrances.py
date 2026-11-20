#!/usr/bin/env python3
"""Add road stubs from all four sides of every compiled map."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.pzlot import rewrite_cell

ROAD = "floors_exterior_street_01_16"


def extents(map_dir: Path) -> tuple[int, int, int, int]:
    cells = []
    for header in map_dir.glob("*.lotheader"):
        p = header.stem.split("_")
        cells.append((int(p[-2]), int(p[-1])))
    return min(x for x, _ in cells), min(y for _, y in cells), max(x for x, _ in cells), max(y for _, y in cells)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-root", required=True)
    args = parser.parse_args()
    root = Path(args.map_root)
    for map_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        x0, y0, x1, y1 = extents(map_dir)
        midx, midy = (x0 + x1) // 2, (y0 + y1) // 2
        cells = {
            (x0, midy): [(x0 * 256 + x, midy * 256 + y, 0) for x in range(0, 80) for y in range(120, 128)],
            (x1, midy): [(x1 * 256 + x, midy * 256 + y, 0) for x in range(176, 256) for y in range(120, 128)],
            (midx, y0): [(midx * 256 + x, y0 * 256 + y, 0) for x in range(120, 128) for y in range(0, 80)],
            (midx, y1): [(midx * 256 + x, y1 * 256 + y, 0) for x in range(120, 128) for y in range(176, 256)],
        }
        for (cx, cy), keys in cells.items():
            if not (map_dir / f"{cx}_{cy}.lotheader").exists():
                continue
            out = map_dir / ".entrance_tmp"
            if out.exists():
                shutil.rmtree(out)
            rewrite_cell(map_dir, out, cx, cy, {k: [ROAD] for k in keys})
            for name in (f"{cx}_{cy}.lotheader", f"world_{cx}_{cy}.lotpack"):
                shutil.copy2(out / name, map_dir / name)
            shutil.rmtree(out)
        print(map_dir.name, "entrances", x0, x1, y0, y1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
