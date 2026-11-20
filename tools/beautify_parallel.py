#!/usr/bin/env python3
"""Parallel, memory-capped beautify by launching one subprocess per cell."""
from __future__ import annotations

import argparse
import fcntl
import resource
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-map", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--memory-gb", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args()
    source = Path(args.source_map)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    lock = open(out / ".beautify.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("already running", flush=True)
        return 2
    headers = [h for h in sorted(source.glob("*.lotheader"))
               if not (out / h.name).exists()]
    print(f"todo={len(headers)} workers={args.workers}", flush=True)

    def limit():
        n = args.memory_gb * 1024 ** 3
        resource.setrlimit(resource.RLIMIT_AS, (n, n))

    done = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {}
        for header in headers:
            cmd = [sys.executable, str(ROOT / "tools" / "beautify_map.py"),
                   "--source-map", str(source), "--out", str(out),
                   "--only-cell", header.stem, "--workers", "1"]
            futures[pool.submit(subprocess.run, cmd, cwd=ROOT,
                                timeout=args.timeout, capture_output=True,
                                text=True, preexec_fn=limit)] = header.stem
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                if result.returncode != 0:
                    failed += 1
                    print(f"FAIL {name} rc={result.returncode} {result.stderr[-200:]}", flush=True)
                else:
                    done += 1
            except Exception as error:
                failed += 1
                print(f"FAIL {name} {error}", flush=True)
            if (done + failed) % 20 == 0:
                print(f"{done + failed}/{len(headers)} done={done} failed={failed}", flush=True)
    print(f"finished done={done} failed={failed}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
