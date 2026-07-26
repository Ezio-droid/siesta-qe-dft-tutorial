# One-hour tutorial route

The complete shortened notebook does not fit in the session. The measured
SIESTA runtime was 133.67 minutes, and QE did not finish within three hours.
Use this route instead of executing every code cell.

## Suggested schedule

| Time | Activity | Mode |
|---:|---|---|
| 0–8 min | ASE structures, calculators, pseudopotentials | Instructor-led |
| 8–18 min | SIESTA single point | Run live |
| 18–27 min | SIESTA convergence and optimization concepts | Supplied data |
| 27–35 min | Surface DOS and ionization potential | Supplied results |
| 35–45 min | QE single point | Run live |
| 45–53 min | Compare SIESTA and QE inputs | Supplied inputs |
| 53–60 min | NEB concept, conclusions, questions | Supplied plot/discussion |

## SIESTA live calculation

On Narval, use the tested smoke-test stage:

```bash
bash slurm/submit_stage.sh 00_single_point
squeue -u "$USER"
```

Expected benchmark runtime was approximately 1.4 minutes on ten MPI ranks.
The result is also available at:

```text
reference-results/siesta/data/00_single_point.json
reference-results/siesta/selected-outputs/00_single_point/c2.out
```

## Supplied SIESTA analysis

Use these without rerunning DFT:

```text
reference-results/siesta/data/bulk_kpoint_convergence.csv
reference-results/siesta/data/bulk_mesh_convergence.csv
reference-results/siesta/data/bulk_dos.csv
reference-results/siesta/data/pristine_slab_dos.csv
reference-results/siesta/data/h_terminated_slab_dos.csv
reference-results/siesta/data/pristine_slab_potential.csv
reference-results/siesta/data/h_terminated_slab_potential.csv
```

Corresponding plots are in `reference-results/siesta/figures/`.

## QE live calculation

The generated input is:

```text
inputs/qe/c2_qe/espresso.pwi
```

After placing the QE pseudopotential under `pseudopotentials/qe/`, submit a
small allocation and run:

```bash
module --force purge
module load StdEnv/2023 gcc/12.3 openmpi/4.1.5 quantumespresso/7.5
srun pw.x -in inputs/qe/c2_qe/espresso.pwi > qe-single-point.out
```

The supplied input uses the repository-relative `pseudopotentials/qe`
directory. Run the command from the repository root.

## Cells not intended for live execution

In `notebooks/tutorial-short.ipynb`, do not execute complete convergence loops,
geometry optimizations, work-function production runs, or either NEB section.
They remain in the notebook for later study.

The additional notebook under `notebooks/extended-ghost-neb/` is strictly a
post-tutorial exercise. Do not run it during the one-hour session.
