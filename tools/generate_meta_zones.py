#!/usr/bin/env python3
"""Generate coarse but valid B42 meta zones from compiled map headers.

The generator deliberately does not invent Suburbs/story GUIDs. It fills the
zones that are safe to derive from tiles: TownZone, Vegitation, Forest,
DeepForest, Nav, LootZone, ZombiesType, SpawnPoint, ParkingStall and trafficjam.
"""
from __future__ import annotations
import re, sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from pzmapstudio.pzlot import read_header
MAPS=[
 Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/omsk-expansion/common/media/maps/Omsk_World'),
 Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/sod2-expansion/common/media/maps'),
]
def kind(names):
    n=' '.join(names).lower()
    if 'floors_interior' in n or 'walls_' in n or 'fixtures_' in n: return 'town'
    if 'street' in n or 'road' in n or 'asphalt' in n: return 'road'
    if 'forest' in n: return 'forest'
    if 'foliage' in n: return 'forest'
    if 'water_' in n: return 'water'
    if 'vegetation' in n or 'grass' in n or 'bush' in n: return 'veg'
    return None
def runs(cells):
    by=defaultdict(list)
    for x,y in cells: by[y].append(x)
    out=[]
    for y,xs in by.items():
        xs=sorted(set(xs)); start=prev=xs[0]
        for x in xs[1:]:
            if x!=prev+1:
                out.append((start,y,prev-start+1)); start=x
            prev=x
        out.append((start,y,prev-start+1))
    return out
def spawnpoints(mapdir):
    out=[]
    for f in mapdir.glob('spawnpoints*.lua'):
        for x,y in re.findall(r'posX\s*=\s*(\d+).*?posY\s*=\s*(\d+)', f.read_text()):
            out.append((int(x),int(y)))
    return out
def zone(name,typ,x,y,w,h,props=None):
    p=''
    if props: p=', properties = { '+props+' }'
    return f'  {{ name = "{name}", type = "{typ}", x = {x}, y = {y}, z = 0, width = {w}, height = {h}{p} }},'
def generate(mapdir):
    buckets=defaultdict(list)
    for h in mapdir.glob('*.lotheader'):
        m=re.match(r'(-?\d+)_(-?\d+)\.lotheader$',h.name)
        if not m: continue
        cx,cy=int(m.group(1)),int(m.group(2)); k=kind(read_header(h).names)
        if k: buckets[k].append((cx,cy))
    lines=[]; stories=0; tone_done=False; extras_done=False
    for x,y,w in runs(buckets['town']):
        lines.append(zone('','TownZone',x*256,y*256,w*256,256))
        lines.append(zone('Offices','ZombiesType',x*256,y*256,w*256,256))
        lines.append(zone('Rich' if (x+y)%3 else 'Poor','LootZone',x*256,y*256,w*256,256))
        if stories < 4:
            lines.append(zone('NewsStory','ZoneStory',x*256+4,y*256+4,1,1)); stories += 1
        if not tone_done:
            lines.append(zone('','RoomTone',x*256+4,y*256+4,1,1,'RoomTone = "Generic", EntireBuilding = true')); tone_done=True
        if not extras_done:
            lines.append(zone('','Mannequin',x*256+12,y*256+12,1,1,'Direction = "N", Script = "MannequinScarecrow01"'))
            lines.append(f'  {{ name = "", type = "Animal", z = 0, geometry = "polyline", points = {{ {x*256+30}, {y*256+30}, {x*256+36}, {y*256+36}, {x*256+30}, {y*256+42} }}, properties = {{ AnimalType = "rabbit", Action = "Follow", SpawnAnimals = true }} }},')
            extras_done=True
        lines.append(zone('parkingstall','ParkingStall',x*256+8,y*256+8,3,5,'Direction = "N"'))
    for x,y,w in runs(buckets['road']):
        lines.append(zone('','Nav',x*256,y*256,w*256,256))
        if stories < 8:
            lines.append(zone('NewsStory','ZoneStory',x*256+4,y*256+4,1,1)); stories += 1
        if (x+y)%4==0: lines.append(zone('trafficjame','ParkingStall',x*256+4,y*256+4,3,3))
    for x,y,w in runs(buckets['veg']):
        lines.append(zone('','Vegitation',x*256,y*256,w*256,256))
        lines.append(zone('','Forest',x*256,y*256,w*256,256))
        lines.append(zone('','DeepForest',x*256,y*256,w*256,256))
    for x,y,w in runs(buckets['forest']):
        lines.append(zone('','Forest',x*256,y*256,w*256,256))
        if stories < 6:
            lines.append(zone('Forest','ZoneStory',x*256+4,y*256+4,1,1)); stories += 1
        lines.append(zone('','DeepForest',x*256,y*256,w*256,256))
        lines.append(zone('','Vegitation',x*256,y*256,w*256,256))
    for x,y,w in runs(buckets['water']):
        lines.append(zone('','WaterZone',x*256,y*256,w*256,256,'WaterGround = false, WaterShore = false'))
    for x,y in spawnpoints(mapdir):
        lines.append(zone('','SpawnPoint',x,y,1,1,'Professions = "all"'))
    # Keep existing parking lines, append generated lines.
    old=(mapdir/'objects.lua').read_text(errors='replace') if (mapdir/'objects.lua').exists() else ''
    existing=[]
    for line in old.splitlines():
        if 'type = "ParkingStall"' in line:
            existing.append(line.rstrip())
    seen=set(); body_lines=[]
    for line in existing+lines:
        line=line.rstrip()
        if line not in seen:
            seen.add(line); body_lines.append(line)
    body='\n'.join(body_lines)
    (mapdir/'objects.lua').write_text('function getObjectList()\n  return {\n'+body+'\n  }\nend\n')
    return len(lines)
for root in MAPS:
    maps=[root] if root.name!='maps' else [p for p in root.iterdir() if p.is_dir() and list(p.glob('*.lotheader'))]
    for m in maps:
        try: print(m.name, generate(m))
        except Exception as e: print('FAIL',m.name,e)
