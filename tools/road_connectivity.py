#!/usr/bin/env python3
"""Fast road continuity report for adjacent compiled map cells."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.pzlot import read_edge_roads


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-root", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.map_root)
    maps = sorted(p for p in root.iterdir() if p.is_dir())
    edges = {}
    for map_dir in maps:
        for header in map_dir.glob("*.lotheader"):
            p = header.stem.split("_")
            cx, cy = int(p[-2]), int(p[-1])
            for side in ("west", "east", "north", "south"):
                values = read_edge_roads(map_dir, cx, cy, side)
                if values:
                    edges[(map_dir.name, cx, cy, side)] = values
    pairs = []
    for (name, cx, cy, side), left in edges.items():
        neighbor = {"west": (cx - 1, cy), "east": (cx + 1, cy),
                    "north": (cx, cy - 1), "south": (cx, cy + 1)}[side]
        opposite = {"west": "east", "east": "west",
                    "north": "south", "south": "north"}[side]
        for (other, ox, oy, oside), right in edges.items():
            if other != name and (ox, oy) == neighbor and oside == opposite:
                shared = sorted(left & right)
                pairs.append({"a": name, "b": other, "cell": [cx, cy],
                              "side": side, "shared_road_tiles": len(shared),
                              "samples": shared[:8]})
    matches = [p for p in pairs if p["shared_road_tiles"]]
    report = {"boundary_pairs": len(pairs), "matching_pairs": len(matches),
              "pairs": pairs}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"boundary pairs={len(pairs)} matching={len(matches)}")
        for item in matches:
            print(item)
        if not matches:
            print("NO ROAD CONTINUITY FOUND ACROSS MAP BORDERS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
