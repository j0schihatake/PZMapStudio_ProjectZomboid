#!/usr/bin/env python3
"""Danforth (State of Decay: Lifeline) — compact 20x20 evacuation city."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from pzmapstudio.scene import Scene
from pzmapstudio.worlded import export_scene_map
from pzmapstudio.hero import military_base, prison, survivor_camp


def key_room(scene, result, kind):
    building = scene.buildings[result['building']]
    floor = building.floors[min(building.floors)]
    if floor.rooms:
        floor.rooms[0].kind = kind

def road(scene, x, y, w, h):
    scene.add_road(x, y, w, h, material="asphalt", sidewalk=True)

def main():
    out=Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/sod2-expansion/common/media/maps')
    scene=Scene('Danforth', 20*256, 20*256)
    # Ring road and inner cross, all inside the 5120-tile map.
    road(scene, 0, 300, 5120, 64)
    road(scene, 0, 4756, 5120, 64)
    road(scene, 300, 0, 64, 5120)
    road(scene, 4756, 0, 64, 5120)
    road(scene, 2460, 300, 64, 4500)
    road(scene, 300, 2460, 4820, 64)
    # West connection toward the SoD2 pack.
    road(scene, 0, 2440, 500, 80)
    # Significant landmarks, kept out of the ring and cross roads.
    b=scene.build_typed('base', 700, 700, 1200, 1100, floors=1, name='Danforth Evacuation Center'); key_room(scene,b,'foodstore')
    military_base(scene, 650, 1950, 900, 600, 'Danforth National Guard')
    b=scene.build_typed('clinic', 3000, 700, 1100, 900, floors=1, name='Danforth Memorial Hospital'); key_room(scene,b,'pharmacy')
    scene.build_typed('church', 700, 2800, 900, 760, floors=1, name='St. Michael Church')
    scene.build_typed('school', 3000, 2800, 1200, 900, floors=1, name='Danforth High School')
    b=scene.build_typed('courthouse', 700, 3900, 1100, 620, floors=1, name='Danforth Police & Civil Office'); key_room(scene,b,'police')
    b=scene.build_typed('warehouse', 2900, 3900, 1100, 650, floors=1, name='Evacuation Supply Depot'); key_room(scene,b,'gunstore')
    prison(scene, 4200, 2400, 800, 700, 'Danforth State Prison')
    survivor_camp(scene, 2000, 3900, 700, 600, 'Danforth Camp')
    # Compact residential blocks.
    for i,(x,y) in enumerate([(750,1950),(1500,1950),(3000,1800),(3800,1800),(1600,3400),(3000,1850)]):
        scene.build_house(x,y,520,420,floors=1,rooms=4,name=f'Danforth Residence {i+1}')
    scene.clean_roads()
    scene.clean_interiors()
    scene.auto_roof_access(min_area=150, kind='ladder')
    scene.add_spawn(2500, 2200)
    scene.add_spawn(1300, 1200)
    scene.add_spawn(3600, 1200)
    scene.add_spawn(3600, 4000)
    export_scene_map(scene, out/'Danforth', 164, 0)
    print('Danforth buildings',len(scene.buildings),'cells',20*20)
    return 0
if __name__=='__main__': raise SystemExit(main())
