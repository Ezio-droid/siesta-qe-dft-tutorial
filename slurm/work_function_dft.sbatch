#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --mem=0
#SBATCH --time=05:00:00
#SBATCH --job-name=siesta-wf-dft
#SBATCH --mail-type=FAIL

set -euo pipefail

ROOT="${SLURM_SUBMIT_DIR:?Submit from the repository root}"
cd "$ROOT"
source config/narval.env

module --force purge
read -r -a modules <<< "$SIESTA_MODULES"
module load "${modules[@]}"
source .venv/bin/activate

export MPLBACKEND=Agg
export OMP_NUM_THREADS=1
export SIESTA_PSEUDO_DIR
export SIESTA_PSEUDO_QUALIFIER
export SIESTA_EXE
export ASE_SIESTA_COMMAND
ASE_SIESTA_COMMAND="$(eval "echo \"$ASE_SIESTA_COMMAND_TEMPLATE\"")"

python scripts/run_work_function_dft.py "$WF_CASE"
