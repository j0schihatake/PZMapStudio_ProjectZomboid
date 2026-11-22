#!/usr/bin/env python3
"""Remove edge/half props and fill ground under lamp/bench-only squares."""
from __future__ import annotations
import argparse, shutil, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from pzmapstudio.pzlot import read_header, read_cell_records, rewrite_cell
PROPS={'furniture_seating_outdoor_01_0','furniture_tables_low_01_0','furniture_seating_indoor_01_0','lighting_outdoor_01_0'}
SIDEWALK='floors_exterior_street_01_0'; GRASS='floors_exterior_natural_01_16'
def is_road(n): return n.startswith(('floors_exterior_street','blends_street')) or 'asphalt' in n
def ground(n): return n.startswith(('floors_','blends_'))
def work(args):
 root,cx,cy,outroot=args; p=Path(root); h=p/f'{cx}_{cy}.lotheader'
 if not h.exists(): return 0
 if not any(n in PROPS for n in read_header(h).names): return 0
 recs=list(read_cell_records(p,cx,cy)); by={(x,y,z):names for x,y,z,_,names in recs}
 overrides={}; removed=0; filled=0
 for (x,y,z),names in by.items():
  has=any(n in PROPS for n in names)
  if not has: continue
  keep=[n for n in names if n not in PROPS]
  # Any prop on the road edge or on a non-sidewalk square near a road is half-placed.
  edge=False
  if any(is_road(n) for n in names):
   edge=True
  if SIDEWALK in names:
   for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
    other=by.get((x+dx,y+dy,z),[])
    if not other or is_road(names) or SIDEWALK not in other:
     edge=True; break
  if edge:
   removed+=1
   if keep: overrides[(x,y,z)]=keep
   else:
    # Recover a ground tile from a neighbour.
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(2,0),(-2,0),(0,2),(0,-2)):
     other=by.get((x+dx,y+dy,z),[])
     g=[n for n in other if ground(n) and n not in PROPS]
     if g: keep=g; break
    if not keep: keep=[GRASS]
    overrides[(x,y,z)]=keep; filled+=1
  elif not any(ground(n) for n in names):
   # Groundless lamp/bench in a non-edge square.
   for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(2,0),(-2,0),(0,2),(0,-2)):
    other=by.get((x+dx,y+dy,z),[])
    g=[n for n in other if ground(n) and n not in PROPS]
    if g: keep=g+keep; break
   if not any(ground(n) for n in keep): keep=[GRASS]+keep
   overrides[(x,y,z)]=keep; filled+=1
 if not overrides: return 0
 out=Path(outroot)/f'{cx}_{cy}'
 if out.exists(): shutil.rmtree(out)
 rewrite_cell(p,out,cx,cy,overrides)
 for name in (f'{cx}_{cy}.lotheader',f'world_{cx}_{cy}.lotpack'):
  shutil.copy2(out/name,p/name)
 shutil.rmtree(out); return removed*1000000+filled
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--map',required=True); ap.add_argument('--workers',type=int,default=12); ap.add_argument('--out-root',default='examples/fixprops-tmp'); a=ap.parse_args()
 root=Path(a.map); cells=[]
 for h in root.glob('*.lotheader'):
  s=h.stem.split('_'); cells.append((str(root),int(s[-2]),int(s[-1]),a.out_root))
 total=0
 with ProcessPoolExecutor(max_workers=a.workers) as ex:
  for i,f in enumerate(as_completed([ex.submit(work,c) for c in cells]),1):
   total+=f.result()
   if i%500==0: print(f'{i}/{len(cells)}',flush=True)
 print('removed_and_filled',total//1000000,total%1000000)
if __name__=='__main__': raise SystemExit(main())
