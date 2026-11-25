#!/usr/bin/env python3
"""Add ground under street props/signs/hydrants that ended up on object-only squares."""
from __future__ import annotations
import argparse, shutil, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from pzmapstudio.pzlot import read_cell_records, rewrite_cell
PROP=('street_','lighting_','furniture_','fire_hydrant','hydrant','traffic_','sign','lamp','trash','bench')
GROUND=('floors_','blends_')
def is_prop(n):
 n=n.lower(); return any(n.startswith(x) or x in n for x in PROP)
def is_ground(n):
 n=n.lower(); return n.startswith(GROUND)
def work(args):
 root,cx,cy,outroot=args; root=Path(root); outroot=Path(outroot)
 h=root/f'{cx}_{cy}.lotheader'
 if not h.exists(): return 0
 by={(x,y,z):ns for x,y,z,_,ns in read_cell_records(root,cx,cy)}
 overrides={}; fixed=0
 for (x,y,z),names in by.items():
  if not any(is_prop(n) for n in names): continue
  if any(is_ground(n) for n in names): continue
  ground=None
  for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(2,0),(-2,0),(0,2),(0,-2)):
   other=by.get((x+dx,y+dy,z),[])
   g=[n for n in other if is_ground(n) and not is_prop(n)]
   if g: ground=g[0]; break
  if not ground: ground='floors_exterior_natural_01_16'
  overrides[(x,y,z)]=[ground]+names; fixed+=1
 if not overrides: return 0
 out=outroot/f'{cx}_{cy}'
 if out.exists(): shutil.rmtree(out)
 rewrite_cell(root,out,cx,cy,overrides)
 for n in (f'{cx}_{cy}.lotheader',f'world_{cx}_{cy}.lotpack'): shutil.copy2(out/n,root/n)
 shutil.rmtree(out); return fixed
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--maps-root',required=True); ap.add_argument('--workers',type=int,default=12); ap.add_argument('--out-root',default='examples/prop-ground-tmp'); a=ap.parse_args()
 root=Path(a.maps_root); maps=[root] if list(root.glob('*.lotheader')) else [p for p in root.iterdir() if p.is_dir() and list(p.glob('*.lotheader'))]
 total=0
 for m in maps:
  cells=[]
  for h in m.glob('*.lotheader'):
   p=h.stem.split('_'); cells.append((str(m),int(p[-2]),int(p[-1]),a.out_root))
  with ProcessPoolExecutor(max_workers=a.workers) as ex:
   for i,f in enumerate(as_completed([ex.submit(work,c) for c in cells]),1):
    total+=f.result()
    if i%500==0: print(m.name,i,'/',len(cells),'fixed',total,flush=True)
  print('DONE',m.name,flush=True)
 print('TOTAL',total)
if __name__=='__main__': raise SystemExit(main())
