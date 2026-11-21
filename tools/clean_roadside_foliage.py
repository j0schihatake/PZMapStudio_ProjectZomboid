#!/usr/bin/env python3
"""Remove bushes/grass overlays touching road squares (one tile radius)."""
from __future__ import annotations
import argparse, shutil, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from pzmapstudio.pzlot import read_header, read_cell_records, rewrite_cell

def road(n):
 n=n.lower(); return n.startswith(('floors_exterior_street','blends_street','road')) or 'asphalt' in n
def veg(n):
 n=n.lower()
 if 'street' in n: return False
 return n.startswith(('blends_natural','blends_grassoverlays','vegetation_','bushes','tree','floors_exterior_natural')) or 'bush' in n

def work(args):
 root,cx,cy,outroot=args; p=Path(root)
 h=read_header(p/f'{cx}_{cy}.lotheader')
 if not any(road(n) for n in h.names): return 0,0
 recs=list(read_cell_records(p,cx,cy)); by={ (x,y,z):names for x,y,z,_,names in recs }
 near=set()
 for (x,y,z),names in by.items():
  if any(road(n) for n in names):
   for dx in (-1,0,1):
    for dy in (-1,0,1): near.add((x+dx,y+dy,z))
 overrides={}; removed=0
 for key in near:
  names=by.get(key)
  if not names: continue
  kept=[n for n in names if not veg(n)]
  if len(kept)==len(names) or not kept: continue
  overrides[key]=kept; removed+=len(names)-len(kept)
 if not overrides: return 0,0
 out=Path(outroot)/f'{cx}_{cy}'
 if out.exists(): shutil.rmtree(out)
 rewrite_cell(p,out,cx,cy,overrides)
 for n in (f'{cx}_{cy}.lotheader',f'world_{cx}_{cy}.lotpack'): shutil.copy2(out/n,p/n)
 shutil.rmtree(out)
 return removed,len(overrides)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--map',required=True); ap.add_argument('--workers',type=int,default=8); ap.add_argument('--out-root',default='examples/roadside-tmp'); ap.add_argument('--skip-newer-than',type=float,default=0); ap.add_argument('--x0',type=int); ap.add_argument('--y0',type=int); ap.add_argument('--x1',type=int); ap.add_argument('--y1',type=int); a=ap.parse_args()
 root=Path(a.map); cells=[]
 for h in root.glob('*.lotheader'):
  if a.skip_newer_than and h.stat().st_mtime > a.skip_newer_than: continue
  s=h.stem.split('_'); cx,cy=int(s[-2]),int(s[-1])
  if a.x0 is not None and not (a.x0<=cx<=a.x1 and a.y0<=cy<=a.y1): continue
  cells.append((str(root),cx,cy,a.out_root))
 total=0; cells_n=0
 with ProcessPoolExecutor(max_workers=a.workers) as ex:
  fs=[ex.submit(work,c) for c in cells]
  for i,f in enumerate(as_completed(fs),1):
   r,n=f.result(); total+=r
   if r: cells_n+=1
   if i%100==0: print(f'{i}/{len(cells)} removed={total}',flush=True)
 print('removed_tiles',total,'changed_cells',cells_n)
if __name__=='__main__': raise SystemExit(main())
