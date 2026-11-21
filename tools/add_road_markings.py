#!/usr/bin/env python3
"""Add vanilla traffic-line floor overlays to compiled road squares."""
from __future__ import annotations

import argparse, shutil, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from pzmapstudio.pzlot import read_header, read_cell_records, rewrite_cell

LINE='street_trafficlines_01_0'

def is_road(n:str)->bool:
    n=n.lower()
    return n.startswith(('floors_exterior_street','blends_street')) or 'asphalt' in n

def work(args):
    root,cx,cy,outroot=args; p=Path(root)
    h=p/f'{cx}_{cy}.lotheader'
    if not h.exists(): return 0
    header=read_header(h)
    if not any(is_road(n) for n in header.names): return 0
    if LINE in header.names: return 0
    overrides={}
    for x,y,z,room,names in read_cell_records(p,cx,cy):
        if any(is_road(n) for n in names) and LINE not in names:
            overrides[(x,y,z)] = names+[LINE]
    if not overrides: return 0
    out=Path(outroot)/f'{cx}_{cy}'
    if out.exists(): shutil.rmtree(out)
    rewrite_cell(p,out,cx,cy,overrides)
    for name in (f'{cx}_{cy}.lotheader',f'world_{cx}_{cy}.lotpack'):
        shutil.copy2(out/name,p/name)
    shutil.rmtree(out)
    return len(overrides)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--map',required=True); ap.add_argument('--workers',type=int,default=8); ap.add_argument('--out-root',default='examples/roadlines-tmp'); a=ap.parse_args()
    root=Path(a.map); cells=[]
    for h in root.glob('*.lotheader'):
        s=h.stem.split('_'); cells.append((str(root),int(s[-2]),int(s[-1]),a.out_root))
    total=0
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for i,f in enumerate(as_completed([ex.submit(work,c) for c in cells]),1):
            total+=f.result()
            if i%200==0: print(f'{i}/{len(cells)} markings={total}',flush=True)
    print('added_road_markings',total)
if __name__=='__main__': raise SystemExit(main())
