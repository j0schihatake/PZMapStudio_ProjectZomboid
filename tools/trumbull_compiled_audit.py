#!/usr/bin/env python3
"""Audit the compiled Trumbull map for required landmark room types."""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.pzlot import read_header_full

REQUIRED = {
    "nave": 1, "altar": 1, "vestibule": 1,
    "lobby": 1, "courtroom A": 1, "courtroom B": 1, "records": 1,
    "mill floor": 1, "loading dock": 1, "mill office": 1,
    "exhibition": 1, "stalls": 1,
    "barn floor": 1, "warehouse": 1,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", default=(
        "/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/"
        "work/KnoxMap-dev/dist/omsk-expansion/common/media/maps/Trumbull Valley"))
    args = parser.parse_args()
    root = Path(args.map)
    counts: Counter[str] = Counter()
    buildings = 0
    cells = 0
    for header in sorted(root.glob("*.lotheader")):
        _h, rooms, bl = read_header_full(header)
        cells += 1
        buildings += len(bl)
        counts.update(name for name, _z, _rects in rooms)
    print(f"cells={cells} rooms={sum(counts.values())} buildings={buildings}")
    missing = []
    for name, minimum in REQUIRED.items():
        have = counts.get(name, 0)
        status = "ok" if have >= minimum else "MISSING"
        print(f"{status:8} {name}: {have}")
        if have < minimum:
            missing.append(name)
    print("room kinds:", ", ".join(sorted(counts)))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
