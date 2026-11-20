#!/usr/bin/env python3
"""Assemble, validate and report a finished PZ map mod."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pzmapstudio.layout import audit_layout
from pzmapstudio.save_audit import audit_map_root
from pzmapstudio.validate import validate_map


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--maps-root", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    subprocess.run([sys.executable, str(ROOT / "tools" / "assemble_mod.py"),
                    "--maps-root", args.maps_root, "--dest", args.dest]
                   + (["--force"] if args.force else []), check=True)
    maps = sorted(p for p in Path(args.dest).iterdir() if p.is_dir())
    report = {
        "layout": audit_layout(args.dest),
        "maps": {p.name: validate_map(p) for p in maps},
        "save_state": audit_map_root(Path(args.dest)).get("combined", {}),
    }
    out = Path(args.dest).parent / "FINAL_REPORT.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    all_ok = all(item["ok"] for item in report["maps"].values())
    print(json.dumps({"maps": len(maps), "all_valid": all_ok,
                      "report": str(out)}, indent=2))
    return 0 if all_ok and not report["layout"]["duplicate_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
