# Running on Narval

## 1. Clone into project or scratch storage

```bash
cd "$SCRATCH"
git clone https://github.com/Ezio-droid/siesta-qe-dft-tutorial.git
cd siesta-qe-dft-tutorial
```

Do not run large calculations from `$HOME`.

## 2. Add pseudopotentials

Follow `pseudopotentials/README.md`. Expected local directories are:

```text
pseudopotentials/siesta/
pseudopotentials/qe/
```

The SIESTA staged driver currently reads the directory configured in
`config/narval.env`. Update:

```bash
SIESTA_PSEUDO_DIR="pseudopotentials/siesta"
```

## 3. Set the Slurm account

Edit `config/narval.env`:

```bash
SLURM_ACCOUNT="your-allocation"
```

The tested module stack is already recorded there.

## 4. Create the Python environment

```bash
bash slurm/01_setup_environment.sh
```

The Alliance Python wheelhouse may require a separate GCC/mpi4py module stack
for `sisl` and `netCDF4` postprocessing. The tested postprocessing modules were:

```bash
module --force purge
module load StdEnv/2023 gcc/12.3 openmpi/4.1.5 \
  python/3.12.4 mpi4py/4.1.0
source .venv/bin/activate
```

## 5. Preflight

```bash
bash slurm/00_diagnose.sh
bash slurm/02_preflight.sh
```

Resolve every missing executable, module, or pseudopotential before submitting
the chain.

## 6. Smoke test

```bash
bash slurm/submit_stage.sh 00_single_point
```

Inspect the Slurm `.out` and `.err` files under `results/logs/` before
continuing.

## 7. Optional staged calculations

```bash
bash slurm/submit_chain.sh bulk
bash slurm/submit_chain.sh surfaces
```

The `nickel_neb` chain includes expensive calculations. For a tutorial, use the
supplied Ni endpoint structures and treat NEB as an advanced exercise.

## Optional: reproduce the complete shortened-notebook benchmark

This is for after the conference, not the one-hour session. It submits four
dependent jobs and can require more than five hours:

```bash
bash slurm/benchmark/setup_and_submit.sh
```

The script refuses to start if `benchmark/run/` is not empty, preventing the
`FileExistsError` caused by rerunning notebook cells in an old work directory.

## Output locations

```text
results/raw/          Complete calculation directories
results/data/         CSV and JSON summaries
results/figures/      Plots
results/structures/   Optimized structures
results/logs/         Slurm and environment logs
```

The GitHub copy provides equivalent compact files under `reference-results/`.
