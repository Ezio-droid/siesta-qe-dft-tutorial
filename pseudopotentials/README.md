# Pseudopotentials

Pseudopotential binaries are intentionally not stored in this repository.

## SIESTA

Place these PseudoDojo PSML files under `pseudopotentials/siesta/`:

```text
C.psml
H.psml
Ni.psml
```

The tested ASE configuration uses an empty `pseudo_qualifier`, so filenames are
resolved directly rather than as `C.gga.psml`.

After copying, record checksums:

```bash
sha256sum pseudopotentials/siesta/*.psml \
  > pseudopotentials/siesta-checksums.sha256
```

## Quantum ESPRESSO

Place these UPF files under `pseudopotentials/qe/`:

```text
C.pbe-n-kjpaw_psl.1.0.0.UPF
H.pbe-rrkjus_psl.1.0.0.UPF
ni_pbe_v1.4.uspp.F.UPF
```

Checksums observed for the benchmark copies:

```text
5d2aebdfa2cae82b50a7e79e9516da0f  C.pbe-n-kjpaw_psl.1.0.0.UPF
f52b6d4d1c606e5624b1dc7b2218f220  H.pbe-rrkjus_psl.1.0.0.UPF
1ee80287db30b12d2bc1f57a5b5d6409  ni_pbe_v1.4.uspp.F.UPF
```

Obtain C and H from the Quantum ESPRESSO PSlibrary and Ni from the GBRV
library, subject to their respective terms. Do not substitute another file
with the same element symbol without reconverging the numerical settings.
If not then: https://drive.google.com/file/d/1WCKHWtrjmiD6gAsUvJhUpItDYMHlU3zj/view?usp=sharing
