"""Sparse, command-driven map scene.

The scene is deliberately independent of Project Zomboid's binary lot format.
It stores tiles, buildings, furniture and spawn markers as plain data, so an
agent can edit it through JSON commands and a UI can render the same state.
"""
from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

LAYERS = ("terrain", "roads", "water", "floors", "walls", "objects", "zones")


class SceneError(ValueError):
    pass


@dataclass
class Furniture:
    kind: str
    x: int
    y: int
    z: int = 0
    rotation: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "x": self.x, "y": self.y, "z": self.z,
                "rotation": self.rotation}


@dataclass
class Room:
    x: int
    y: int
    w: int
    h: int
    kind: str = "room"

    def to_dict(self) -> dict[str, Any]:
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h, "kind": self.kind}


@dataclass
class Floor:
    z: int
    rooms: list[Room] = field(default_factory=list)
    furniture: list[Furniture] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"z": self.z, "rooms": [r.to_dict() for r in self.rooms],
                "furniture": [f.to_dict() for f in self.furniture]}


@dataclass
class Building:
    id: str
    name: str
    x: int
    y: int
    w: int
    h: int
    floors: dict[int, Floor] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "x": self.x, "y": self.y,
            "w": self.w, "h": self.h,
            "floors": {str(k): v.to_dict() for k, v in sorted(self.floors.items())},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Building":
        floors = {}
        for key, value in data.get("floors", {}).items():
            floor = Floor(z=int(value.get("z", key)))
            floor.rooms = [Room(**room) for room in value.get("rooms", [])]
            floor.furniture = [Furniture(**item) for item in value.get("furniture", [])]
            floors[floor.z] = floor
        return cls(
            id=str(data["id"]), name=str(data.get("name", data["id"])),
            x=int(data["x"]), y=int(data["y"]), w=int(data["w"]), h=int(data["h"]),
            floors=floors,
        )


@dataclass
class Spawn:
    x: int
    y: int
    z: int = 0
    profession: str = "unemployed"

    def to_dict(self) -> dict[str, Any]:
        return {"x": self.x, "y": self.y, "z": self.z,
                "profession": self.profession}


class Scene:
    """Editable map scene with undo/redo."""

    def __init__(self, name: str = "Untitled", width: int = 512, height: int = 512):
        if width <= 0 or height <= 0:
            raise SceneError("width and height must be positive")
        self.name = name
        self.width = int(width)
        self.height = int(height)
        self.layers: dict[str, dict[tuple[int, int], str]] = {name: {} for name in LAYERS}
        self.buildings: dict[str, Building] = {}
        self.spawns: list[Spawn] = []
        self._history: list[str] = []
        self._redo: list[str] = []

    # ------------------------------------------------------------------ state
    def to_dict(self) -> dict[str, Any]:
        return {
            "version": 1,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "layers": {
                name: [{"x": x, "y": y, "tile": tile}
                       for (x, y), tile in sorted(cells.items())]
                for name, cells in self.layers.items()
            },
            "buildings": [b.to_dict() for b in self.buildings.values()],
            "spawns": [s.to_dict() for s in self.spawns],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Scene":
        scene = cls(
            name=str(data.get("name", "Untitled")),
            width=int(data.get("width", 512)),
            height=int(data.get("height", 512)),
        )
        for layer, cells in data.get("layers", {}).items():
            if layer not in scene.layers:
                scene.layers[layer] = {}
            for item in cells:
                scene.layers[layer][(int(item["x"]), int(item["y"]))] = str(item["tile"])
        scene.buildings = {
            str(item["id"]): Building.from_dict(item)
            for item in data.get("buildings", [])
        }
        scene.spawns = [Spawn(**item) for item in data.get("spawns", [])]
        scene._history = []
        scene._redo = []
        return scene

    def check_rect(self, x: int, y: int, w: int, h: int) -> None:
        if w <= 0 or h <= 0:
            raise SceneError("rectangle must have positive width and height")
        if x < 0 or y < 0 or x + w > self.width or y + h > self.height:
            raise SceneError(
                f"rectangle {x},{y},{w},{h} is outside scene {self.width}x{self.height}"
            )

    # --------------------------------------------------------------- commands
    def apply(self, command: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(command, dict) or "op" not in command:
            raise SceneError("command must be an object with an 'op' field")
        before = json.dumps(self.to_dict(), sort_keys=True)
        op = str(command["op"])
        result: dict[str, Any] = {"op": op, "ok": True}

        if op == "paint":
            result.update(self.paint(
                layer=str(command.get("layer", "terrain")),
                x=int(command["x"]), y=int(command["y"]),
                w=int(command["w"]), h=int(command["h"]),
                tile=str(command["tile"]),
            ))
        elif op == "erase":
            result.update(self.erase(
                layer=str(command.get("layer", "terrain")),
                x=int(command["x"]), y=int(command["y"]),
                w=int(command["w"]), h=int(command["h"]),
            ))
        elif op == "build_house":
            result.update(self.build_house(
                x=int(command["x"]), y=int(command["y"]),
                w=int(command["w"]), h=int(command["h"]),
                floors=int(command.get("floors", 1)),
                rooms=int(command.get("rooms", 4)),
                furnish=bool(command.get("furnish", True)),
                name=str(command.get("name", "")),
            ))
        elif op == "add_floor":
            result.update(self.add_floor(str(command["building"]), int(command["z"]),
                                         int(command.get("rooms", 4)),
                                         bool(command.get("furnish", True))))
        elif op == "place_furniture":
            result.update(self.place_furniture(
                str(command["building"]), int(command["x"]), int(command["y"]),
                int(command.get("z", 0)), str(command.get("kind", "chair")),
            ))
        elif op == "add_spawn":
            result.update(self.add_spawn(int(command["x"]), int(command["y"]),
                                         int(command.get("z", 0)),
                                         str(command.get("profession", "unemployed"))))
        elif op == "remove_spawn":
            result.update(self.remove_spawn(int(command["index"])))
        elif op == "undo":
            result.update(self.undo())
        elif op == "redo":
            result.update(self.redo())
        else:
            raise SceneError(f"unknown op: {op}")

        if op not in ("undo", "redo") and isinstance(result, dict):
            self._history.append(before)
            if len(self._history) > 100:
                self._history.pop(0)
            self._redo.clear()
        return result

    def apply_batch(self, commands: list[dict[str, Any]]) -> dict[str, Any]:
        """Apply commands atomically: on error the scene is restored."""
        before = json.dumps(self.to_dict(), sort_keys=True)
        results = []
        try:
            for index, command in enumerate(commands):
                results.append({"index": index, "result": self.apply(command)})
        except Exception:
            restored = Scene.from_dict(json.loads(before))
            history, redo = self._history, self._redo
            self.__dict__.update(restored.__dict__)
            self._history, self._redo = history, redo
            raise
        return {"applied": len(results), "results": results}

    def paint(self, layer: str, x: int, y: int, w: int, h: int, tile: str) -> dict[str, Any]:
        if layer not in self.layers:
            raise SceneError(f"unknown layer: {layer}")
        self.check_rect(x, y, w, h)
        cells = self.layers[layer]
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                cells[(xx, yy)] = tile
        return {"painted": w * h, "layer": layer}

    def erase(self, layer: str, x: int, y: int, w: int, h: int) -> dict[str, Any]:
        if layer not in self.layers:
            raise SceneError(f"unknown layer: {layer}")
        self.check_rect(x, y, w, h)
        cells = self.layers[layer]
        removed = 0
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if (xx, yy) in cells:
                    del cells[(xx, yy)]
                    removed += 1
        return {"erased": removed, "layer": layer}

    def build_house(self, x: int, y: int, w: int, h: int, floors: int = 1,
                    rooms: int = 4, furnish: bool = True, name: str = "") -> dict[str, Any]:
        self.check_rect(x, y, w, h)
        if floors < 1 or floors > 32:
            raise SceneError("floors must be between 1 and 32")
        if w < 6 or h < 6:
            raise SceneError("a house needs at least 6x6 tiles")
        building_id = f"house-{len(self.buildings) + 1}"
        building = Building(
            id=building_id, name=name or building_id,
            x=x, y=y, w=w, h=h,
        )
        for z in range(floors):
            self._add_floor(building, z, rooms, furnish)
        self.buildings[building_id] = building
        self.layers["objects"][(x + w // 2, y + h // 2)] = f"building:{building_id}"
        return {"building": building_id, "floors": floors,
                "furniture": sum(len(f.furniture) for f in building.floors.values())}

    def add_floor(self, building_id: str, z: int, rooms: int = 4,
                  furnish: bool = True) -> dict[str, Any]:
        building = self.buildings.get(building_id)
        if building is None:
            raise SceneError(f"unknown building: {building_id}")
        if z in building.floors:
            raise SceneError(f"floor {z} already exists in {building_id}")
        self._add_floor(building, int(z), int(rooms), bool(furnish))
        return {"building": building_id, "z": int(z),
                "rooms": len(building.floors[int(z)].rooms)}

    def _add_floor(self, building: Building, z: int, rooms: int, furnish: bool) -> None:
        floor = Floor(z=z)
        rooms = max(1, int(rooms))
        room_w = max(2, building.w // 2)
        room_h = max(2, building.h // 2)
        count = 0
        for ry in range(building.y, building.y + building.h - 2, room_h):
            for rx in range(building.x, building.x + building.w - 2, room_w):
                if count >= rooms:
                    break
                floor.rooms.append(Room(rx, ry, room_w, room_h))
                count += 1
            if count >= rooms:
                break
        if furnish:
            for index, room in enumerate(floor.rooms):
                kinds = ["bed", "table", "chair", "kitchen", "lamp"]
                kind = kinds[index % len(kinds)]
                fx = max(room.x, min(room.x + room.w - 1, room.x + 1))
                fy = max(room.y, min(room.y + room.h - 1, room.y + 1))
                floor.furniture.append(Furniture(kind=kind, x=fx, y=fy, z=z))
        building.floors[z] = floor

    def place_furniture(self, building_id: str, x: int, y: int, z: int = 0,
                        kind: str = "chair") -> dict[str, Any]:
        building = self.buildings.get(building_id)
        if building is None:
            raise SceneError(f"unknown building: {building_id}")
        if z not in building.floors:
            raise SceneError(f"floor {z} does not exist in {building_id}")
        if not (building.x <= x < building.x + building.w and
                building.y <= y < building.y + building.h):
            raise SceneError("furniture must be inside the building footprint")
        furniture = Furniture(kind=kind, x=x, y=y, z=z)
        building.floors[z].furniture.append(furniture)
        return {"placed": kind, "x": x, "y": y, "z": z}

    def add_spawn(self, x: int, y: int, z: int = 0,
                  profession: str = "unemployed") -> dict[str, Any]:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise SceneError("spawn is outside the scene")
        self.spawns.append(Spawn(x=x, y=y, z=z, profession=profession))
        return {"spawn": len(self.spawns) - 1, "x": x, "y": y, "z": z}

    def remove_spawn(self, index: int) -> dict[str, Any]:
        if not (0 <= index < len(self.spawns)):
            raise SceneError("spawn index out of range")
        del self.spawns[index]
        return {"removed": index}

    def undo(self) -> dict[str, Any]:
        if not self._history:
            raise SceneError("nothing to undo")
        current = json.dumps(self.to_dict(), sort_keys=True)
        previous = self._history.pop()
        self._redo.append(current)
        restored = Scene.from_dict(json.loads(previous))
        history, redo = self._history, self._redo
        self.__dict__.update(restored.__dict__)
        self._history, self._redo = history, redo
        return {"undone": True}

    def redo(self) -> dict[str, Any]:
        if not self._redo:
            raise SceneError("nothing to redo")
        target = self._redo.pop()
        self._history.append(json.dumps(self.to_dict(), sort_keys=True))
        restored = Scene.from_dict(json.loads(target))
        history, redo = self._history, self._redo
        self.__dict__.update(restored.__dict__)
        self._history, self._redo = history, redo
        return {"redone": True}

    # --------------------------------------------------------------- persistence
    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: str | Path) -> "Scene":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def stats(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "layers": {k: len(v) for k, v in self.layers.items()},
            "buildings": len(self.buildings),
            "floors": sum(len(b.floors) for b in self.buildings.values()),
            "furniture": sum(len(f.furniture) for b in self.buildings.values()
                             for f in b.floors.values()),
            "spawns": len(self.spawns),
        }


def parse_spawnpoints(text: str) -> list[tuple[int, int, int]]:
    positions = []
    for x, y, z in re.findall(
            r"posX\s*=\s*(-?\d+)\s*,\s*posY\s*=\s*(-?\d+)\s*,\s*posZ\s*=\s*(-?\d+)",
            text):
        positions.append((int(x), int(y), int(z)))
    return positions


def import_pz_map(map_dir: str | Path, name: str | None = None) -> Scene:
    """Create an editable overlay from a compiled PZ map folder.

    Cell files are named by absolute 256-tile coordinates; their maximum gives
    the scene bounds. Spawn points and their Lua positions are imported. The
    compiled terrain itself is not decoded yet.
    """
    path = Path(map_dir)
    cells = []
    for header in path.glob("*.lotheader"):
        parts = header.stem.split("_")
        try:
            cells.append((int(parts[-2]), int(parts[-1])))
        except (ValueError, IndexError):
            continue
    if not cells:
        raise SceneError(f"no .lotheader files in {path}")
    width = (max(x for x, _ in cells) + 1) * 256
    height = (max(y for _, y in cells) + 1) * 256
    title = path.name
    info = path / "map.info"
    if info.exists():
        for line in info.read_text(errors="ignore").splitlines():
            if line.startswith("title="):
                title = line.split("=", 1)[1].strip()
                break
    scene = Scene(name=name or title, width=width, height=height)
    spawn_file = path / "spawnpoints.lua"
    if spawn_file.exists():
        for x, y, z in parse_spawnpoints(spawn_file.read_text(errors="ignore")):
            if 0 <= x < width and 0 <= y < height:
                scene.spawns.append(Spawn(x=x, y=y, z=z))
    return scene


def import_knoxmap(pzw_path: str | Path, spawnpoints_path: str | Path | None = None,
                   name: str | None = None) -> Scene:
    """Create an editable overlay for a KnoxMap .pzw project.

    World dimensions are in 300-tile cells in the PZW. The compiled map is
    larger than that in places, but the project dimensions are the best available
    origin for an overlay.
    """
    import xml.etree.ElementTree as ET
    root = ET.parse(pzw_path).getroot()
    width = int(root.attrib.get("width", "1")) * 300
    height = int(root.attrib.get("height", "1")) * 300
    scene = Scene(name=name or Path(pzw_path).stem, width=width, height=height)
    if spawnpoints_path and Path(spawnpoints_path).exists():
        for x, y, z in parse_spawnpoints(Path(spawnpoints_path).read_text(encoding="utf-8")):
            if 0 <= x < width and 0 <= y < height:
                scene.spawns.append(Spawn(x=x, y=y, z=z))
    return scene
