"""Export a scene as a PZ-oriented bundle and a Tiled preview map."""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

from .scene import Scene


def _spawn_lua(scene: Scene) -> str:
    grouped: dict[str, list] = defaultdict(list)
    for spawn in scene.spawns:
        grouped[spawn.profession or "unemployed"].append(spawn)
    lines = ["function SpawnPoints()", "  return {"]
    for profession, spawns in sorted(grouped.items()):
        lines.append(f"    {profession} = {{")
        for spawn in spawns:
            lines.append(
                f"      {{ posX = {spawn.x}, posY = {spawn.y}, posZ = {spawn.z} }},"
            )
        lines.append("    },")
    lines.extend(["  }", "end", ""])
    return "\n".join(lines)


def _objects_lua(scene: Scene) -> str:
    lines = ["function getObjects()", "  local objects = {}"]
    for building in scene.buildings.values():
        lines.append(
            f"  table.insert(objects, {{name='{building.name}', "
            f"x={building.x}, y={building.y}, w={building.w}, h={building.h}, "
            f"type='Building'}})"
        )
    lines.extend(["  return objects", "end", ""])
    return "\n".join(lines)


def export_bundle(scene: Scene, out_dir: str | Path) -> Path:
    """Write a portable scene bundle.

    It contains the editable scene plus PZ metadata and spawn/object Lua. It is
    not a compiled map; a PZ compiler adapter still has to turn this into lots.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    scene.save(out / "scene.json")
    (out / "map.info").write_text(
        f"title={scene.name}\n"
        "lots=Muldraugh, KY\n"
        "fixed2x=true\n"
        "description=Editable PZMapStudio scene. Terrain cells are not compiled yet.\n",
        encoding="utf-8",
    )
    (out / "spawnpoints.lua").write_text(_spawn_lua(scene), encoding="utf-8")
    (out / "objects.lua").write_text(_objects_lua(scene), encoding="utf-8")
    (out / "pzmapstudio.json").write_text(
        json.dumps({"format": "pzmapstudio-bundle", "version": 1,
                    "stats": scene.stats()}, indent=2),
        encoding="utf-8",
    )
    return out


def export_tmx(scene: Scene, path: str | Path) -> Path:
    """Write a small Tiled TMX preview (not a PZ lot pack)."""
    root = ET.Element("map", {
        "version": "1.10", "tiledversion": "1.10.2",
        "orientation": "orthogonal", "renderorder": "right-down",
        "width": str(scene.width), "height": str(scene.height),
        "tilewidth": "1", "tileheight": "1", "infinite": "0",
    })
    ET.SubElement(root, "tileset", {
        "firstgid": "1", "name": "terrain", "tilewidth": "1",
        "tileheight": "1", "tilecount": "5", "columns": "5",
    })
    layer = ET.SubElement(root, "layer", {
        "id": "1", "name": "terrain", "width": str(scene.width),
        "height": str(scene.height),
    })
    data = ET.SubElement(layer, "data", {"encoding": "csv"})
    palette = {"grass": 1, "forest": 2, "farm": 3, "water": 4, "sand": 5}
    rows = []
    terrain = scene.layers["terrain"]
    for y in range(scene.height):
        row = []
        for x in range(scene.width):
            row.append(str(palette.get(terrain.get((x, y), "grass"), 1)))
        rows.append(",".join(row))
    data.text = ",\n".join(rows)
    objects = ET.SubElement(root, "objectgroup", {"id": "2", "name": "buildings"})
    for building in scene.buildings.values():
        ET.SubElement(objects, "object", {
            "id": str(len(objects) + 1), "name": building.name,
            "x": str(building.x), "y": str(building.y),
            "width": str(building.w), "height": str(building.h),
        })
    spawn_group = ET.SubElement(root, "objectgroup", {"id": "3", "name": "spawns"})
    for spawn in scene.spawns:
        ET.SubElement(spawn_group, "object", {
            "id": str(len(spawn_group) + 1), "name": spawn.profession,
            "x": str(spawn.x), "y": str(spawn.y), "point": "1",
        })
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path
