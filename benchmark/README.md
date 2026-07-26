# Runtime benchmark

The shortened notebook was executed headlessly on Narval with ten MPI ranks.
Compiler-dependent sections were separated but run sequentially.

| Segment | Status | Wall time |
|---|---:|---:|
| SIESTA DFT | Succeeded | 85.15 min |
| SIESTA work-function postprocessing | Succeeded | 4.80 min |
| SIESTA graphene and NEB | Succeeded | 43.72 min |
| Total completed SIESTA | Succeeded | 133.67 min |
| QE | Slurm time limit | 180 min |

Observed execution exceeded 313.67 minutes, and QE did not complete.

The slowest SIESTA cell was the low-accuracy H-terminated slab optimization
(57.22 min), followed by the notebook NEB (21.78 min).

Machine-readable timestamps are under `timings/`; calculation-level durations
are in `cell-timings.csv`. The QE job has no timing JSON because Slurm
terminated the process externally.
