#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --job-name=nb-siesta-post
#SBATCH --output=benchmark/logs/02_siesta_post-%j.out
#SBATCH --error=benchmark/logs/02_siesta_post-%j.err

set -euo pipefail
ROOT="${SLURM_SUBMIT_DIR:?Submit this job from the repository root}"
cd "$ROOT"

module --force purge
module load StdEnv/2023 gcc/12.3 openmpi/4.1.5 python/3.12.4 mpi4py/4.1.0
source .venv/bin/activate
export MPLBACKEND=Agg
export BENCHMARK_RUN_DIR="$ROOT/benchmark/run"

python scripts/execute_notebook.py \
  notebooks/narval-segments/02_siesta_postprocess.ipynb \
  benchmark/executed/02_siesta_postprocess_executed.ipynb \
  benchmark/timings/02_siesta_postprocess.json
