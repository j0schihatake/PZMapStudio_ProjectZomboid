#!/usr/bin/env python3
"""Add a few sidewalk parking stalls near existing spawn towns for maps without zones."""
from __future__ import annotations
import re, sys
from pathlib import Path
ROOT=Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/sod2-expansion/common/media/maps')
OMSK=Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/omsk-expansion/common/media/maps/Omsk_World')
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from pzmapstudio.pzlot import read_cell_records
TARGETS=[('Omsk_World',OMSK,'spawnpoints_*.lua'),('Trumbull Valley',ROOT/'Trumbull Valley','spawnpoints*.lua'),('Providence Ridge',ROOT/'Providence Ridge','spawnpoints*.lua')]
def points(mapdir):
 pts=[]
 for f in mapdir.glob('spawnpoints*.lua'):
  for x,y in re.findall(r'posX\s*=\s*(\d+).*?posY\s*=\s*(\d+)', f.read_text()):
   pts.append((int(x),int(y)))
 return pts
def find_pavement(mapdir,x,y):
 # cell-local records: scan the target cell and its neighbours for a sidewalk tile
 cx,cy=x//256,y//256
 for ox in (-1,0,1):
  for oy in (-1,0,1):
   cxx,cyy=cx+ox,cy+oy
   h=mapdir/f'{cxx}_{cyy}.lotheader'
   if not h.exists(): continue
   best=None
   for lx,ly,z,room,names in read_cell_records(mapdir,cxx,cyy):
    if z!=0: continue
    floor=''
    for n in names:
     if n.startswith('floors_exterior_street'): floor=n
    if not floor: continue
    wx,wy=lx+256*cxx,ly+256*cyy
    d=(wx-x)**2+(wy-y)**2
    if not best or d<best[0]: best=(d,wx,wy,floor)
   if best and best[0] <= 64*64: return best[1],best[2]
 return None
def main():
 for name,mapdir,pattern in TARGETS:
  pts=points(mapdir)
  zones=[]
  for x,y in pts:
   found=find_pavement(mapdir,x,y)
   if not found: continue
   px,py=found
   zones.append(f'      {{ name = "parkingstall", type = "ParkingStall", x = {px}, y = {py}, z = 0, width = 1, height = 4, properties = {{ Direction = "N" }} }},')
   if len(zones)>=4: break
  if not zones: print(name,'no pavement'); continue
  old=(mapdir/'objects.lua').read_text(errors='replace') if (mapdir/'objects.lua').exists() else ''
  if 'ParkingStall' in old: print(name,'already has parking'); continue
  if 'getObjectList' in old:
   (mapdir/'objects.lua').write_text(old.replace('\n  }', '\n'+'\n'.join(zones)+'\n  }', 1))
  else:
   (mapdir/'objects.lua').write_text('function getObjectList()\n  return {\n'+'\n'.join(zones)+'\n  }\nend\n')
  print(name,'zones',len(zones))
if __name__=='__main__': raise SystemExit(main())
