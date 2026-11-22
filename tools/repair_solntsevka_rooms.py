#!/usr/bin/env python3
"""Ensure Solntsevka ground-floor rooms have a wall perimeter and a door."""
from __future__ import annotations
import shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from pzmapstudio.pzlot import read_header_full, read_cell_records, rewrite_cell
WALL='walls_commercial_01_48'; DOOR='fixtures_doors_01_0'
KEEP={'livingroom','bedroom','kitchen','bathroom','storage','shop','office','hall','lobby','diningroom','classroom','library','clinic','ward','exam'}
def cell(root,cx,cy):
 p=Path(root); h=p/f'{cx}_{cy}.lotheader'
 if not h.exists(): return 0
 _h,rooms,_b=read_header_full(h)
 recs=list(read_cell_records(p,cx,cy)); by={(x,y,z):names for x,y,z,_,names in recs}
 overrides={}; walls=doors=0
 for name,z,rects in rooms:
  if z<0 or name.lower() not in KEEP: continue
  for lx,ly,w,hh in rects:
   if w<2 or hh<2: continue
   x0,y0=lx+256*cx,ly+256*cy
   edge=[]
   for xx in range(x0,x0+w): edge += [(xx,y0,z),(xx,y0+hh-1,z)]
   for yy in range(y0,y0+hh): edge += [(x0,yy,z),(x0+w-1,yy,z)]
   edge=sorted(set(edge))
   has_wall=any(any(n.startswith('walls_') for n in by.get(k,[])) for k in edge)
   has_door=any(any(n.startswith('fixtures_doors') for n in by.get(k,[])) for k in edge)
   if not has_wall:
    for k in edge:
     if k not in by: continue
     overrides[k]=[WALL]
     walls+=1
   if not has_door and edge:
    k=edge[len(edge)//2]
    if k in by:
     kept=[n for n in by[k] if not n.startswith('walls_')]
     overrides[k]=[DOOR]+kept; doors+=1
 if not overrides: return 0
 out=Path('examples/solrooms')/f'{cx}_{cy}'
 if out.exists(): shutil.rmtree(out)
 rewrite_cell(p,out,cx,cy,overrides)
 for n in (f'{cx}_{cy}.lotheader',f'world_{cx}_{cy}.lotpack'):
  shutil.copy2(out/n,p/n)
 shutil.rmtree(out); return walls*1000000+doors
root='/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/omsk-expansion/common/media/maps/Omsk_World'
tw=td=0
for cx in range(0,14):
 for cy in range(75,93):
  v=cell(root,cx,cy); tw+=v//1000000; td+=v%1000000
print('walls',tw,'doors',td)
