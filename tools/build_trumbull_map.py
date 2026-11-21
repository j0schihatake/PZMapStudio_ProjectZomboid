#!/usr/bin/env python3
"""Merge Trumbull district scenes into one 7500x7800 map scene."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.scene import Scene

OFFSETS = {
    "marshall": (2200, 700),
    "spencers-mill": (800, 3500),
    "third-town": (4000, 5400),
    "county-fair": (5000, 1500),
    "rural-fair": (4500, 4300),
    "farm": (6200, 5900),
}


def road(dst: Scene, x1: int, y1: int, x2: int, y2: int, width: int = 48) -> None:
    steps = max(abs(x2 - x1), abs(y2 - y1)) // max(1, width // 2)
    for i in range(steps + 1):
        t = i / max(1, steps)
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        px = max(0, min(dst.width - width, x - width // 2))
        py = max(0, min(dst.height - width, y - width // 2))
        dst.paint("roads", px, py, width, width, "asphalt")


def merge_layer(dst: Scene, src: Scene, dx: int, dy: int, layer: str) -> None:
    for (x, y), tile in src.layers.get(layer, {}).items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < dst.width and 0 <= ny < dst.height:
            dst.layers[layer][(nx, ny)] = tile


def main() -> int:
    scene = Scene("Trumbull Valley", 7500, 7800)
    for name, (dx, dy) in OFFSETS.items():
        path = Path("examples") / f"trumbull-{name}.json"
        data = json.loads(path.read_text())
        src = Scene.from_dict(data)
        for layer in src.layers:
            merge_layer(scene, src, dx, dy, layer)
        for building in src.buildings.values():
            building.id = f"{name}-{building.id}"
            building.x += dx
            building.y += dy
            for floor in building.floors.values():
                for room in floor.rooms:
                    room.x += dx
                    room.y += dy
                for item in floor.furniture:
                    item.x += dx
                    item.y += dy
            scene.buildings[building.id] = building
        for spawn in src.spawns:
            scene.spawns.append(type(spawn)(x=spawn.x + dx, y=spawn.y + dy))
    # global highway and district connectors
    road(scene, 0, 220, 7500, 220)
    for x, y in [(800, 3500), (2200, 700), (4000, 5400), (5000, 1500), (4500, 4300), (6200, 5900)]:
        road(scene, x, 220, x, y)
    out = Path("examples/trumbull-map.json")
    out.write_text(json.dumps(scene.to_dict(), indent=1), encoding="utf-8")
    print(out, "buildings", len(scene.buildings), "spawns", len(scene.spawns))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
