#!/usr/bin/env python3
"""Build a source release zip for PZMapStudio (GitHub Release/PyPI-friendly)."""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ["pyproject.toml", "README.md", "ART_PLAN.md", "AGENT_API.md",
         "REFERENCES.md", "ROOF_TRACE.md", "ADDRESS_LOOKUP.md", "ROADMAP.md"]


def main() -> int:
    version = "0.1.0"
    match = re.search(r'version\s*=\s*"([^"]+)"', (ROOT / "pyproject.toml").read_text())
    if match:
        version = match.group(1)
    out = ROOT / "dist" / f"PZMapStudio-v{version}.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            path = ROOT / name
            if path.exists():
                archive.write(path, name)
        for path in sorted((ROOT / "pzmapstudio").rglob("*.py")):
            archive.write(path, path.relative_to(ROOT))
        for path in sorted((ROOT / "tests").rglob("*.py")):
            archive.write(path, path.relative_to(ROOT))
        for path in sorted((ROOT / "tools").rglob("*.py")):
            archive.write(path, path.relative_to(ROOT))
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
