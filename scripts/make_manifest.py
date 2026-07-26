#!/usr/bin/env python3
"""Create a checksum manifest for GitHub-sized reproducibility files."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
included = [
    ROOT / "results" / "data",
    ROOT / "results" / "figures",
    ROOT / "results" / "structures",
    ROOT / "results" / "logs",
    ROOT / "environment",
    ROOT / "config",
    ROOT / "scripts",
    ROOT / "slurm",
]
records = []
for base in included:
    for path in sorted(p for p in base.rglob("*") if p.is_file()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        records.append(
            {
                "path": str(path.relative_to(ROOT)),
                "size_bytes": path.stat().st_size,
                "sha256": digest,
            }
        )
manifest = {
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "files": records,
}
(ROOT / "results" / "manifest.json").write_text(
    json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
)
print(f"Wrote results/manifest.json with {len(records)} files.")

