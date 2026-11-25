#!/usr/bin/env python3
"""Fill floorless cells with ground and build walls/doors for wall-less rooms.

Works on compiled cells only; objects.lua, spawnpoints and map.info are untouched.
"""
from __future__ import annotations
import argparse, shutil, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from pzmapstudio.pzlot import read_header_full, read_cell_records, rewrite_cell
GROUND='floors_exterior_natural_01_16'; WALL='walls_commercial_01_48'; DOOR='fixtures_doors_01_0'
SKIP_NAMES={'outside','yard','street','road','forest','water','parking'}
def work(args):
 root,cx,cy,outroot,ground_only=args; root=Path(root); outroot=Path(outroot)
 h=root/f'{cx}_{cy}.lotheader'
 if not h.exists(): return (0,0,0)
 try:
  recs=list(read_cell_records(root,cx,cy))
  by={(x,y,z):names for x,y,z,_,names in recs}
  overrides={}; filled=walls=doors=0
  has_floor=any(any(n.startswith('floors_') for n in ns) for ns in by.values())
  if not has_floor:
   for x in range(256):
    for y in range(256): overrides[(x,y,0)]=[GROUND]
   filled=1
  _h,rooms,_b=read_header_full(h)
  for name,z,rects in ([] if ground_only else rooms):
   if name.lower() in SKIP_NAMES: continue
   for lx,ly,w,hh in rects:
    if w<2 or hh<2: continue
    x0,y0=lx+256*cx,ly+256*cy
    edge=[]
    for xx in range(x0,x0+w): edge += [(xx,y0,z),(xx,y0+hh-1,z)]
    for yy in range(y0,y0+hh): edge += [(x0,yy,z),(x0+w-1,yy,z)]
    edge=sorted(set(edge))
    if any(any(n.startswith('walls_') for n in by.get(k,[])) for k in edge): continue
    for k in edge:
     if k in by: overrides[k]=[WALL]; walls+=1
    if edge:
     k=edge[len(edge)//2]
     if k in by: overrides[k]=[DOOR,GROUND]; doors+=1
  if not overrides: return (0,0,0)
  out=outroot/f'{cx}_{cy}'
  if out.exists(): shutil.rmtree(out)
  rewrite_cell(root,out,cx,cy,overrides)
  for n in (f'{cx}_{cy}.lotheader',f'world_{cx}_{cy}.lotpack'):
   shutil.copy2(out/n,root/n)
  shutil.rmtree(out); return (filled,walls,doors)
 except Exception as e:
  print('FAIL',root.name,cx,cy,e,flush=True); return (0,0,0)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--maps-root',required=True); ap.add_argument('--workers',type=int,default=12); ap.add_argument('--out-root',default='examples/ground-walls-tmp'); ap.add_argument('--ground-only',action='store_true'); a=ap.parse_args()
 root=Path(a.maps_root); maps=[root] if list(root.glob('*.lotheader')) else [p for p in root.iterdir() if p.is_dir() and list(p.glob('*.lotheader'))]
 totals=[0,0,0]
 for m in maps:
  cells=[]
  for h in m.glob('*.lotheader'):
   p=h.stem.split('_'); cells.append((str(m),int(p[-2]),int(p[-1]),a.out_root,a.ground_only))
  with ProcessPoolExecutor(max_workers=a.workers) as ex:
   for i,f in enumerate(as_completed([ex.submit(work,c) for c in cells]),1):
    a1,b1,c1=f.result(); totals[0]+=a1; totals[1]+=b1; totals[2]+=c1
    if i%500==0: print(m.name,i,'/',len(cells),'filled',totals[0],'walls',totals[1],'doors',totals[2],flush=True)
  print('DONE',m.name,flush=True)
 print('TOTAL filled',totals[0],'walls',totals[1],'doors',totals[2])
if __name__=='__main__': raise SystemExit(main())
