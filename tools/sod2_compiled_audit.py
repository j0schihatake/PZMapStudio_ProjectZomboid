#!/usr/bin/env python3
"""Audit compiled SoD2-inspired maps for base/landmark rooms."""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.pzlot import read_header_full

REQUIRED = {"compound yard", "command", "infirmary", "barracks", "storage"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-root", default=(
        "/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/"
        "KnoxMap-dev/dist/sod2-expansion/common/media/maps"))
    args = parser.parse_args()
    root = Path(args.map_root)
    missing_total = 0
    for map_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        counts: Counter[str] = Counter()
        buildings = cells = 0
        for header in map_dir.glob("*.lotheader"):
            _h, rooms, bl = read_header_full(header)
            cells += 1
            buildings += len(bl)
            counts.update(name for name, _z, _rects in rooms)
        missing = sorted(REQUIRED - set(counts))
        print(f"{map_dir.name}: cells={cells} buildings={buildings} rooms={sum(counts.values())}")
        print("  bases:", {k: counts[k] for k in ("compound yard", "command", "infirmary", "barracks", "storage")})
        if missing:
            print("  MISSING:", missing)
            missing_total += len(missing)
    return 1 if missing_total else 0


if __name__ == "__main__":
    raise SystemExit(main())
