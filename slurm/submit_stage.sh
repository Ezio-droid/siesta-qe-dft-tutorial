#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Usage: bash slurm/submit_stage.sh STAGE [DEPENDENCY_JOB_ID]" >&2
    exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
source config/narval.env

stage="$1"
dependency="${2:-}"
mkdir -p results/logs

args=(
    --account="$SLURM_ACCOUNT"
    --job-name="st-${stage}"
    --output="results/logs/${stage}-%j.out"
    --error="results/logs/${stage}-%j.err"
    --export="ALL,STAGE=${stage}"
)
if [[ -n "$dependency" ]]; then
    args+=(--dependency="afterok:${dependency}")
fi

sbatch --parsable "${args[@]}" slurm/siesta_stage.sbatch

