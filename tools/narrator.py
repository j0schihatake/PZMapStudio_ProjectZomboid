#!/usr/bin/env python3
"""A tiny external storyteller loop for PZMapStudio's file queue.

It observes nearby zombies/items and occasionally asks the in-game Java mod for
a camp, crime scene or weather change. Run it while the game is open.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

BASE = Path(os.environ.get("PZMAPSTUDIO_DIR", Path.home() / "Zomboid" / "PZMapStudio"))


def queued(cmd: dict) -> None:
    with (BASE / "queue.jsonl").open("a") as fh:
        fh.write(json.dumps(cmd) + "\n")


def last_response() -> dict | None:
    path = BASE / "responses.jsonl"
    if not path.exists():
        return None
    lines = [line for line in path.read_text().splitlines() if line.strip()]
    if not lines:
        return None
    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=float, default=10)
    args = parser.parse_args()
    BASE.mkdir(parents=True, exist_ok=True)
    last_story = 0.0
    while True:
        queued({"op": "observe"})
        time.sleep(3)
        response = last_response()
        if response:
            result = response.get("result", "")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    result = {}
            zombies = result.get("zombiesNear", 0) if isinstance(result, dict) else 0
            items = result.get("itemsNear", 0) if isinstance(result, dict) else 0
            if time.time() - last_story > 90:
                if zombies >= 6:
                    queued({"op": "weather", "kind": "fog", "seconds": 60})
                    last_story = time.time()
                elif items >= 8:
                    queued({"op": "story", "kind": "crime", "x": int(result.get("x", 0)),
                            "y": int(result.get("y", 0)), "cooldown": 60})
                    last_story = time.time()
                else:
                    queued({"op": "story", "kind": "camp", "x": int(result.get("x", 0)),
                            "y": int(result.get("y", 0)), "cooldown": 60})
                    last_story = time.time()
        if args.once:
            break
        time.sleep(args.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
