#!/usr/bin/env python3
"""Fill empty Isilkul cells and add walls/doors to rooms without any walls."""
from __future__ import annotations
import shutil, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from pzmapstudio.pzlot import read_header_full, read_cell_records, rewrite_cell
ROOT=Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/omsk-expansion/common/media/maps/Omsk_World')
GRASS='floors_exterior_natural_01_16'; WALL='walls_commercial_01_48'; DOOR='fixtures_doors_01_0'
def work(cx,cy):
 h=ROOT/f'{cx}_{cy}.lotheader'
 if not h.exists(): return (0,0,0)
 recs=list(read_cell_records(ROOT,cx,cy)); by={(x,y,z):names for x,y,z,_,names in recs}
 overrides={}; empty=walls=doors=0
 # Fill a completely empty cell with grass.
 if not any(any(n.startswith('floors_') for n in ns) for ns in by.values()):
  for x in range(256):
   for y in range(256): overrides[(x,y,0)]=[GRASS]
  empty=1
 _h,rooms,_b=read_header_full(h)
 for name,z,rects in rooms:
  if name.lower() in ('outside','yard','street','road'): continue
  for lx,ly,w,hh in rects:
   if w<2 or hh<2: continue
   x0,y0=lx+256*cx,ly+256*cy
   edge=[]
   for xx in range(x0,x0+w): edge += [(xx,y0,z),(xx,y0+hh-1,z)]
   for yy in range(y0,y0+hh): edge += [(x0,yy,z),(x0+w-1,yy,z)]
   edge=sorted(set(edge))
   if any(any(n.startswith('walls_') for n in by.get((x,y,z),[])) for x,y,_ in edge): continue
   for x,y,_ in edge:
    if (x,y,z) in by:
     overrides[(x,y,z)]=[WALL]; walls+=1
   if edge:
    x,y,_=edge[len(edge)//2]
    if (x,y,z) in by:
     overrides[(x,y,z)]=[DOOR,GRASS]; doors+=1
 if not overrides: return (0,0,0)
 out=Path('examples/isilkul-repair')/f'{cx}_{cy}'
 if out.exists(): shutil.rmtree(out)
 rewrite_cell(ROOT,out,cx,cy,overrides)
 for n in (f'{cx}_{cy}.lotheader',f'world_{cx}_{cy}.lotpack'):
  shutil.copy2(out/n,ROOT/n)
 shutil.rmtree(out); return (empty,walls,doors)
e=w=d=0
for cy in range(60,76):
 for cx in range(0,15):
  a,b,c=work(cx,cy); e+=a;w+=b;d+=c
print('empty_filled',e,'walls',w,'doors',d)
