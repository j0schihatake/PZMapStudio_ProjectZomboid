#!/usr/bin/env python3
"""Add safe ParkingStall and traffic-jam zones to SoD base compounds."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/sod2-expansion/common/media/maps')
DATA=Path(__file__).resolve().parent.parent/'sod2-buildings.json'
def object_line(x,y,w,h,name='parkingstall',kind='ParkingStall',direction='N',traffic=False):
    props = '' if traffic else f', properties = {{ Direction = "{direction}" }}'
    return f'      {{ name = "{name}", type = "{kind}", x = {x}, y = {y}, z = 0, width = {w}, height = {h}{props} }},'
def main():
    data=json.loads(DATA.read_text())
    for mapname, spec in data.items():
        mapdir=ROOT/mapname
        if not mapdir.is_dir(): print('missing',mapname); continue
        lines=[]
        for item in spec.get('bases',[]):
            if item.get('kind') not in ('base','warehouse','clinic','house','prison','shop','courthouse','school','firestation','police'):
                continue
            x,y,w,h=item['x'],item['y'],item['w'],item['h']
            # Two stalls on the paved inner perimeter, away from the main building.
            lines.append(object_line(x+45,y+100,3,10,'parkingstall','ParkingStall','N'))
            lines.append(object_line(x+55,y+100,3,10,'parkingstall','ParkingStall','N'))
            # A small accident zone on the access road outside the compound.
            lines.append(object_line(x+w//2-4,y+h+40,8,4,'trafficjame','ParkingStall','E',True))
        content='function getObjectList()\n    return {\n' + '\n'.join(lines) + '\n    }\nend\n'
        (mapdir/'objects.lua').write_text(content)
        print(mapname,'zones',len(lines))
if __name__=='__main__': raise SystemExit(main())
