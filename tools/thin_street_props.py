#!/usr/bin/env python3
"""Remove half of the decorative street props for the final optimization pass."""
from __future__ import annotations
import argparse, shutil, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from pzmapstudio.pzlot import read_header, read_cell_records, rewrite_cell
PROPS={'furniture_seating_outdoor_01_0','furniture_tables_low_01_0','furniture_seating_indoor_01_0','lighting_outdoor_01_0'}
def work(args):
 root,cx,cy,outroot=args; p=Path(root); h=p/f'{cx}_{cy}.lotheader'
 if not h.exists(): return 0
 if not any(n in PROPS for n in read_header(h).names): return 0
 overrides={}; removed=0
 for x,y,z,room,names in read_cell_records(p,cx,cy):
  if not any(n in PROPS for n in names): continue
  if (x*13+y*7)%2!=0: continue
  kept=[n for n in names if n not in PROPS]
  if kept:
   overrides[(x,y,z)]=kept; removed+=1
 if not overrides: return 0
 out=Path(outroot)/f'{cx}_{cy}'
 if out.exists(): shutil.rmtree(out)
 rewrite_cell(p,out,cx,cy,overrides)
 for name in (f'{cx}_{cy}.lotheader',f'world_{cx}_{cy}.lotpack'):
  shutil.copy2(out/name,p/name)
 shutil.rmtree(out); return removed
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--maps-root',required=True); ap.add_argument('--workers',type=int,default=12); ap.add_argument('--out-root',default='examples/thin-tmp'); a=ap.parse_args()
 root=Path(a.maps_root); total=0
 for m in sorted(p for p in root.iterdir() if p.is_dir() and list(p.glob('*.lotheader'))):
  cells=[]
  for h in m.glob('*.lotheader'):
   s=h.stem.split('_'); cells.append((str(m),int(s[-2]),int(s[-1]),a.out_root))
  with ProcessPoolExecutor(max_workers=a.workers) as ex:
   for f in as_completed([ex.submit(work,c) for c in cells]): total+=f.result()
 print('removed_props',total)
if __name__=='__main__': raise SystemExit(main())
