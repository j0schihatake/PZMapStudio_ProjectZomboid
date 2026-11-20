#!/usr/bin/env python3
"""Append a live command for PZMapStudio and optionally print new responses."""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--op", required=True,
                   choices=["observe", "horde", "loot", "story", "weather", "door"])
    p.add_argument("--kind", default="")
    p.add_argument("--item", default="Base.Bandage")
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--x", type=int, default=0)
    p.add_argument("--y", type=int, default=0)
    p.add_argument("--z", type=int, default=0)
    p.add_argument("--seconds", type=float, default=60)
    p.add_argument("--open", action="store_true")
    p.add_argument("--wait", type=float, default=0,
                   help="seconds to wait and print responses")
    args = p.parse_args()
    base = Path(os.environ.get("PZMAPSTUDIO_DIR",
                               Path.home() / "Zomboid" / "PZMapStudio"))
    base.mkdir(parents=True, exist_ok=True)
    cmd = {"op": args.op}
    if args.kind:
        cmd["kind"] = args.kind
    if args.op == "loot":
        cmd["item"] = args.item
        cmd["count"] = args.count
    if args.op == "horde":
        cmd["count"] = args.count
    if args.op in ("story", "door"):
        cmd["x"], cmd["y"] = args.x, args.y
    if args.op == "door":
        cmd["z"] = args.z
        cmd["open"] = args.open
    if args.op == "weather":
        cmd["seconds"] = args.seconds
    with (base / "queue.jsonl").open("a") as fh:
        fh.write(json.dumps(cmd) + "\n")
    print("queued", json.dumps(cmd))
    if args.wait:
        time.sleep(args.wait)
        response = base / "responses.jsonl"
        if response.exists():
            print(response.read_text()[-2000:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
