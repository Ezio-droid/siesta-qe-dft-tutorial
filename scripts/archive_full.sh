#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

stamp="$(date -u +%Y%m%dT%H%M%SZ)"
destination="archive/siesta-tutorial-full-${stamp}.tar.gz"

tar -czf "$destination" \
    README.md config environment notebooks pseudopotentials \
    scripts slurm results

sha256sum "$destination" > "${destination}.sha256"
echo "Created $destination"
echo "Created ${destination}.sha256"

