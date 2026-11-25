#!/usr/bin/env python3
"""Overlay later street tiles and street furniture onto current cells, preserving walls/floors."""
from __future__ import annotations
import argparse, shutil, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from pzmapstudio.pzlot import read_cell_records, rewrite_cell
STREET_PREFIX=('floors_exterior_street','blends_street','street_','street_trafficlines')
PROPS=('furniture_seating_outdoor','furniture_tables_low','furniture_seating_indoor','lighting_outdoor')
def street(n): return n.startswith(STREET_PREFIX)
def prop(n): return n.startswith(PROPS)
def work(args):
 cur,later,cx,cy,outroot=args; cur=Path(cur); later=Path(later); outroot=Path(outroot)
 if not (cur/f'{cx}_{cy}.lotheader').exists() or not (later/f'{cx}_{cy}.lotheader').exists(): return (0,0)
 by={(x,y,z):ns for x,y,z,_,ns in read_cell_records(cur,cx,cy)}
 lat={(x,y,z):ns for x,y,z,_,ns in read_cell_records(later,cx,cy)}
 overrides={}; roads=props=0
 for k,lns in lat.items():
  cns=by.get(k)
  if not cns: continue
  if any(n.startswith(('walls_','floors_interior')) for n in cns): continue
  add=[n for n in lns if (street(n) or prop(n))]
  if not add: continue
  keep=[n for n in cns if not (street(n) or prop(n))]
  new=keep+[n for n in add if n not in keep]
  if new!=cns:
   overrides[k]=new; roads+=sum(1 for n in add if street(n)); props+=sum(1 for n in add if prop(n))
 if not overrides: return (0,0)
 out=outroot/f'{cx}_{cy}'
 if out.exists(): shutil.rmtree(out)
 rewrite_cell(cur,out,cx,cy,overrides)
 for n in (f'{cx}_{cy}.lotheader',f'world_{cx}_{cy}.lotpack'): shutil.copy2(out/n,cur/n)
 shutil.rmtree(out); return (roads,props)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--current',required=True); ap.add_argument('--later',required=True); ap.add_argument('--workers',type=int,default=8); ap.add_argument('--out-root',default='examples/overlay-roads-tmp'); a=ap.parse_args()
 cur=Path(a.current); later=Path(a.later); cells=[]
 for h in cur.glob('*.lotheader'):
  p=h.stem.split('_'); cells.append((str(cur),str(later),int(p[-2]),int(p[-1]),a.out_root))
 tr=tp=0
 with ProcessPoolExecutor(max_workers=a.workers) as ex:
  for i,f in enumerate(as_completed([ex.submit(work,c) for c in cells]),1):
   r,p=f.result(); tr+=r; tp+=p
   if i%500==0: print(i,'/',len(cells),'roads',tr,'props',tp,flush=True)
 print('TOTAL roads',tr,'props',tp)
if __name__=='__main__': raise SystemExit(main())
