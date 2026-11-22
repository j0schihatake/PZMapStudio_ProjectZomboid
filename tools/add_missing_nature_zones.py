#!/usr/bin/env python3
"""Add the remaining nature/Nav zones to SoD cells that contain no buildings."""
from pathlib import Path
import re, sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from pzmapstudio.pzlot import read_cell_records
ROOT=Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/sod2-expansion/common/media/maps')
def zone(t,x,y,w,h): return f'  {{ name = "", type = "{t}", x = {x}, y = {y}, z = 0, width = {w}, height = {h} }},'
for m in sorted(p for p in ROOT.iterdir() if p.is_dir()):
 p=m/'objects.lua'; s=p.read_text(errors='replace')
 have=set(re.findall(r'type = "([^"]+)"',s))
 if {'Forest','DeepForest','Vegitation','Nav'} <= have: continue
 nature=None; road=None
 for h in m.glob('*.lotheader'):
  mm=re.match(r'(\d+)_(\d+)\.lotheader$',h.name)
  if not mm: continue
  cx,cy=int(mm.group(1)),int(mm.group(2)); recs=list(read_cell_records(m,cx,cy))
  if not recs: continue
  names=[n for _,_,_,_,ns in recs for n in ns]
  if not road and any(n.startswith('floors_exterior_street') or n.startswith('blends_street') for n in names): road=(cx,cy)
  if not nature and not any(n.startswith(('walls_','floors_interior')) for n in names): nature=(cx,cy)
  if road and nature: break
 add=[]
 if nature:
  x,y=nature; add += [zone('Vegitation',x*256,y*256,256,256),zone('Forest',x*256,y*256,256,256),zone('DeepForest',x*256,y*256,256,256)]
 if road:
  x,y=road; add.append(zone('Nav',x*256,y*256,256,256))
 if add:
  s=s.replace('  }\nend', '\n'.join(add)+'\n  }\nend',1)
  p.write_text(s); print(m.name,'+',len(add))
