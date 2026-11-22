#!/usr/bin/env python3
"""Report whether each custom map has usable ParkingStall vehicle zones."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
ROOTS = [
    Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/omsk-expansion/common/media/maps'),
    Path('/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/sod2-expansion/common/media/maps'),
]
def main() -> int:
    report = {}
    for root in ROOTS:
        if not root.is_dir(): continue
        for mapdir in sorted(p for p in root.iterdir() if p.is_dir()):
            objects = mapdir / 'objects.lua'
            text = objects.read_text(errors='replace') if objects.is_file() else ''
            stalls = len(re.findall(r'ParkingStall', text, re.I))
            jams = len(re.findall(r'TrafficJam|trafficjam', text, re.I))
            report[mapdir.name] = {'objects_lua': objects.is_file(), 'parkingstall': stalls, 'trafficjam': jams}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0
if __name__ == '__main__': raise SystemExit(main())
