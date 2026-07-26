#!/usr/bin/env python3
"""Execute a notebook, preserve partial output on failure, and report timings."""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def iso_now():
    return datetime.now(timezone.utc).isoformat()


def main():
    if len(sys.argv) != 4:
        raise SystemExit(
            "usage: execute_notebook.py INPUT.ipynb OUTPUT.ipynb TIMINGS.json"
        )

    source, output, timing_file = map(Path, sys.argv[1:])
    notebook = nbformat.read(source, as_version=4)
    started = iso_now()
    start_clock = time.monotonic()
    status = "succeeded"
    error = None

    run_dir = Path(
        os.environ.get("BENCHMARK_RUN_DIR", Path.cwd() / "benchmark" / "run")
    ).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    timing_file.parent.mkdir(parents=True, exist_ok=True)

    client = NotebookClient(
        notebook,
        timeout=None,
        kernel_name="python3",
        resources={"metadata": {"path": str(run_dir)}},
        record_timing=True,
        allow_errors=False,
    )

    try:
        client.execute()
    except Exception as exc:
        status = "failed"
        error = f"{type(exc).__name__}: {exc}"
    finally:
        finished = iso_now()
        elapsed = time.monotonic() - start_clock
        nbformat.write(notebook, output)

    cells = []
    for local_index, cell in enumerate(notebook.cells):
        timing = cell.get("metadata", {}).get("execution", {})
        cells.append(
            {
                "local_cell_index": local_index,
                "original_cell_index": cell.get("metadata", {}).get(
                    "original_cell_index"
                ),
                "cell_type": cell.cell_type,
                "started": timing.get("iopub.execute_input"),
                "finished": timing.get("iopub.status.idle"),
            }
        )

    report = {
        "notebook": source.name,
        "status": status,
        "error": error,
        "started_utc": started,
        "finished_utc": finished,
        "wall_seconds": elapsed,
        "cells": cells,
    }
    timing_file.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if status != "succeeded":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
