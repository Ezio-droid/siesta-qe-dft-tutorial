#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p results/{data,figures,structures,logs}

find results/raw -name 'stage_complete.json' -type f -print0 \
    | while IFS= read -r -d '' marker; do
        stage="$(basename "$(dirname "$marker")")"
        cp "$marker" "results/data/${stage}.json"
      done

if find pseudopotentials -maxdepth 1 -type f \
    ! -name README.md ! -name checksums.sha256 | grep -q .; then
    find pseudopotentials -maxdepth 1 -type f \
        ! -name README.md ! -name checksums.sha256 -print0 \
        | sort -z | xargs -0 sha256sum > pseudopotentials/checksums.sha256
fi

echo "Compact results collected under results/data, figures, and structures."

