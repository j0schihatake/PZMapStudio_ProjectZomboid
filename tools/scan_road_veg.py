from __future__ import annotations
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from pzmapstudio.pzlot import read_header, read_cell_records

def road(n):
 n=n.lower(); return n.startswith(('floors_exterior_street','blends_street','road')) or 'asphalt' in n
def veg(n):
 n=n.lower()
 if 'street' in n: return False
 return n.startswith(('blends_natural','blends_grassoverlays','vegetation_','floors_exterior_natural','e_','f_')) or 'bush' in n or n.startswith('tree')

def scan(args):
 root,cx,cy=args; p=Path(root); h=p/f'{cx}_{cy}.lotheader'
 names=read_header(h).names
 if not any(road(n) for n in names) or not any(veg(n) for n in names): return 0,0,[]
 count=0; samples=[]
 for x,y,z,room,tiles in read_cell_records(p,cx,cy):
  r=[n for n in tiles if road(n)]; v=[n for n in tiles if veg(n)]
  if r and v:
   count+=1
   if len(samples)<5: samples.append((x,y,tiles))
 return count,1,samples

def main():
 root=sys.argv[1]; cells=[]
 for h in Path(root).glob('*.lotheader'):
  p=h.stem.split('_'); cells.append((root,int(p[-2]),int(p[-1])))
 total=0; cellsn=0; samples=[]
 with ProcessPoolExecutor(max_workers=8) as ex:
  for f in as_completed([ex.submit(scan,c) for c in cells]):
   n,c,s=f.result(); total+=n; cellsn+=c; samples+=s
 print('squares',total,'cells',cellsn)
 for s in samples[:10]: print(s)
if __name__=='__main__': main()
