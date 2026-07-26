#!/usr/bin/env python3
"""Restart-safe ASE/SIESTA calculation stages for the conference tutorial."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from ase import Atom
from ase.build import bulk, graphene, surface
from ase.calculators.siesta import Siesta
from ase.dft.dos import DOS
from ase.filters import UnitCellFilter
from ase.io import read, write
from ase.mep import NEB
from ase.optimize import BFGS
from ase.units import Ry

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw"
DATA = ROOT / "results" / "data"
FIGURES = ROOT / "results" / "figures"
STRUCTURES = ROOT / "results" / "structures"
for directory in (RAW, DATA, FIGURES, STRUCTURES):
    directory.mkdir(parents=True, exist_ok=True)

PSEUDO_DIR = Path(os.environ.get("SIESTA_PSEUDO_DIR", "pseudopotentials"))
if not PSEUDO_DIR.is_absolute():
    PSEUDO_DIR = ROOT / PSEUDO_DIR
PSEUDO_QUALIFIER = os.environ.get("SIESTA_PSEUDO_QUALIFIER", "gga")


@contextmanager
def in_directory(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def calculator(
    label: str,
    *,
    mesh_ry: int = 230,
    kpts: tuple[int, int, int] = (5, 5, 5),
    spin: str = "non-polarized",
    extra_fdf: dict | None = None,
) -> Siesta:
    fdf = {"DM.MixingWeight": 0.1, "MaxSCFIterations": 100}
    if extra_fdf:
        fdf.update(extra_fdf)
    return Siesta(
        label=label,
        xc="PBE",
        pseudo_path=str(PSEUDO_DIR),
        pseudo_qualifier=PSEUDO_QUALIFIER,
        symlink_pseudos=True,
        mesh_cutoff=mesh_ry * Ry,
        energy_shift=0.01 * Ry,
        basis_set="DZP",
        spin=spin,
        kpts=kpts,
        fdf_arguments=fdf,
    )


def require(path: Path, producer: str):
    if not path.exists():
        raise FileNotFoundError(
            f"Required file is missing: {path}\nRun stage {producer} successfully first."
        )
    return path


def save_csv(name: str, header: list[str], rows: list[list[object]]) -> None:
    with (DATA / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def save_plot(
    x,
    y,
    filename: str,
    xlabel: str,
    ylabel: str,
    title: str,
    *,
    xlim=None,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, y, "-o", markersize=4)
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    if xlim:
        ax.set_xlim(*xlim)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIGURES / filename, dpi=200)
    plt.close(fig)


def save_structure(atoms, stem: str) -> None:
    write(STRUCTURES / f"{stem}.traj", atoms)
    write(STRUCTURES / f"{stem}.xyz", atoms)


def diamond():
    return bulk("C", "diamond", a=3.567, cubic=True)


def h_terminated_slab():
    atoms = read(require(STRUCTURES / "bulk_optimized.traj", "03_bulk_opt"))
    atoms.pbc = True
    slab = surface(atoms, (1, 0, 0), 4, vacuum=15.0)
    slab.center(vacuum=15.0, axis=2)
    carbon_z = [a.position[2] for a in slab if a.symbol == "C"]
    zmax, zmin = max(carbon_z), min(carbon_z)
    tolerance, ch = 0.5, 0.8
    top = [
        i
        for i, atom in enumerate(slab)
        if atom.symbol == "C" and zmax - atom.position[2] < tolerance
    ]
    bottom = [
        i
        for i, atom in enumerate(slab)
        if atom.symbol == "C" and atom.position[2] - zmin < tolerance
    ]
    top_offsets = [(-0.5, -0.5, ch), (0.5, 0.5, ch),
                   (-0.5, 0.5, ch), (0.5, -0.5, ch)]
    bottom_offsets = [(-0.5, -0.5, -ch), (0.5, 0.5, -ch),
                      (-0.5, 0.5, -ch), (0.5, -0.5, -ch)]
    for index, offset in zip((top[0], top[0], top[1], top[1]), top_offsets):
        slab.append(Atom("H", slab[index].position + np.array(offset)))
    for index, offset in zip(
        (bottom[0], bottom[0], bottom[1], bottom[1]), bottom_offsets
    ):
        slab.append(Atom("H", slab[index].position + np.array(offset)))
    return slab


def stage_00_single_point(stage_dir: Path):
    atoms = diamond()
    with in_directory(stage_dir):
        atoms.calc = calculator("c2", mesh_ry=200, kpts=(4, 4, 4))
        energy = atoms.get_potential_energy()
    save_structure(atoms, "diamond_single_point")
    return {"energy_eV": energy}


def stage_01_bulk_kpoints(stage_dir: Path):
    rows = []
    for kk in range(1, 9):
        run_dir = stage_dir / f"k_{kk:02d}"
        atoms = diamond()
        with in_directory(run_dir):
            atoms.calc = calculator("c2", mesh_ry=200, kpts=(kk, kk, kk))
            energy = atoms.get_potential_energy()
        rows.append([kk, energy])
    save_csv("bulk_kpoint_convergence.csv", ["k", "energy_eV"], rows)
    save_plot(
        [r[0] for r in rows], [r[1] for r in rows],
        "bulk_kpoint_convergence.png", "k-point grid (k×k×k)",
        "Total energy (eV)", "Diamond k-point convergence",
    )
    return {"points": len(rows), "last_energy_eV": rows[-1][1]}


def stage_02_bulk_cutoff(stage_dir: Path):
    rows = []
    for cutoff in range(150, 260, 10):
        run_dir = stage_dir / f"mesh_{cutoff:03d}Ry"
        atoms = diamond()
        with in_directory(run_dir):
            atoms.calc = calculator("c2", mesh_ry=cutoff, kpts=(5, 5, 5))
            energy = atoms.get_potential_energy()
        rows.append([cutoff, energy])
    save_csv("bulk_mesh_convergence.csv", ["mesh_cutoff_Ry", "energy_eV"], rows)
    save_plot(
        [r[0] for r in rows], [r[1] for r in rows],
        "bulk_mesh_convergence.png", "Mesh cutoff (Ry)", "Total energy (eV)",
        "Diamond real-space mesh convergence",
    )
    return {"points": len(rows), "last_energy_eV": rows[-1][1]}


def stage_03_bulk_opt(stage_dir: Path):
    atoms = diamond()
    initial_cell = atoms.cell.array.tolist()
    with in_directory(stage_dir):
        atoms.calc = calculator("c2")
        initial_energy = atoms.get_potential_energy()
        opt = BFGS(UnitCellFilter(atoms), trajectory="cellopt.traj", logfile="bfgs.log")
        converged = opt.run(fmax=0.01)
        final_energy = atoms.get_potential_energy()
    save_structure(atoms, "bulk_optimized")
    return {
        "converged": bool(converged),
        "initial_energy_eV": initial_energy,
        "final_energy_eV": final_energy,
        "initial_cell_A": initial_cell,
        "final_cell_A": atoms.cell.array.tolist(),
    }


def calculate_dos(atoms, stage_dir: Path, prefix: str, kpts):
    with in_directory(stage_dir):
        atoms.calc = calculator(
            "c2",
            kpts=kpts,
            extra_fdf={"WriteEigenvalues": True, "SaveHS": True},
        )
        energy = atoms.get_potential_energy()
        dos = DOS(atoms.calc, width=0.05, npts=3000)
        energies = dos.get_energies()
        density = dos.get_dos()
    mask = (energies >= -10) & (energies <= 10)
    rows = [[float(e), float(d)] for e, d in zip(energies[mask], density[mask])]
    save_csv(f"{prefix}_dos.csv", ["energy_minus_fermi_eV", "dos_states_per_eV"], rows)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(energies[mask], density[mask])
    ax.axvline(0, color="k", linestyle="--")
    ax.set(
        xlim=(-10, 10),
        xlabel=r"$E-E_F$ (eV)",
        ylabel="DOS (states/eV)",
        title=prefix.replace("_", " ").title(),
    )
    fig.tight_layout()
    fig.savefig(FIGURES / f"{prefix}_dos.png", dpi=200)
    plt.close(fig)
    return {"energy_eV": energy, "dos_points": len(rows)}


def stage_04_bulk_dos(stage_dir: Path):
    atoms = read(require(STRUCTURES / "bulk_optimized.traj", "03_bulk_opt"))
    atoms.pbc = True
    return calculate_dos(atoms, stage_dir, "bulk", (5, 5, 5))


def stage_05_slab_opt(stage_dir: Path):
    atoms = read(require(STRUCTURES / "bulk_optimized.traj", "03_bulk_opt"))
    atoms.pbc = True
    slab = surface(atoms, (1, 0, 0), 4, vacuum=15.0)
    slab.center(vacuum=15.0, axis=2)
    with in_directory(stage_dir):
        slab.calc = calculator("c2", kpts=(5, 5, 1))
        initial_energy = slab.get_potential_energy()
        opt = BFGS(slab, trajectory="cellopt.traj", logfile="bfgs.log")
        converged = opt.run(fmax=0.01)
        final_energy = slab.get_potential_energy()
    save_structure(slab, "pristine_slab_optimized")
    return {
        "converged": bool(converged),
        "initial_energy_eV": initial_energy,
        "final_energy_eV": final_energy,
    }


def stage_06_slab_dos(stage_dir: Path):
    atoms = read(require(STRUCTURES / "pristine_slab_optimized.traj", "05_slab_opt"))
    atoms.pbc = True
    return calculate_dos(atoms, stage_dir, "pristine_slab", (5, 5, 1))


def stage_07_h_slab_low_opt(stage_dir: Path):
    slab = h_terminated_slab()
    save_structure(slab, "h_slab_initial")
    with in_directory(stage_dir):
        slab.calc = calculator("c2", mesh_ry=170, kpts=(3, 3, 1))
        initial_energy = slab.get_potential_energy()
        opt = BFGS(slab, trajectory="cellopt.traj", logfile="bfgs.log")
        converged = opt.run(fmax=0.01)
        final_energy = slab.get_potential_energy()
    save_structure(slab, "h_slab_low_optimized")
    return {
        "converged": bool(converged),
        "initial_energy_eV": initial_energy,
        "final_energy_eV": final_energy,
    }


def stage_08_h_slab_high_opt(stage_dir: Path):
    slab = read(require(STRUCTURES / "h_slab_low_optimized.traj", "07_h_slab_low_opt"))
    slab.pbc = True
    with in_directory(stage_dir):
        slab.calc = calculator("c2", mesh_ry=230, kpts=(5, 5, 1))
        initial_energy = slab.get_potential_energy()
        opt = BFGS(slab, trajectory="cellopt.traj", logfile="bfgs.log")
        converged = opt.run(fmax=0.01)
        final_energy = slab.get_potential_energy()
    save_structure(slab, "h_slab_high_optimized")
    return {
        "converged": bool(converged),
        "initial_energy_eV": initial_energy,
        "final_energy_eV": final_energy,
    }


def stage_09_h_slab_dos(stage_dir: Path):
    atoms = read(require(STRUCTURES / "h_slab_high_optimized.traj", "08_h_slab_high_opt"))
    atoms.pbc = True
    return calculate_dos(atoms, stage_dir, "h_terminated_slab", (5, 5, 1))


def parse_eigenvalues(path: Path):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    fermi = float(lines[0].split()[0])
    eigs = []
    for line in lines[2:]:
        parts = line.split()
        if parts and re.fullmatch(r"[+-]?\d+", parts[0]):
            parts = parts[1:]
        for value in parts:
            try:
                eigs.append(float(value))
            except ValueError:
                pass
    eigs = np.asarray(eigs)
    occupied = eigs[eigs < fermi]
    unoccupied = eigs[eigs > fermi]
    if not len(occupied) or not len(unoccupied):
        raise RuntimeError(f"Could not identify occupied/unoccupied states in {path}")
    return fermi, occupied.max(), unoccupied.min()


def work_function(atoms, stage_dir: Path, prefix: str):
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
        energy = atoms.get_potential_energy()
        import sisl

        candidates = list(stage_dir.glob("ElectrostaticPotential.grid.nc"))
        if not candidates:
            candidates = list(stage_dir.glob("*.grid.nc"))
        if not candidates:
            raise FileNotFoundError(
                "No SIESTA NetCDF electrostatic-potential grid was produced. "
                "Check the SIESTA build and fdf output in this stage directory."
            )
        grid = sisl.get_sile(str(candidates[0])).read_grid()
        potential = np.asarray(grid.grid)
        planar = potential.mean(axis=(0, 1))
        cell_z = float(grid.cell[2, 2])
        z = np.linspace(0, cell_z, len(planar))
        vacuum = float(np.max(planar))
        fermi, vbm, cbm = parse_eigenvalues(stage_dir / "slab.EIG")
    ionization = vacuum - vbm
    affinity = vacuum - cbm
    save_csv(
        f"{prefix}_potential.csv",
        ["z_A", "planar_electrostatic_potential_eV"],
        [[float(a), float(b)] for a, b in zip(z, planar)],
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(z, planar, lw=2)
    ax.axhline(vacuum, ls="--", label=f"Vacuum = {vacuum:.2f} eV")
    ax.axhline(vbm, ls="--", label=f"VBM = {vbm:.2f} eV")
    ax.set(
        xlabel="z (Å)",
        ylabel="Electrostatic potential (eV)",
        title=prefix.replace("_", " ").title(),
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / f"{prefix}_potential.png", dpi=200)
    plt.close(fig)
    return {
        "energy_eV": energy,
        "vacuum_eV": vacuum,
        "fermi_eV": fermi,
        "vbm_eV": vbm,
        "cbm_eV": cbm,
        "ionization_potential_eV": ionization,
        "electron_affinity_eV": affinity,
    }


def stage_10_h_slab_work_function(stage_dir: Path):
    atoms = read(require(STRUCTURES / "h_slab_high_optimized.traj", "08_h_slab_high_opt"))
    atoms.pbc = True
    return work_function(atoms, stage_dir, "h_terminated_slab")


def stage_11_pristine_slab_work_function(stage_dir: Path):
    atoms = read(require(STRUCTURES / "pristine_slab_optimized.traj", "05_slab_opt"))
    atoms.pbc = True
    return work_function(atoms, stage_dir, "pristine_slab")


def stage_12_graphene_kpoints(stage_dir: Path):
    rows = []
    for kk in range(1, 15):
        atoms = graphene(a=2.46, vacuum=10.0)
        atoms.center(axis=2)
        with in_directory(stage_dir / f"k_{kk:02d}"):
            atoms.calc = calculator("c2", mesh_ry=200, kpts=(kk, kk, 1))
            energy = atoms.get_potential_energy()
        rows.append([kk, energy])
    save_csv("graphene_kpoint_convergence.csv", ["k", "energy_eV"], rows)
    save_plot(
        [r[0] for r in rows], [r[1] for r in rows],
        "graphene_kpoint_convergence.png", "k-point grid (k×k×1)",
        "Total energy (eV)", "Graphene k-point convergence",
    )
    return {"points": len(rows), "last_energy_eV": rows[-1][1]}


def stage_13_ni_initial_opt(stage_dir: Path):
    atoms = graphene(a=2.46, vacuum=10.0)
    atoms.center(axis=2)
    atoms = atoms.repeat((4, 4, 1))
    atoms.append(Atom("Ni", (2.5, 1.0, 12.5)))
    # The empty DM.InitSpin block produced by the original notebook initializes
    # every atom as non-magnetic and caused the Ni/graphene SCF to stall. Give
    # only Ni a physically reasonable starting moment.
    initial_magmoms = np.zeros(len(atoms))
    initial_magmoms[-1] = 2.0
    atoms.set_initial_magnetic_moments(initial_magmoms)
    with in_directory(stage_dir):
        atoms.calc = calculator(
            "c2",
            kpts=(3, 3, 1),
            spin="collinear",
            extra_fdf={
                "DM.MixingWeight": 0.05,
                "DM.Tolerance": 1.0e-3,
                "SCF.H.Converge": False,
                "DM.NumberPulay": 6,
                "MaxSCFIterations": 400,
                "ElectronicTemperature": "50 meV",
            },
        )
        initial_energy = atoms.get_potential_energy()
        opt = BFGS(atoms, trajectory="atoms.traj", logfile="bfgs.log")
        converged = opt.run(fmax=0.02)
        final_energy = atoms.get_potential_energy()
    save_structure(atoms, "ni_graphene_initial_optimized")
    return {
        "converged": bool(converged),
        "initial_energy_eV": initial_energy,
        "final_energy_eV": final_energy,
    }


def stage_14_ni_final_opt(stage_dir: Path):
    atoms = read(
        require(STRUCTURES / "ni_graphene_initial_optimized.traj", "13_ni_initial_opt")
    )
    ni_index = next(i for i, atom in enumerate(atoms) if atom.symbol == "Ni")
    atoms[ni_index].position += [1.5, 2.0, 0.0]
    initial_magmoms = np.zeros(len(atoms))
    initial_magmoms[ni_index] = 2.0
    atoms.set_initial_magnetic_moments(initial_magmoms)
    with in_directory(stage_dir):
        atoms.calc = calculator(
            "c2",
            kpts=(3, 3, 1),
            spin="collinear",
            extra_fdf={
                "DM.MixingWeight": 0.05,
                "DM.Tolerance": 1.0e-3,
                "SCF.H.Converge": False,
                "DM.NumberPulay": 6,
                "MaxSCFIterations": 400,
                "ElectronicTemperature": "50 meV",
            },
        )
        initial_energy = atoms.get_potential_energy()
        opt = BFGS(atoms, trajectory="atoms.traj", logfile="bfgs.log")
        converged = opt.run(fmax=0.02)
        final_energy = atoms.get_potential_energy()
    save_structure(atoms, "ni_graphene_final_optimized")
    return {
        "converged": bool(converged),
        "initial_energy_eV": initial_energy,
        "final_energy_eV": final_energy,
    }


def stage_15_ni_neb(stage_dir: Path):
    initial = read(
        require(STRUCTURES / "ni_graphene_initial_optimized.traj", "13_ni_initial_opt")
    )
    final = read(
        require(STRUCTURES / "ni_graphene_final_optimized.traj", "14_ni_final_opt")
    )
    images = [initial] + [initial.copy() for _ in range(3)] + [final]
    neb = NEB(images)
    neb.interpolate()
    for index, image in enumerate(images):
        ni_index = next(i for i, atom in enumerate(image) if atom.symbol == "Ni")
        initial_magmoms = np.zeros(len(image))
        initial_magmoms[ni_index] = 2.0
        image.set_initial_magnetic_moments(initial_magmoms)
        image_dir = stage_dir / f"image_{index:02d}"
        image_dir.mkdir(parents=True, exist_ok=True)
        image.calc = calculator(
            str(image_dir / "c2"),
            kpts=(3, 3, 1),
            spin="collinear",
            extra_fdf={
                "DM.MixingWeight": 0.05,
                "DM.Tolerance": 1.0e-3,
                "SCF.H.Converge": False,
                "DM.NumberPulay": 6,
                "MaxSCFIterations": 400,
                "ElectronicTemperature": "50 meV",
            },
        )
    with in_directory(stage_dir):
        opt = BFGS(neb, logfile="neb.log", trajectory="neb.traj")
        converged = opt.run(fmax=0.05)
        energies = [float(image.get_potential_energy()) for image in images]
    relative = [energy - energies[0] for energy in energies]
    ts_index = int(np.argmax(energies))
    save_structure(images[ts_index], "ni_graphene_transition_state")
    save_csv(
        "ni_graphene_neb.csv",
        ["image", "absolute_energy_eV", "relative_energy_eV"],
        [[i, e, r] for i, (e, r) in enumerate(zip(energies, relative))],
    )
    save_plot(
        list(range(len(images))), relative, "ni_graphene_neb.png",
        "Image index", "Relative energy (eV)", "Ni diffusion on graphene",
    )
    return {
        "converged": bool(converged),
        "energies_eV": energies,
        "relative_energies_eV": relative,
        "transition_state_image": ts_index,
        "barrier_eV": max(relative),
    }


STAGES = {
    name.removeprefix("stage_"): function
    for name, function in list(globals().items())
    if name.startswith("stage_") and callable(function)
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=sorted(STAGES))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    stage_dir = RAW / args.stage
    marker = stage_dir / "stage_complete.json"
    if marker.exists() and not args.force:
        raise SystemExit(
            f"{args.stage} is already marked complete. Use --force only for an "
            "intentional rerun."
        )
    stage_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    print(f"Starting {args.stage} at {started.isoformat()}", flush=True)
    result = STAGES[args.stage](stage_dir)
    finished = datetime.now(timezone.utc)
    payload = {
        "stage": args.stage,
        "started_utc": started.isoformat(),
        "finished_utc": finished.isoformat(),
        "duration_seconds": (finished - started).total_seconds(),
        "result": result,
    }
    marker.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (DATA / f"{args.stage}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2), flush=True)


if __name__ == "__main__":
    main()
