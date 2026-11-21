#!/usr/bin/env python3
"""Audit key gameplay elements (weapons, food, medical, police, schools)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.pzlot import read_header_full

KEYS = {
    "weapons": ("gun", "weapon", "armory", "arms"),
    "food": ("food", "grocery", "market", "kitchen", "bakery"),
    "medical": ("medical", "clinic", "hospital", "pharmacy", "ward", "exam"),
    "police": ("police", "sheriff", "courthouse", "jail"),
    "school": ("school", "classroom", "library"),
    "religion": ("church", "chapel", "mosque", "nave", "altar"),
    "military": ("army", "military", "base", "barracks", "command"),
    "warehouse": ("warehouse", "storage", "depot"),
}


def audit(map_dir: Path) -> dict:
    counts = {key: 0 for key in KEYS}
    samples = {key: [] for key in KEYS}
    cells = 0
    rooms = 0
    for h in map_dir.glob("*.lotheader"):
        try:
            _header, room_list, _buildings = read_header_full(h)
        except Exception:
            continue
        cells += 1
        parts = h.stem.split("_")
        cx, cy = int(parts[-2]), int(parts[-1])
        for name, z, _rects in room_list:
            rooms += 1
            lower = name.lower()
            for key, words in KEYS.items():
                if any(word in lower for word in words):
                    counts[key] += 1
                    if len(samples[key]) < 3:
                        samples[key].append([name, cx, cy, z])
    return {"map": map_dir.name, "cells": cells, "rooms": rooms,
            "counts": counts, "samples": samples}


def main() -> int:
    roots = [
        Path("/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/omsk-expansion/common/media/maps"),
        Path("/home/j0schi/SteamLibrary/steamapps/common/ProjectZomboid/work/KnoxMap-dev/dist/sod2-expansion/common/media/maps"),
    ]
    report = []
    for root in roots:
        for map_dir in sorted(p for p in root.iterdir() if p.is_dir() and list(p.glob("*.lotheader"))):
            row = audit(map_dir)
            report.append(row)
            print(json.dumps(row, ensure_ascii=False))
    out = Path("examples/key-elements-audit.json")
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
