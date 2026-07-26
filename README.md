# SIESTA and Quantum ESPRESSO tutorial

Conference tutorial materials for running introductory density-functional
theory calculations through the Atomic Simulation Environment (ASE), using
SIESTA and Quantum ESPRESSO (QE).

The repository contains both tutorial notebooks, generated input files,
Narval/Alliance Canada job scripts, and precomputed reference results. The
precomputed files are intentional: a benchmark of the shortened notebook
showed that executing every calculation requires more than five hours and the
QE section still did not finish within its three-hour allocation.

## Notebook author

The original tutorial notebooks were created by:

**Aleksandar Staykov, PhD**  
Associate Professor and Principal Investigator  
International Institute for Carbon-Neutral Energy Research (WPI-I²CNER)  
Kyushu University

The Narval execution workflow, generated inputs, benchmark records, and
reference outputs in this repository are supporting materials prepared to make
the notebooks practical for the conference tutorial.

## Start here

| Goal | Use |
|---|---|
| Follow the conference session | [`docs/ONE_HOUR_ROUTE.md`](docs/ONE_HOUR_ROUTE.md) |
| Open the shortened notebook | [`notebooks/tutorial-short.ipynb`](notebooks/tutorial-short.ipynb) |
| Study the complete notebook | [`notebooks/tutorial-full-reference.ipynb`](notebooks/tutorial-full-reference.ipynb) |
| Explore the ghost-atom NEB extension afterward | [`notebooks/extended-ghost-neb/`](notebooks/extended-ghost-neb/) |
| Run the restartable SIESTA workflow on Narval | [`docs/NARVAL.md`](docs/NARVAL.md) |
| Inspect generated inputs | [`inputs/`](inputs/) |
| Use precomputed results | [`reference-results/`](reference-results/) |
| Review measured runtimes | [`benchmark/README.md`](benchmark/README.md) |

> **Do not use “Run all” during the one-hour tutorial.** Follow the one-hour
> route and load the supplied results for expensive calculations.

## What students should run live

The recommended live path is:

1. Build and visualize diamond with ASE.
2. Run one small SIESTA single-point calculation.
3. Plot supplied SIESTA convergence data.
4. Inspect supplied optimized structures, DOS, and surface potentials.
5. Run one small QE single-point calculation.
6. Compare SIESTA and QE inputs and results.

Geometry optimizations, convergence sweeps, work-function production runs,
Ni/graphene optimizations, and NEB calculations should use the supplied
reference files.

## Repository contents

```text
notebooks/
  tutorial-short.ipynb             Shortened notebook supplied for the tutorial
  tutorial-full-reference.ipynb    Original full notebook
  extended-ghost-neb/              Post-tutorial extension and supplied assets
  narval-segments/                 Headless benchmark copies split by toolchain
inputs/
  siesta/                          Generated SIESTA FDF inputs
  qe/                              Generated QE PW/PP inputs
reference-results/
  siesta/data/                     CSV and JSON summaries
  siesta/figures/                  Convergence, DOS, and potential plots
  siesta/structures/               Optimized ASE trajectory and XYZ files
  siesta/selected-outputs/         Readable SIESTA outputs
  qe/                              Partial QE benchmark outputs and structures
benchmark/                         Cell timings and Slurm logs
scripts/                           Restartable calculation and analysis drivers
slurm/                             Narval submission scripts
pseudopotentials/                  Required names, checksums, and acquisition notes
```

## Reference-result status

### Validated SIESTA staged workflow

Stages 00–14 completed. This includes bulk convergence and optimization, bulk
and surface DOS, pristine and H-terminated slabs, both surface ionization
potentials, graphene k-point convergence, and two optimized Ni/graphene
endpoints. Stage 15 NEB was deliberately not run in this production workflow.

Selected values:

- Optimized diamond lattice parameter: **3.591774 Å**
- H-terminated-slab ionization potential: **2.629165 eV**
- Pristine-slab ionization potential: **6.692514 eV**
- Ni endpoint energies agree within approximately **0.000063 eV**

### Exact shortened-notebook benchmark

- Completed SIESTA portions: **133.67 min**
- QE allocation: **180 min**, terminated by the Slurm time limit
- Observed total: **at least 313.67 min**

The benchmark SIESTA Ni/graphene cells follow the notebook exactly and are
non-spin-polarized. The restartable staged workflow uses spin-polarized Ni and
is the preferred physical reference.

## Clone

```bash
git clone https://github.com/Ezio-droid/siesta-qe-dft-tutorial.git
cd siesta-qe-dft-tutorial
```

Then follow [`docs/NARVAL.md`](docs/NARVAL.md) or
[`docs/ONE_HOUR_ROUTE.md`](docs/ONE_HOUR_ROUTE.md).

## Pseudopotentials

Pseudopotential binaries are not committed. Obtain the exact C, H, and Ni
files described in [`pseudopotentials/README.md`](pseudopotentials/README.md)
and verify their checksums. This avoids silently mixing incompatible
pseudopotential families and respects third-party distribution terms.

## Large raw outputs

Readable inputs and compact outputs are included in Git. Volumetric grids and
additional raw calculation files are packaged separately as
`reference-raw-results-v1.tar.gz`, intended to be attached to the GitHub
Release. See [`reference-results/README.md`](reference-results/README.md).

## Reproducibility notes

- Narval benchmark modules: SIESTA 5.4.0 and Quantum ESPRESSO 7.5.
- The notebook prose mentions Mg in places, but the implemented diffusion
  example uses **Ni**.
- Numerical settings are tutorial settings and are not automatically suitable
  for unrelated production systems.
- The QE reference directory is incomplete because the benchmark reached its
  three-hour time limit. It is retained as an honest partial record.

## Citation

If these materials contribute to published work, cite ASE, SIESTA, Quantum
ESPRESSO, and the pseudopotential libraries used. Suggested references are in
[`CITATION.md`](CITATION.md).

## Licensing

Scripts added for the Narval workflow are provided under the MIT License.
Notebook text and third-party tutorial material remain subject to the rights
of their respective contributors; see [`LICENSES.md`](LICENSES.md).
