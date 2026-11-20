#!/usr/bin/env python3
"""Copy finished maps into one mod folder and validate that cells are unique."""
from __future__ import annotations

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--maps-root", required=True,
                        help="folder containing finished map folders")
    parser.add_argument("--dest", required=True,
                        help="mod's common/media/maps folder")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    source = Path(args.maps_root)
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    owners = defaultdict(list)
    for map_dir in source.iterdir():
        if not map_dir.is_dir() or not list(map_dir.glob("*.lotheader")):
            continue
        target = dest / map_dir.name
        if target.exists():
            if not args.force:
                print(f"exists, skipping {target}")
                continue
            shutil.rmtree(target)
        shutil.copytree(map_dir, target, ignore=shutil.ignore_patterns("lots", "*.zip"))
        for header in target.glob("*.lotheader"):
            parts = header.stem.split("_")
            owners[(int(parts[-2]), int(parts[-1]))].append(map_dir.name)
        print(f"added {map_dir.name}")
    conflicts = {key: names for key, names in owners.items() if len(names) > 1}
    manifest = {
        "cells": len(owners),
        "conflicts": len(conflicts),
        "maps": {
            map_dir.name: len(list((dest / map_dir.name).glob("*.lotheader")))
            for map_dir in source.iterdir()
            if map_dir.is_dir() and (dest / map_dir.name).is_dir()
        },
    }
    (dest.parent / "MAP_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"cells={len(owners)} conflicts={len(conflicts)}")
    if conflicts:
        for key, names in list(conflicts.items())[:10]:
            print("conflict", key, names)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
