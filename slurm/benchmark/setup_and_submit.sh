#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
source config/narval.env

if [[ "$SLURM_ACCOUNT" == "YOUR_ALLOCATION" ]]; then
    echo "Set SLURM_ACCOUNT in config/narval.env first." >&2
    exit 1
fi

for file in \
  pseudopotentials/qe/C.pbe-n-kjpaw_psl.1.0.0.UPF \
  pseudopotentials/qe/H.pbe-rrkjus_psl.1.0.0.UPF \
  pseudopotentials/qe/ni_pbe_v1.4.uspp.F.UPF \
  pseudopotentials/siesta/C.psml \
  pseudopotentials/siesta/H.psml \
  pseudopotentials/siesta/Ni.psml
do
    [[ -s "$file" ]] || { echo "Missing $file" >&2; exit 1; }
done

[[ -f .venv/bin/activate ]] || {
    echo "Missing .venv; follow docs/NARVAL.md before submitting." >&2
    exit 1
}

module --force purge
module load StdEnv/2023 python/3.12.4
source .venv/bin/activate
python -c "import ase, numpy, matplotlib, nbformat, nbclient"
deactivate

module --force purge
module load StdEnv/2023 gcc/12.3 openmpi/4.1.5 python/3.12.4 mpi4py/4.1.0
source .venv/bin/activate
python -c "import mpi4py, netCDF4, sisl"
deactivate

mkdir -p benchmark/logs benchmark/timings benchmark/executed benchmark/run
if find benchmark/run -mindepth 1 -print -quit | grep -q .; then
    echo "benchmark/run is not empty; move it aside before a fresh benchmark." >&2
    exit 1
fi

python scripts/prepare_benchmark.py

j1=$(sbatch --parsable --account="$SLURM_ACCOUNT" slurm/benchmark/01_siesta_benchmark.sbatch)
j2=$(sbatch --parsable --account="$SLURM_ACCOUNT" --dependency="afterok:$j1" slurm/benchmark/02_siesta_postprocess.sbatch)
j3=$(sbatch --parsable --account="$SLURM_ACCOUNT" --dependency="afterok:$j2" slurm/benchmark/03_siesta_neb.sbatch)
# Continue to QE even if the optional NEB segment fails.
j4=$(sbatch --parsable --account="$SLURM_ACCOUNT" --dependency="afterany:$j3" slurm/benchmark/02_qe_benchmark.sbatch)

{
    echo "SIESTA_DFT_JOB=$j1"
    echo "SIESTA_POST_JOB=$j2"
    echo "SIESTA_NEB_JOB=$j3"
    echo "QE_JOB=$j4"
} | tee benchmark/benchmark-jobs.txt
