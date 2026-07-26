# Notebooks

The original tutorial notebooks were created by **Aleksandar Staykov, PhD**,
Associate Professor and Principal Investigator at the International Institute
for Carbon-Neutral Energy Research (WPI-I²CNER), Kyushu University.

| Notebook | Purpose |
|---|---|
| `tutorial-short.ipynb` | Shorter version supplied for the conference |
| `tutorial-full-reference.ipynb` | Original complete reference notebook |
| `extended-ghost-neb/tutorial-extended-ghost-neb.ipynb` | Extended version with an additional SIESTA ghost-atom NEB workflow |
| `narval-segments/*.ipynb` | Headless benchmark copies split by required Narval toolchain |

The word “short” refers to the tutorial author's shortened content, not a
guaranteed one-hour runtime. The complete shortened notebook exceeded five
hours in the Narval benchmark and QE remained incomplete.

For the conference session, follow `../docs/ONE_HOUR_ROUTE.md`.

The extended ghost-atom notebook is intended for exploration after the
tutorial. Its core calculations already exceed five hours when run in full,
before accounting for the additional ghost-atom optimizations and NEB. Supplied
trajectory files and a completed NEB profile are stored beside the notebook.

The original notebooks retain local workstation paths and interactive viewer
calls. The staged scripts under `../scripts/` and `../slurm/` are the preferred
Narval interface.
