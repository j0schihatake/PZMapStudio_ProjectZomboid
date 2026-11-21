#!/usr/bin/env python3
"""Place vanilla benches, tables, chairs and lamps along compiled sidewalks."""
from __future__ import annotations

import argparse
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.pzlot import read_header, read_cell_records, rewrite_cell

SIDEWALK = ('floors_exterior_street_01_0',)
PROPS = [
    'furniture_seating_outdoor_01_0',
    'furniture_tables_low_01_0',
    'furniture_seating_indoor_01_0',
    'lighting_outdoor_01_0',
]
BLOCK = ('walls_', 'floors_interior', 'fixtures_doors')


def work(args):
    root, cx, cy, out_root = args
    p = Path(root)
    h = p / f'{cx}_{cy}.lotheader'
    if not h.exists():
        return 0
    names_h = read_header(h).names
    if not any(n in names_h for n in SIDEWALK):
        return 0
    records = list(read_cell_records(p, cx, cy))
    by = {(x, y, z): names for x, y, z, _room, names in records}
    overrides = {}
    placed = 0
    for i, ((x, y, z), names) in enumerate(sorted(by.items())):
        if not any(n in SIDEWALK for n in names):
            continue
        if any(n.startswith(BLOCK) for n in names):
            continue
        # Sparse, deterministic street furniture.
        if (x * 31 + y * 17) % 53 != 0:
            continue
        prop = PROPS[(x + y) % len(PROPS)]
        if prop in names:
            continue
        overrides[(x, y, z)] = names + [prop]
        placed += 1
    if not overrides:
        return 0
    out = Path(out_root) / f'{cx}_{cy}'
    if out.exists():
        shutil.rmtree(out)
    rewrite_cell(p, out, cx, cy, overrides)
    for name in (f'{cx}_{cy}.lotheader', f'world_{cx}_{cy}.lotpack'):
        shutil.copy2(out / name, p / name)
    shutil.rmtree(out)
    return placed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--maps-root', required=True)
    ap.add_argument('--workers', type=int, default=12)
    ap.add_argument('--out-root', default='examples/streetprops-tmp')
    a = ap.parse_args()
    root = Path(a.maps_root)
    maps = [p for p in sorted(root.iterdir()) if p.is_dir() and list(p.glob('*.lotheader'))]
    total = 0
    for m in maps:
        cells = []
        for h in m.glob('*.lotheader'):
            s = h.stem.split('_')
            cells.append((str(m), int(s[-2]), int(s[-1]), a.out_root))
        print('===', m.name, flush=True)
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            for i, f in enumerate(as_completed([ex.submit(work, c) for c in cells]), 1):
                total += f.result()
                if i % 200 == 0:
                    print(f'{i}/{len(cells)} props={total}', flush=True)
    print('street_props', total)


if __name__ == '__main__':
    raise SystemExit(main())
