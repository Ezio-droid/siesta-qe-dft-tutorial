# Reference results

## Included in Git

- Processed CSV and JSON summaries
- PNG figures
- Optimized `.traj` and `.xyz` structures
- Generated SIESTA and QE text outputs
- QE structures and the SIESTA benchmark NEB plot

## Separate release asset

`reference-raw-results-v1.tar.gz` contains additional raw calculation files,
including electrostatic-potential grids and the partial QE benchmark
directories. Wavefunctions, density-matrix restart files, pseudopotential
binaries, and QE `.save` wavefunction trees are intentionally excluded.

Extract from the repository root:

```bash
tar -xzf reference-raw-results-v1.tar.gz
```

## Completeness

The staged SIESTA workflow completed through stage 14. Its production NEB
stage was skipped. The exact shortened-notebook SIESTA benchmark completed,
including its separate non-spin-polarized NEB. QE was terminated at the
three-hour Slurm limit, so QE files are partial and must not be interpreted as
a fully completed tutorial workflow.
