#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

module purge
module load StdEnv/2023
module load python/3.12.4

python -m venv --clear .venv
source .venv/bin/activate
python -m pip install --no-index --upgrade pip
python -m pip install --no-index -r environment/requirements.txt
python -m pip freeze > environment/requirements-lock-narval.txt

echo "Environment created at $ROOT/.venv"
echo "Resolved packages recorded in environment/requirements-lock-narval.txt"

