#!/usr/bin/env python3
"""Replace gravel-looking blends_street road tiles with plain asphalt."""
from __future__ import annotations
import argparse, shutil, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from pzmapstudio.pzlot import read_header, read_cell_records, rewrite_cell
ROAD='floors_exterior_street_01_16'
def work(args):
 root,cx,cy,outroot=args; p=Path(root); h=p/f'{cx}_{cy}.lotheader'
 if not h.exists(): return 0
 if not any(n.startswith('blends_street') for n in read_header(h).names): return 0
 overrides={}; n=0
 for x,y,z,room,names in read_cell_records(p,cx,cy):
  if not any(name.startswith('blends_street') for name in names): continue
  new=[]
  for name in names:
   if name.startswith('blends_street'):
    if ROAD not in new: new.append(ROAD)
    n+=1
   elif name not in new: new.append(name)
  overrides[(x,y,z)]=new
 if not overrides: return 0
 out=Path(outroot)/f'{cx}_{cy}'
 if out.exists(): shutil.rmtree(out)
 rewrite_cell(p,out,cx,cy,overrides)
 for name in (f'{cx}_{cy}.lotheader',f'world_{cx}_{cy}.lotpack'):
  shutil.copy2(out/name,p/name)
 shutil.rmtree(out); return n
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--map',required=True); ap.add_argument('--workers',type=int,default=12); ap.add_argument('--out-root',default='examples/asphalt-tmp'); a=ap.parse_args()
 root=Path(a.map); cells=[]
 for h in root.glob('*.lotheader'):
  s=h.stem.split('_'); cells.append((str(root),int(s[-2]),int(s[-1]),a.out_root))
 total=0
 with ProcessPoolExecutor(max_workers=a.workers) as ex:
  for i,f in enumerate(as_completed([ex.submit(work,c) for c in cells]),1):
   total+=f.result()
   if i%500==0: print(f'{i}/{len(cells)} replaced={total}',flush=True)
 print('replaced_blends_street',total)
if __name__=='__main__': raise SystemExit(main())
