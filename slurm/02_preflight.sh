#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
source config/narval.env

module purge
read -r -a modules <<< "$SIESTA_MODULES"
module load "${modules[@]}"
source .venv/bin/activate

export SIESTA_PSEUDO_DIR
export SIESTA_PSEUDO_QUALIFIER
export SIESTA_EXE

python scripts/preflight.py

