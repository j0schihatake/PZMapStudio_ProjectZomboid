#!/usr/bin/env python3
"""Merge completed beautify outputs into the map mod, validating each map."""
from __future__ import annotations

import argparse
import shutil
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pzmapstudio.validate import validate_map


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-maps", required=True,
                        help="installed map folder with originals")
    parser.add_argument("--beautify-root", required=True)
    parser.add_argument("--dest", required=True)
    args = parser.parse_args()
    source = Path(args.source_maps)
    beautify = Path(args.beautify_root)
    dest = Path(args.dest)
    owners = defaultdict(set)
    for candidate in sorted(beautify.iterdir()):
        if not candidate.is_dir():
            continue
        name = candidate.name.removeprefix("beautify-")
        # Map the output folder to the original by matching cell counts.
        originals = [p for p in source.iterdir() if p.is_dir()]
        match = None
        for original in originals:
            if len(list(original.glob("*.lotheader"))) == len(list(candidate.glob("*.lotheader"))):
                if original.name.lower().split(",")[0][:5] in name.lower():
                    match = original
                    break
        if match is None:
            print("skip (no match)", candidate.name)
            continue
        target = dest / match.name
        report = validate_map(candidate)
        if not report["ok"]:
            print("skip invalid", candidate.name, report["errors"][:2])
            continue
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(candidate, target)
        print("merged", match.name, report["cells"])
        for header in target.glob("*.lotheader"):
            owners[header.stem].add(match.name)
    conflicts = {k: v for k, v in owners.items() if len(v) > 1}
    print("cells", len(owners), "conflicts", len(conflicts))
    return 1 if conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
