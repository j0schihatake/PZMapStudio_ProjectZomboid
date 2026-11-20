#!/usr/bin/env python3
"""Create the Trumbull Valley layout scene (roads/water/spawns)."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.scene import Scene


def line(scene: Scene, x1: int, y1: int, x2: int, y2: int, width: int,
         tile: str, layer: str = "roads") -> None:
    steps = max(abs(x2 - x1), abs(y2 - y1)) // max(1, width // 2)
    for i in range(steps + 1):
        t = i / max(1, steps)
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        px = max(0, min(scene.width - width, x - width // 2))
        py = max(0, min(scene.height - width, y - width // 2))
        scene.paint(layer, px, py, width, width, tile)


def main() -> int:
    scene = Scene("Trumbull Valley", 7500, 7800)
    # river
    line(scene, 0, 2500, 7500, 3600, 90, "water", "water")
    # highways: Spencer's Mill -> Marshall -> County Fair
    line(scene, 1500, 4200, 3000, 2400, 24, "asphalt")
    line(scene, 3000, 2400, 5600, 1800, 24, "asphalt")
    line(scene, 5600, 1800, 6500, 2600, 20, "asphalt")
    # Marshall -> Third Town
    line(scene, 3000, 2400, 4300, 5700, 20, "asphalt")
    # Third Town -> Rural Fair
    line(scene, 4300, 5700, 5000, 4600, 18, "asphalt")
    # farm access roads
    for (x, y) in [(300, 1600), (1500, 2100), (3000, 4300), (5800, 4100),
                   (6200, 5900), (1800, 6100), (3000, 6600)]:
        line(scene, x + 200, y + 150, x + 200, y - 250, 10, "dirt")
    # town grids
    for cx, cy, blocks in [(2500, 900, 5), (1000, 3600, 4), (4100, 5500, 4)]:
        for i in range(blocks):
            for j in range(blocks):
                x, y = cx + i * 240, cy + j * 240
                scene.paint("roads", x, y, 220, 14, "asphalt")
                scene.paint("roads", x, y, 14, 220, "asphalt")
    # fairs
    for x, y, w, h in [(5000, 1500, 1500, 900), (4500, 4300, 1000, 700)]:
        scene.paint("roads", x, y, w, 14, "asphalt")
        scene.paint("roads", x, y + h - 14, w, 14, "asphalt")
        scene.paint("roads", x, y, 14, h, "asphalt")
        scene.paint("roads", x + w - 14, y, 14, h, "asphalt")
    # spawns
    for x, y in [(3000, 1800), (1800, 4200), (4800, 6100)]:
        scene.apply({"op": "add_spawn", "x": x, "y": y})
    out = Path("examples/trumbull-scene.json")
    out.write_text(json.dumps(scene.to_dict(), indent=1), encoding="utf-8")
    print(out, "roads", len(scene.layers["roads"]), "water", len(scene.layers["water"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
