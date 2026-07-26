# Extended ghost-atom NEB notebook

This directory contains an extended version of Aleksandar Staykov’s tutorial
notebook. It adds two SIESTA Ni/graphene endpoint optimizations using ghost
carbon atoms and a second SIESTA NEB calculation.

Open:

```text
tutorial-extended-ghost-neb.ipynb
```

## Runtime warning

This notebook is for study after the conference session. Do not use **Run
All** during the one-hour tutorial. The previously benchmarked core took
133.67 minutes for its completed SIESTA sections, and its QE section exceeded
a 180-minute allocation. The ghost-atom optimizations and NEB add further
runtime.

Precomputed `.traj` files and `neb_profile.png` are provided so that students
can inspect the structures and result without repeating the expensive
calculations.

## Portable paths

The original workstation-specific pseudopotential paths were replaced with:

```text
../../pseudopotentials/siesta
../../pseudopotentials/qe
```

Copy the required pseudopotentials into those repository directories as
described in `../../pseudopotentials/README.md`. Pseudopotential binaries from
the submitted archive are not redistributed here.

On Narval, start Jupyter in a compute allocation and set the QE launcher when
needed:

```bash
export ASE_ESPRESSO_COMMAND="srun --ntasks=10 pw.x"
```

The notebook retains executed outputs as a reference record.
