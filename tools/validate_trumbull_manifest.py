#!/usr/bin/env python3
"""Check required Trumbull landmark footprints in district scene JSONs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="trumbull-buildings.json")
    parser.add_argument("--examples", default="examples")
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    examples = Path(args.examples)
    failed = False
    for district, spec in manifest.items():
        scene_path = examples / f"trumbull-{district}.json"
        if not scene_path.exists():
            print(f"{district}: MISSING {scene_path}")
            failed = True
            continue
        scene = json.loads(scene_path.read_text())
        buildings = scene.get("buildings", [])
        for required in spec["required"]:
            found = None
            for building in buildings:
                if (building.get("x"), building.get("y"), building.get("w"), building.get("h")) == (
                        required["x"], required["y"], required["w"], required["h"]):
                    found = building
                    break
            if found is None:
                print(f"{district}: missing required {required['name']} at "
                      f"{required['x']},{required['y']} {required['w']}x{required['h']}")
                failed = True
            else:
                floors = len(found.get("floors", {}))
                if floors < required["floors"]:
                    print(f"{district}: {required['name']} has {floors} floors, need {required['floors']}")
                    failed = True
                else:
                    print(f"{district}: ok {required['name']} ({floors} floors)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
