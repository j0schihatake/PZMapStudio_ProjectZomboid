#!/usr/bin/env python3
"""Harran City and The Following countryside (Dying Light-inspired)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.scene import Scene
from pzmapstudio.worlded import export_scene_map

OUT = Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/sod2-expansion/common/media/maps')


def key_room(scene, result, kind):
    building = scene.buildings[result['building']]
    floor = building.floors[min(building.floors)]
    if floor.rooms:
        floor.rooms[0].kind = kind


def key_room_at(scene, result, index, kind):
    building = scene.buildings[result['building']]
    floor = building.floors[min(building.floors)]
    if len(floor.rooms) > index:
        floor.rooms[index].kind = kind


def ring(scene: Scene, margin: int, width: int = 64) -> None:
    scene.add_road(margin, margin, scene.width - 2 * margin, width)
    scene.add_road(margin, scene.height - margin - width, scene.width - 2 * margin, width)
    scene.add_road(margin, margin, width, scene.height - 2 * margin)
    scene.add_road(scene.width - margin - width, margin, width, scene.height - 2 * margin)


def city() -> None:
    scene = Scene('Harran City', 24 * 256, 24 * 256)
    # Concrete ring and major streets.
    ring(scene, 280)
    for x in (1200, 2400, 3600, 4800):
        scene.add_road(x, 280, 56, scene.height - 560)
    for y in (1200, 2400, 3600, 4800):
        scene.add_road(280, y, scene.width - 560, 56)
    # West connection to Danforth.
    scene.add_road(0, 2380, 650, 80)
    # Recognisable landmarks.
    scene.build_typed('base', 650, 650, 700, 650, name='The Tower')
    b=scene.build_typed('clinic', 1400, 650, 650, 500, name="St. Joseph's Hospital"); key_room(scene,b,'pharmacy')
    scene.build_typed('school', 2500, 650, 700, 600, name='Harran High School')
    scene.build_typed('base', 3700, 650, 700, 650, name='Harran Stadium')
    scene.build_typed('church', 650, 3000, 600, 600, name='Old Town Mosque')
    b=scene.build_typed('fair_hall', 1450, 3000, 800, 650, name='Old Town Market'); key_room(scene,b,'foodmarket')
    b=scene.build_typed('warehouse', 2700, 3000, 750, 600, name='Harran Depot'); key_room(scene,b,'gunstore')
    b=scene.build_typed('courthouse', 3800, 3000, 700, 550, name='Harran Police Station'); key_room(scene,b,'police')
    # Dense residential blocks.
    for i, (x, y) in enumerate([
        (700, 1600), (1500, 1600), (2600, 1600), (3900, 1600),
        (700, 2300), (1500, 2300), (2600, 2300), (3900, 2300),
        (700, 3800), (1500, 3800), (2600, 3800), (3900, 3800),
        (700, 4500), (1500, 4500), (2600, 4500), (3900, 4500),
    ]):
        scene.build_house(x, y, 520, 420, floors=1, rooms=4, name=f'Harran Block {i+1}')
    # A few market stalls and barricades.
    for i in range(10):
        scene.add_fence(900 + i * 90, 2850, 70, axis='y', kind='metal', gate=True)
    scene.add_spawn(2500, 2350)
    scene.clean_roads()
    scene.clean_interiors()
    scene.auto_roof_access(min_area=300, kind='ladder')
    export_scene_map(scene, OUT / 'Harran City', 184, 0)
    print('Harran City buildings', len(scene.buildings), 'cells', 24 * 24)


def countryside() -> None:
    scene = Scene('The Following', 24 * 256, 24 * 256)
    ring(scene, 220)
    scene.add_road(0, 2380, 620, 80)
    scene.add_road(3000, 0, 64, scene.height)
    scene.add_road(0, 3000, scene.width, 64)
    # Village centre.
    scene.build_typed('church', 700, 700, 700, 600, name='Countryside Chapel')
    scene.build_typed('barn', 1700, 700, 800, 700, name='Bilal Farm')
    b=scene.build_typed('warehouse', 2800, 700, 800, 600, name='Grain Store'); key_room(scene,b,'foodstore')
    b=scene.build_typed('shop', 700, 1700, 700, 600, name='Village Market'); key_room(scene,b,'gunstore'); key_room_at(scene,b,1,'foodmarket')
    for i, (x, y) in enumerate([(1700, 1700), (2800, 1700), (700, 2600), (1700, 2600), (2800, 2600)]):
        scene.build_house(x, y, 600, 500, floors=1, rooms=4, name=f'Farmhouse {i+1}')
    b=scene.build_typed('clinic', 700, 3300, 700, 600, name='Countryside Clinic')
    key_room(scene,b,'pharmacy')
    b=scene.build_typed('courthouse', 2800, 3300, 800, 600, name='Countryside Constable')
    key_room(scene,b,'police')
    # River and lake on the east; bridges are the two roads crossing it.
    scene.paint('water', 4000, 0, 700, scene.height, 'water')
    scene.paint('water', 4700, 3300, 1300, 1200, 'water')
    # Fields west and south, forest on the east bank.
    scene.paint('terrain', 300, 3400, 3400, 2500, 'field')
    scene.paint('terrain', 300, 0, 3400, 500, 'field')
    scene.paint('terrain', 5200, 0, 700, 3000, 'forest')
    scene.paint('terrain', 400, 5500, 3500, 400, 'forest')
    scene.add_spawn(2200, 2300)
    scene.clean_roads()
    scene.auto_roof_access(min_area=300, kind='ladder')
    export_scene_map(scene, OUT / 'The Following', 184, 24)
    print('The Following buildings', len(scene.buildings), 'cells', 24 * 24)


if __name__ == '__main__':
    city()
    countryside()
