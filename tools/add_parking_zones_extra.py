#!/usr/bin/env python3
"""Add parking stalls to the hand-authored landmarks outside the SoD JSON set."""
from pathlib import Path
ROOT=Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/sod2-expansion/common/media/maps')
DATA={
 'Danforth':[(700,700,1200,1100),(650,1950,900,600),(4200,2400,800,700)],
 'Harran City':[(650,650,700,650),(3700,650,700,650),(4550,1550,1050,900),(4550,2600,1000,800),(4550,3800,1100,950),(4550,4900,1000,800)],
 'Dread Dawn':[(620,620,1500,1300),(2450,500,900,700),(3800,2600,1000,800),(650,3000,900,700)],
 'The Following':[(700,1700,700,600)],
}
def line(x,y,w,h,name,kind,dir='N',traffic=False):
    prop='' if traffic else f', properties = {{ Direction = "{dir}" }}'
    return f'      {{ name = "{name}", type = "ParkingStall", x = {x}, y = {y}, z = 0, width = {w}, height = {h}{prop} }},'
for mapname,areas in DATA.items():
    lines=[]
    for x,y,w,h in areas:
        lines += [line(x+45,y+100,3,10,'parkingstall','N'), line(x+55,y+100,3,10,'parkingstall','N'),
                  line(x+w//2-4,y+h+40,8,4,'trafficjame','E',True)]
    p=ROOT/mapname/'objects.lua'
    if not p.parent.is_dir(): print('missing',mapname); continue
    p.write_text('function getObjectList()\n    return {\n'+'\n'.join(lines)+'\n    }\nend\n')
    print(mapname,'zones',len(lines))
