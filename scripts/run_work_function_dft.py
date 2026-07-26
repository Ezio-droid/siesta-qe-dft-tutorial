#!/usr/bin/env python3
"""Run only the SIESTA portion of a work-function calculation."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from ase.io import read

from run_stage import RAW, STRUCTURES, calculator, in_directory, require

CASES = {
    "h_slab": {
        "stage": "10_h_slab_work_function",
        "structure": "h_slab_high_optimized.traj",
        "producer": "08_h_slab_high_opt",
    },
    "pristine_slab": {
        "stage": "11_pristine_slab_work_function",
        "structure": "pristine_slab_optimized.traj",
        "producer": "05_slab_opt",
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=sorted(CASES))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    case = CASES[args.case]
    stage_dir = RAW / case["stage"]
    marker = stage_dir / "dft_complete.json"
    if marker.exists() and not args.force:
        raise SystemExit(
            f"DFT is already marked complete: {marker}. "
            "Use --force only for an intentional recalculation."
        )
    stage_dir.mkdir(parents=True, exist_ok=True)
    atoms = read(
        require(STRUCTURES / case["structure"], case["producer"])
    )
    atoms.pbc = True
    started = datetime.now(timezone.utc)
    with in_directory(stage_dir):
        atoms.calc = calculator(
            "slab",
            kpts=(5, 5, 1),
            extra_fdf={
                "WriteEigenvalues": True,
                "SaveHS": True,
                "SaveElectrostaticPotential": True,
                "WriteVH": True,
            },
        )
        energy = float(atoms.get_potential_energy())
    finished = datetime.now(timezone.utc)
    payload = {
        "stage": case["stage"],
        "case": args.case,
        "started_utc": started.isoformat(),
        "finished_utc": finished.isoformat(),
        "duration_seconds": (finished - started).total_seconds(),
        "energy_eV": energy,
        "postprocessing": "pending",
    }
    marker.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

