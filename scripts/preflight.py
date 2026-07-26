#!/usr/bin/env python3
"""Fail-fast checks that do not launch a DFT calculation."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


for package in ("ase", "numpy", "matplotlib", "sisl"):
    try:
        module = __import__(package)
        print(f"{package}: {getattr(module, '__version__', 'version unavailable')}")
    except ImportError as exc:
        fail(f"Python package {package!r} is unavailable: {exc}")

exe = os.environ.get("SIESTA_EXE", "siesta")
resolved = shutil.which(exe)
if not resolved:
    fail(
        f"SIESTA executable {exe!r} was not found. Run 00_diagnose.sh and "
        "update SIESTA_MODULES/SIESTA_EXE in config/narval.env."
    )
print(f"SIESTA executable: {resolved}")

pseudo_value = os.environ.get("SIESTA_PSEUDO_DIR", "pseudopotentials")
pseudo_dir = Path(pseudo_value)
if not pseudo_dir.is_absolute():
    pseudo_dir = ROOT / pseudo_dir
if not pseudo_dir.is_dir():
    fail(f"Pseudopotential directory does not exist: {pseudo_dir}")

files = [p for p in pseudo_dir.iterdir() if p.is_file()]
for symbol in ("C", "H", "Ni"):
    matches = [p for p in files if p.name.lower().startswith(symbol.lower() + ".")]
    if not matches:
        fail(
            f"No {symbol} pseudopotential found in {pseudo_dir}. ASE normally "
            f"expects a filename beginning with {symbol}."
        )
    print(f"{symbol} candidates: {', '.join(sorted(p.name for p in matches))}")

for relative in (
    "results/raw",
    "results/data",
    "results/figures",
    "results/structures",
    "results/logs",
):
    (ROOT / relative).mkdir(parents=True, exist_ok=True)

print("Preflight passed. Next submit stage 00_single_point.")

