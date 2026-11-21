"""Hand-authored hero compounds: military bases and prisons."""
from __future__ import annotations

from .scene import Scene


def fence_rect(scene: Scene, x: int, y: int, w: int, h: int, gate: bool = True) -> None:
    scene.add_fence(x, y, w, axis="x", kind="metal", gate=gate)
    scene.add_fence(x, y + h - 1, w, axis="x", kind="metal", gate=gate)
    scene.add_fence(x, y, h, axis="y", kind="metal", gate=gate)
    scene.add_fence(x + w - 1, y, h, axis="y", kind="metal", gate=gate)


def key_room(scene: Scene, result: dict, kind: str) -> None:
    building = scene.buildings[result["building"]]
    floor = building.floors[min(building.floors)]
    if floor.rooms:
        floor.rooms[0].kind = kind


def watchtower(scene: Scene, x: int, y: int, name: str) -> None:
    result = scene.build_house(x, y, 18, 18, floors=1, rooms=1, furnish=False, name=name)
    key_room(scene, result, "watchtower")


def military_base(scene: Scene, x: int, y: int, w: int, h: int, name: str) -> None:
    """A fenced compound with command, barracks, armory and vehicle yard."""
    fence_rect(scene, x, y, w, h)
    scene.paint("sidewalks", x + 40, y + 40, w - 80, h - 80, "sidewalk")
    command = scene.build_typed(
        "base", x + 100, y + 100, w - 500, h - 300, floors=1, name=f"{name} Command"
    )
    key_room(scene, command, "command")
    barracks = scene.build_house(
        x + w - 360, y + 120, 260, 150, floors=1, rooms=3,
        name=f"{name} Barracks",
    )
    key_room(scene, barracks, "barracks")
    armory = scene.build_typed(
        "warehouse", x + w - 400, y + h - 260, 320, 180, floors=1,
        name=f"{name} Armory",
    )
    key_room(scene, armory, "armory")
    watchtower(scene, x + 20, y + 20, f"{name} Watchtower NW")
    watchtower(scene, x + w - 40, y + 20, f"{name} Watchtower NE")
    watchtower(scene, x + 20, y + h - 40, f"{name} Watchtower SW")
    watchtower(scene, x + w - 40, y + h - 40, f"{name} Watchtower SE")
    scene.add_road(x + w // 2 - 32, y + h, 64, 260)


def prison(scene: Scene, x: int, y: int, w: int, h: int, name: str) -> None:
    """A walled prison with gatehouse, cellblocks, yard and admin."""
    fence_rect(scene, x, y, w, h)
    scene.paint("sidewalks", x + 50, y + 50, w - 100, h - 100, "sidewalk")
    gatehouse = scene.build_typed(
        "warehouse", x + w // 2 - 110, y + 30, 220, 140, floors=1,
        name=f"{name} Gatehouse",
    )
    key_room(scene, gatehouse, "gatehouse")
    for i in range(3):
        cx = x + 90 + i * (w - 180) // 3
        cellblock = scene.build_house(
            cx, y + 220, (w - 240) // 3, 150, floors=1, rooms=4,
            name=f"{name} Cellblock {i + 1}",
        )
        key_room(scene, cellblock, "cellblock")
    admin = scene.build_typed(
        "courthouse", x + w - 360, y + h - 260, 300, 190, floors=1,
        name=f"{name} Administration",
    )
    key_room(scene, admin, "prisonadministration")
    scene.build_typed(
        "clinic", x + 40, y + h - 230, 280, 170, floors=1,
        name=f"{name} Infirmary",
    )
    watchtower(scene, x + 20, y + 20, f"{name} Watchtower NW")
    watchtower(scene, x + w - 40, y + 20, f"{name} Watchtower NE")
    watchtower(scene, x + 20, y + h - 40, f"{name} Watchtower SW")
    watchtower(scene, x + w - 40, y + h - 40, f"{name} Watchtower SE")
    scene.add_road(x + w // 2 - 32, y + h, 64, 260)


def village(scene: Scene, x: int, y: int, w: int, h: int, name: str) -> None:
    """A small fenced village with houses, a market and a well square."""
    fence_rect(scene, x, y, w, h, gate=True)
    scene.paint("sidewalks", x + 30, y + 30, w - 60, h - 60, "sidewalk")
    for i in range(4):
        hx = x + 60 + (i % 2) * (w // 2)
        hy = y + 60 + (i // 2) * (h // 2)
        scene.build_house(hx, hy, w // 2 - 100, h // 2 - 100, floors=1, rooms=2,
                         name=f"{name} House {i + 1}")
    market = scene.build_typed(
        "shop", x + w // 2 - 80, y + h // 2 - 60, 180, 120, floors=1,
        name=f"{name} Market",
    )
    key_room(scene, market, "foodmarket")
    scene.add_road(x + w // 2 - 32, y + h, 64, 200)
