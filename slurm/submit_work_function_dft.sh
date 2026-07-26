#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || ! "$1" =~ ^(h_slab|pristine_slab)$ ]]; then
    echo "Usage: bash slurm/submit_work_function_dft.sh {h_slab|pristine_slab}" >&2
    exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
source config/narval.env
case_name="$1"
mkdir -p results/logs

sbatch --parsable \
    --account="$SLURM_ACCOUNT" \
    --job-name="wf-${case_name}" \
    --output="results/logs/wf-${case_name}-%j.out" \
    --error="results/logs/wf-${case_name}-%j.err" \
    --export="ALL,WF_CASE=${case_name}" \
    slurm/work_function_dft.sbatch

