#!/usr/bin/env python3
"""Run beautify one cell per subprocess, skipping cells that crash/OOM."""
from __future__ import annotations

import argparse
import resource
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-map", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--memory-gb", type=int, default=4)
    args = parser.parse_args()
    source = Path(args.source_map)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    headers = sorted(source.glob("*.lotheader"))
    skipped = []
    done = 0
    for index, header in enumerate(headers, 1):
        if (out / header.name).exists():
            continue
        cmd = [
            sys.executable, str(ROOT / "tools" / "beautify_map.py"),
            "--source-map", str(source), "--out", str(out),
            "--only-cell", header.stem, "--workers", "1",
        ]
        def limit_memory():
            limit = args.memory_gb * 1024 ** 3
            resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        try:
            result = subprocess.run(cmd, cwd=ROOT, timeout=args.timeout,
                                    capture_output=True, text=True,
                                    preexec_fn=limit_memory)
            if result.returncode != 0:
                skipped.append((header.stem, result.returncode, result.stderr[-300:]))
            else:
                done += 1
        except subprocess.TimeoutExpired:
            skipped.append((header.stem, "timeout", ""))
        if index % 10 == 0 or (out / header.name).exists():
            print(f"{index}/{len(headers)} done={done} skipped={len(skipped)}", flush=True)
    if skipped:
        print("SKIPPED:")
        for item in skipped:
            print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
