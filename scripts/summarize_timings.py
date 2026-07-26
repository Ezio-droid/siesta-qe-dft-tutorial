#!/usr/bin/env python3
"""Summarize all completed benchmark timing reports."""

import json
from pathlib import Path

root = Path(__file__).resolve().parent
reports = []
for path in sorted((root / "timings").glob("*.json")):
    report = json.loads(path.read_text())
    reports.append(
        {
            "segment": path.stem,
            "status": report["status"],
            "wall_seconds": report["wall_seconds"],
            "error": report.get("error"),
        }
    )

summary = {
    "segments": reports,
    "total_executed_wall_seconds": sum(
        item["wall_seconds"] for item in reports
    ),
    "all_available_segments_succeeded": all(
        item["status"] == "succeeded" for item in reports
    ),
}
(root / "timings" / "summary.json").write_text(
    json.dumps(summary, indent=2) + "\n"
)
print(json.dumps(summary, indent=2))
