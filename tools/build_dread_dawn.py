#!/usr/bin/env python3
"""Dread Dawn-inspired quarantined city (school camp, hospital, checkpoint)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.scene import Scene
from pzmapstudio.worlded import export_scene_map

OUT = Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/sod2-expansion/common/media/maps')


def key_room(scene: Scene, result: dict, kind: str) -> None:
    building = scene.buildings[result['building']]
    floor = building.floors[min(building.floors)]
    if floor.rooms:
        floor.rooms[0].kind = kind


def road(scene: Scene, x: int, y: int, w: int, h: int) -> None:
    scene.add_road(x, y, w, h, material='asphalt', sidewalk=True)


def main() -> int:
    scene = Scene('Dread Dawn', 24 * 256, 24 * 256)
    # Ring road, main avenue, and the quarantine cordon.
    road(scene, 0, 260, 6144, 96)
    road(scene, 0, 5820, 6144, 96)
    road(scene, 260, 0, 96, 6144)
    road(scene, 5820, 0, 96, 6144)
    road(scene, 0, 3000, 6144, 96)
    road(scene, 3000, 0, 96, 6144)
    road(scene, 0, 2380, 650, 112)
    # School camp: the player's starting base.
    b = scene.build_typed('base', 620, 620, 1500, 1300, name='Dread Dawn School Camp')
    key_room(scene, b, 'school')
    scene.add_fence(650, 650, 1400, axis='x', kind='metal', gate=True)
    scene.add_fence(650, 1850, 1400, axis='x', kind='metal', gate=True)
    scene.add_fence(650, 650, 1200, axis='y', kind='metal', gate=True)
    scene.add_fence(2050, 650, 1200, axis='y', kind='metal', gate=True)
    # Hospital, checkpoint, police, food market and bus station.
    b = scene.build_typed('clinic', 3700, 620, 1100, 900, name='Dread Dawn Hospital')
    key_room(scene, b, 'pharmacy')
    b = scene.build_typed('base', 2450, 500, 900, 700, name='North Evacuation Checkpoint')
    key_room(scene, b, 'military')
    b = scene.build_typed('courthouse', 650, 3900, 900, 650, name='Dread Dawn Police Station')
    key_room(scene, b, 'police')
    b = scene.build_typed('shop', 1700, 3950, 650, 500, name='Quarantine Gun Shop')
    key_room(scene, b, 'gunstore')
    b = scene.build_typed('fair_hall', 2550, 3850, 950, 750, name='Dread Dawn Food Market')
    key_room(scene, b, 'foodmarket')
    b = scene.build_typed('warehouse', 3700, 3850, 950, 700, name='City Bus Station')
    key_room(scene, b, 'foodstore')
    # Apartment blocks and smaller shops.
    for i, (x, y) in enumerate([
        (650, 2200), (1450, 2200), (2250, 2200), (3700, 2000), (4500, 2000),
        (650, 4700), (1450, 4700), (2250, 4700), (3700, 4700), (4500, 4700),
    ]):
        scene.build_house(x, y, 560, 450, floors=1, rooms=4, name=f'Dread Dawn Apartment {i+1}')
    # Concrete plaza and quarantine barriers.
    scene.paint('sidewalks', 2450, 2200, 1300, 800, 'sidewalk')
    scene.paint('sidewalks', 2200, 3600, 1500, 500, 'sidewalk')
    scene.add_fence(2500, 2100, 1800, axis='x', kind='metal', gate=True)
    scene.add_fence(2500, 3500, 1800, axis='x', kind='metal', gate=True)
    # Canal on the east, with bridges formed by the main roads.
    scene.paint('water', 5200, 0, 420, 6144, 'water')
    # Spawn inside the school camp.
    scene.add_spawn(1300, 1100)
    scene.add_spawn(4200, 1000)
    scene.add_spawn(2900, 800)
    scene.add_spawn(3000, 4200)
    scene.clean_roads()
    scene.clean_interiors()
    scene.auto_roof_access(min_area=250, kind='ladder')
    export_scene_map(scene, OUT / 'Dread Dawn', 208, 0)
    print('Dread Dawn buildings', len(scene.buildings), 'cells', 24 * 24)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
