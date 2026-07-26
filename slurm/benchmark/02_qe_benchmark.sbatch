#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=10
#SBATCH --cpus-per-task=1
#SBATCH --mem=0
#SBATCH --time=3:00:00
#SBATCH --job-name=nb-qe
#SBATCH --output=benchmark/logs/02_qe-%j.out
#SBATCH --error=benchmark/logs/02_qe-%j.err

set -euo pipefail

ROOT="${SLURM_SUBMIT_DIR:?Submit this job from the repository root}"
cd "$ROOT"

module --force purge
module load StdEnv/2023 gcc/12.3 openmpi/4.1.5 quantumespresso/7.5 python/3.12.4
source .venv/bin/activate

export OMP_NUM_THREADS=1
export MPLBACKEND=Agg
export QE_PSEUDO_DIR="$ROOT/pseudopotentials/qe"
export BENCHMARK_RUN_DIR="$ROOT/benchmark/run"

mkdir -p benchmark/logs benchmark/timings benchmark/executed benchmark/run
python scripts/execute_notebook.py \
  notebooks/narval-segments/04_qe.ipynb \
  benchmark/executed/04_qe_executed.ipynb \
  benchmark/timings/04_qe.json
