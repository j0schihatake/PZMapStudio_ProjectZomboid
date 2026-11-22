#!/usr/bin/env python3
"""Add a paved shoulder outside already-compiled roads."""
from __future__ import annotations
import argparse, shutil, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from pzmapstudio.pzlot import read_header, read_cell_records, rewrite_cell
PAVEMENT='floors_exterior_street_01_0'
def road(n):
 n=n.lower(); return n.startswith(('floors_exterior_street','blends_street')) or 'asphalt' in n
def blocked(n):
 n=n.lower(); return n.startswith(('walls_','floors_interior','water_','fixtures_doors'))
def work(args):
 root,cx,cy,grow,outroot=args; p=Path(root); h=p/f'{cx}_{cy}.lotheader'
 if not h.exists(): return 0
 if not any(road(n) for n in read_header(h).names): return 0
 recs=list(read_cell_records(p,cx,cy)); by={(x,y,z):names for x,y,z,_,names in recs}
 seeds={(x,y,z) for (x,y,z),names in by.items() if any(road(n) for n in names)}
 add=set()
 for x,y,z in seeds:
  for dx in range(-grow,grow+1):
   for dy in range(-grow,grow+1):
    k=(x+dx,y+dy,z); names=by.get(k)
    if not names: continue
    if any(road(n) for n in names): continue
    if any(blocked(n) for n in names): continue
    add.add(k)
 if not add: return 0
 overrides={}
 for k in add:
  kept=[n for n in by[k] if not n.lower().startswith(('blends_','floors_','vegetation_','e_'))]
  overrides[k]=[PAVEMENT]+kept
 out=Path(outroot)/f'{cx}_{cy}'
 if out.exists(): shutil.rmtree(out)
 rewrite_cell(p,out,cx,cy,overrides)
 for name in (f'{cx}_{cy}.lotheader',f'world_{cx}_{cy}.lotpack'):
  shutil.copy2(out/name,p/name)
 shutil.rmtree(out); return len(overrides)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--map',required=True); ap.add_argument('--grow',type=int,default=3); ap.add_argument('--workers',type=int,default=12); ap.add_argument('--out-root',default='examples/sidewalk-tmp'); a=ap.parse_args()
 root=Path(a.map); cells=[]
 for h in root.glob('*.lotheader'):
  s=h.stem.split('_'); cells.append((str(root),int(s[-2]),int(s[-1]),a.grow,a.out_root))
 total=0
 with ProcessPoolExecutor(max_workers=a.workers) as ex:
  for i,f in enumerate(as_completed([ex.submit(work,c) for c in cells]),1):
   total+=f.result()
   if i%200==0: print(f'{i}/{len(cells)} sidewalk={total}',flush=True)
 print('added_sidewalk',total)
if __name__=='__main__': raise SystemExit(main())
