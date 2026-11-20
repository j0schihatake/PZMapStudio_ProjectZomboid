#!/usr/bin/env python3
"""Build one Trumbull Valley district as a small, fast scene."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.scene import Scene

DISTRICTS = {
    "marshall": (1800, 1600, 4, 3),
    "spencers-mill": (1600, 1500, 3, 3),
    "third-town": (1700, 1500, 3, 3),
    "county-fair": (1500, 1100, 2, 2),
    "rural-fair": (1200, 900, 2, 2),
    "farm": (900, 800, 1, 1),
}


def house(scene, x, y, w, h, floors=2, rooms=5, furnish=True):
    scene.apply({"op": "build_house", "x": x, "y": y, "w": w, "h": h,
                 "floors": floors, "rooms": rooms, "furnish": furnish})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--district", required=True, choices=sorted(DISTRICTS))
    args = parser.parse_args()
    width, height, blocks_x, blocks_y = DISTRICTS[args.district]
    scene = Scene(f"Trumbull {args.district}", width, height)
    for i in range(blocks_x + 1):
        for y in range(0, height, 220):
            scene.paint("roads", i * 300, y, 16, min(220, height - y), "asphalt")
    for j in range(blocks_y + 1):
        for x in range(0, width, 300):
            scene.paint("roads", x, j * 260, min(300, width - x), 16, "asphalt")
    for i in range(blocks_x):
        for j in range(blocks_y):
            scene.paint("sidewalks", i * 300 + 16, j * 260 + 16, 284, 244, "pavement")
            house(scene, i * 300 + 40, j * 260 + 40, 112, 92)
            house(scene, i * 300 + 168, j * 260 + 40, 100, 92, rooms=4)
            house(scene, i * 300 + 40, j * 260 + 148, 100, 82, rooms=4)
            house(scene, i * 300 + 168, j * 260 + 148, 112, 82, rooms=4)
    # district landmark
    house(scene, 40, 40, 220, 160, floors=3, rooms=8)
    scene.apply({"op": "add_spawn", "x": width // 2, "y": height // 2})
    out = Path("examples") / f"trumbull-{args.district}.json"
    out.write_text(json.dumps(scene.to_dict(), indent=1), encoding="utf-8")
    print(out, "buildings", len(scene.buildings), "roads", len(scene.layers["roads"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
