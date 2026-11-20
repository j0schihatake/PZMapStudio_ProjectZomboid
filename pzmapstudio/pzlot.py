"""Minimal reader for compiled PZ .lotheader/.lotpack cells.

The format is little-endian and documented in KnoxMap's tools/render_lots.py:

    X_Y.lotheader     "LOTH", version, tile count, tile names,
                      chunk width, chunk height, min level, max level
    world_X_Y.lotpack "LOTP", version, 32*32 chunk offsets, chunk records

This module deliberately only reads. Encoding compiled lots is a separate
milestone; PZMapStudio first needs to import real terrain to edit it.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

CELL = 256
CHUNKS = 32
CHUNK = 8


@dataclass
class Header:
    names: list[str]
    low: int
    high: int
    chunk_width: int
    chunk_height: int


def read_header(path: str | Path) -> Header:
    data = Path(path).read_bytes()
    pos = 4 if data[:4] == b"LOTH" else 0
    pos += 4
    (count,) = struct.unpack_from("<i", data, pos)
    pos += 4
    names = []
    for _ in range(count):
        end = data.index(b"\n", pos)
        names.append(data[pos:end].decode("latin-1"))
        pos = end + 1
    chunk_width, chunk_height, low, high = struct.unpack_from("<4i", data, pos)
    return Header(names, low, high, chunk_width, chunk_height)


def iter_cell(map_dir: str | Path, cell_x: int, cell_y: int,
              max_level: int | None = None) -> Iterator[tuple[int, int, int, list[str]]]:
    """Yield (absolute tile x, y, z, tile names) for a compiled cell."""
    folder = Path(map_dir)
    header = read_header(folder / f"{cell_x}_{cell_y}.lotheader")
    pack_path = folder / f"world_{cell_x}_{cell_y}.lotpack"
    if not pack_path.exists():
        return
    data = pack_path.read_bytes()
    pos = 4 if data[:4] == b"LOTP" else 0
    pos += 4
    (n,) = struct.unpack_from("<i", data, pos)
    pos += 4
    offsets = struct.unpack_from(f"<{n}q", data, pos)
    high = header.high if max_level is None else min(header.high, max_level)
    for cx in range(CHUNKS):
        for cy in range(CHUNKS):
            p = offsets[cx * CHUNKS + cy]
            if p < 0:
                continue
            bx, by = cx * CHUNK, cy * CHUNK
            skip = 0
            for z in range(header.low, high + 1):
                for sx in range(CHUNK):
                    for sy in range(CHUNK):
                        if skip > 0:
                            skip -= 1
                            continue
                        (count,) = struct.unpack_from("<i", data, p)
                        p += 4
                        if count == -1:
                            (skip,) = struct.unpack_from("<i", data, p)
                            p += 4
                            skip -= 1
                            continue
                        _room = struct.unpack_from("<i", data, p)[0]
                        p += 4
                        if count <= 1:
                            continue
                        ids = struct.unpack_from(f"<{count - 1}i", data, p)
                        p += 4 * (count - 1)
                        names = []
                        for tile_id in ids:
                            if 0 <= tile_id < len(header.names):
                                names.append(header.names[tile_id])
                        if names:
                            yield cell_x * CELL + bx + sx, cell_y * CELL + by + sy, z, names


def classify_tile(names: list[str]) -> tuple[str, str]:
    """Return (layer, representative tile name) for a square."""
    joined = " ".join(names).lower()
    if any(word in joined for word in ("road", "asphalt", "pavement", "sidewalk", "kerb", "street")):
        return "roads", names[0]
    if any(word in joined for word in ("water", "river", "lake")):
        return "water", names[0]
    if any(word in joined for word in ("grass", "dirt", "forest", "ground", "earth")):
        return "terrain", names[0]
    return "terrain", names[0]
