#!/usr/bin/env python3
"""Post-process an existing SIESTA work-function calculation.

Run this with Narval's GCC/OpenMPI mpi4py module loaded. It does not execute
SIESTA and is intentionally separated from the Intel-based DFT job.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sisl

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw"
DATA = ROOT / "results" / "data"
FIGURES = ROOT / "results" / "figures"

CASES = {
    "h_slab": {
        "stage": "10_h_slab_work_function",
        "prefix": "h_terminated_slab",
    },
    "pristine_slab": {
        "stage": "11_pristine_slab_work_function",
        "prefix": "pristine_slab",
    },
}


def parse_eigenvalues(path: Path):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if len(lines) < 3:
        raise RuntimeError(f"Unexpectedly short eigenvalue file: {path}")
    fermi = float(lines[0].split()[0])
    eigenvalues = []
    for line in lines[2:]:
        parts = line.split()
        if parts and re.fullmatch(r"[+-]?\d+", parts[0]):
            parts = parts[1:]
        for value in parts:
            try:
                eigenvalues.append(float(value))
            except ValueError:
                pass
    eigenvalues = np.asarray(eigenvalues)
    occupied = eigenvalues[eigenvalues < fermi]
    unoccupied = eigenvalues[eigenvalues > fermi]
    if occupied.size == 0 or unoccupied.size == 0:
        raise RuntimeError(
            f"Could not identify both occupied and unoccupied states in {path}"
        )
    return (
        float(fermi),
        float(occupied.max()),
        float(unoccupied.min()),
        int(eigenvalues.size),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=sorted(CASES))
    args = parser.parse_args()
    case = CASES[args.case]
    stage = case["stage"]
    prefix = case["prefix"]
    stage_dir = RAW / stage
    if not stage_dir.is_dir():
        raise FileNotFoundError(f"Missing calculation directory: {stage_dir}")

    candidates = list(stage_dir.glob("ElectrostaticPotential.grid.nc"))
    if not candidates:
        candidates = sorted(stage_dir.glob("*.grid.nc"))
    if not candidates:
        raise FileNotFoundError(
            f"No electrostatic-potential *.grid.nc file found in {stage_dir}"
        )
    eig_path = stage_dir / "slab.EIG"
    if not eig_path.is_file():
        raise FileNotFoundError(f"Missing eigenvalue file: {eig_path}")

    grid = sisl.get_sile(str(candidates[0])).read_grid()
    potential = np.asarray(grid.grid)
    if potential.ndim != 3:
        raise RuntimeError(f"Expected a 3-D grid, found shape {potential.shape}")
    planar = potential.mean(axis=(0, 1))
    cell_z = float(grid.cell[2, 2])
    z = np.linspace(0.0, cell_z, planar.size, endpoint=False)
    vacuum = float(np.max(planar))
    fermi, vbm, cbm, eigenvalue_count = parse_eigenvalues(eig_path)
    ionization = vacuum - vbm
    affinity = vacuum - cbm

    DATA.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    with (DATA / f"{prefix}_potential.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["z_A", "planar_electrostatic_potential_eV"])
        writer.writerows(zip(z, planar))

    figure, axis = plt.subplots(figsize=(8, 5))
    axis.plot(z, planar, linewidth=2)
    axis.axhline(vacuum, linestyle="--", label=f"Vacuum = {vacuum:.2f} eV")
    axis.axhline(vbm, linestyle="--", label=f"VBM = {vbm:.2f} eV")
    axis.set(
        xlabel="z (Å)",
        ylabel="Electrostatic potential (eV)",
        title=prefix.replace("_", " ").title(),
    )
    axis.legend()
    figure.tight_layout()
    figure.savefig(FIGURES / f"{prefix}_potential.png", dpi=200)
    plt.close(figure)

    payload = {
        "stage": stage,
        "postprocessed_utc": datetime.now(timezone.utc).isoformat(),
        "source_grid": str(candidates[0].relative_to(ROOT)),
        "source_eigenvalues": str(eig_path.relative_to(ROOT)),
        "result": {
            "vacuum_eV": vacuum,
            "fermi_eV": fermi,
            "vbm_eV": vbm,
            "cbm_eV": cbm,
            "ionization_potential_eV": ionization,
            "electron_affinity_eV": affinity,
            "grid_shape": list(potential.shape),
            "eigenvalue_count": eigenvalue_count,
        },
    }
    output = DATA / f"{stage}.json"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (stage_dir / "stage_complete.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

