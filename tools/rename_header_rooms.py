#!/usr/bin/env python3
"""Rename room labels in a compiled map without changing cells or pack data."""
from __future__ import annotations

import argparse
import shutil
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pzmapstudio.pzlot import read_header, read_header_full


def rewrite_header(path: Path, rename: dict[str, str], out: Path) -> int:
    header = read_header(path)
    _h, rooms, buildings = read_header_full(path)
    changed = 0
    data = bytearray(b"LOTH")
    data += struct.pack("<i", header.version)
    data += struct.pack("<i", len(header.names))
    for name in header.names:
        data += name.encode("latin-1", errors="replace") + b"\n"
    data += struct.pack("<4i", header.chunk_width, header.chunk_height,
                        header.low, header.high)
    data += struct.pack("<i", len(rooms))
    for name, z, rects in rooms:
        new = rename.get(name, name)
        if new != name:
            changed += 1
        data += new.encode("latin-1", errors="replace") + b"\n"
        data += struct.pack("<2i", z, len(rects))
        for rect in rects:
            data += struct.pack("<4i", *rect)
        data += struct.pack("<i", 0)  # our generated rooms have no objects
    data += struct.pack("<i", len(buildings))
    for ids in buildings:
        data += struct.pack("<i", len(ids))
        data += struct.pack(f"<{len(ids)}i", *ids)
    data += b"\0" * 1024
    out.write_bytes(bytes(data))
    return changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rename", required=True, help="old=new,old2=new2")
    args = ap.parse_args()
    pairs = dict(part.split("=", 1) for part in args.rename.split(",") if "=" in part)
    src = Path(args.map)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    for h in sorted(src.glob("*.lotheader")):
        temp = out / h.name
        total += rewrite_header(h, pairs, temp)
    # copy packs and other metadata; headers are replaced
    for f in src.iterdir():
        if f.suffix not in (".lotheader",) and f.name != "spawnpoints.lua":
            if f.is_file():
                shutil.copy2(f, out / f.name)
    print("renamed_rooms", total, "cells", len(list(src.glob("*.lotheader"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
