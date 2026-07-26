#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=10
#SBATCH --cpus-per-task=1
#SBATCH --mem=0
#SBATCH --time=3:00:00
#SBATCH --job-name=nb-siesta-neb
#SBATCH --output=benchmark/logs/03_siesta_neb-%j.out
#SBATCH --error=benchmark/logs/03_siesta_neb-%j.err

set -euo pipefail
ROOT="${SLURM_SUBMIT_DIR:?Submit this job from the repository root}"
cd "$ROOT"

module --force purge
module load StdEnv/2023 intel/2023.2.1 openmpi/4.1.5 siesta/5.4.0 python/3.12.4
source .venv/bin/activate
export OMP_NUM_THREADS=1
export MPLBACKEND=Agg
export ASE_SIESTA_COMMAND='srun --exclusive --ntasks=10 --cpus-per-task=1 siesta < PREFIX.fdf > PREFIX.out'
export SIESTA_PSEUDO_DIR="$ROOT/pseudopotentials/siesta"
export BENCHMARK_RUN_DIR="$ROOT/benchmark/run"

python scripts/execute_notebook.py \
  notebooks/narval-segments/03_siesta_neb.ipynb \
  benchmark/executed/03_siesta_neb_executed.ipynb \
  benchmark/timings/03_siesta_neb.json
