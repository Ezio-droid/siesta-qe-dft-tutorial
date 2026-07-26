#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/results/logs"

echo "Date: $(date --iso-8601=seconds)"
echo "Host: $(hostname)"
echo "User: $USER"
echo "Working directory: $ROOT"
echo
echo "Cluster release:"
cat /etc/os-release 2>/dev/null || true
echo
echo "Candidate SIESTA modules:"
module spider siesta 2>&1 || true
echo
echo "Python modules:"
module spider python 2>&1 | head -n 80 || true
echo
echo "Visible executables before loading a module:"
for exe in siesta siesta.psml siesta-mpi; do
    command -v "$exe" 2>/dev/null || true
done
echo
echo "Pseudopotential files currently present:"
find "$ROOT/pseudopotentials" -maxdepth 1 -type f -printf '%f\n' \
    | sort || true

