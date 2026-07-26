#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: bash slurm/submit_chain.sh {bulk|surfaces|nickel_neb}" >&2
    exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

case "$1" in
    bulk)
        stages=(01_bulk_kpoints 02_bulk_cutoff 03_bulk_opt 04_bulk_dos)
        ;;
    surfaces)
        stages=(05_slab_opt 06_slab_dos 07_h_slab_low_opt 08_h_slab_high_opt
                09_h_slab_dos 10_h_slab_work_function
                11_pristine_slab_work_function)
        ;;
    nickel_neb)
        stages=(12_graphene_kpoints 13_ni_initial_opt 14_ni_final_opt 15_ni_neb)
        ;;
    *)
        echo "Unknown chain: $1" >&2
        exit 2
        ;;
esac

dependency=""
for stage in "${stages[@]}"; do
    if [[ -n "$dependency" ]]; then
        job_id="$(bash slurm/submit_stage.sh "$stage" "$dependency")"
    else
        job_id="$(bash slurm/submit_stage.sh "$stage")"
    fi
    printf '%-32s %s\n' "$stage" "$job_id"
    dependency="$job_id"
done

