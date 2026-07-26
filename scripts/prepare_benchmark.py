#!/usr/bin/env python3
"""Create clean Narval-ready segments from the shortened tutorial notebook."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "notebooks" / "tutorial-short.ipynb"
OUTPUT_DIR = ROOT / "notebooks" / "narval-segments"


def patch_source(source):
    text = "".join(source)
    text = text.replace(
        "'/Users/staykov/pseudodojo'",
        'os.environ["SIESTA_PSEUDO_DIR"]',
    )
    text = text.replace(
        '"/Users/staykov/pseudo_espresso"',
        'os.environ["QE_PSEUDO_DIR"]',
    )
    text = text.replace("pseudo_qualifier='gga'", "pseudo_qualifier=''")
    text = text.replace(
        "mpirun --mca btl self,tcp -n 10 pw.x",
        "srun --exclusive --ntasks=10 --cpus-per-task=1 pw.x",
    )
    text = text.replace(
        "'H.pbe-rrkjus_psl.1.0.0.UPF '",
        "'H.pbe-rrkjus_psl.1.0.0.UPF'",
    )
    text = text.replace(
        'os.system("pp.x < pp.in > pp.out")',
        'os.system("srun --exclusive --ntasks=1 pp.x < pp.in > pp.out")',
    )
    return text.splitlines(keepends=True)


def make_notebook(original, cells, name, source_overrides=None):
    source_overrides = source_overrides or {}
    notebook = {
        key: value
        for key, value in original.items()
        if key not in {"cells"}
    }
    notebook["cells"] = []
    for original_index in cells:
        cell = dict(original["cells"][original_index])
        source = source_overrides.get(original_index, cell.get("source", []))
        cell["source"] = patch_source(source)
        cell["outputs"] = []
        cell["execution_count"] = None
        metadata = dict(cell.get("metadata", {}))
        metadata["original_cell_index"] = original_index
        cell["metadata"] = metadata
        notebook["cells"].append(cell)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / name).write_text(json.dumps(notebook, indent=1) + "\n")


def main():
    original = json.loads(SOURCE.read_text())
    wf_h = "".join(original["cells"][24]["source"])
    wf_p = "".join(original["cells"][26]["source"])

    # Keep SIESTA DFT in the Intel job and move sisl/netCDF reading into the
    # GCC/mpi4py job required by Alliance's Python modules.
    wf_h_dft = wf_h.split("\nimport sisl\n", 1)[0] + '\nos.chdir("../")\n'
    wf_p_dft = wf_p.replace("import sisl\n", "").split(
        "# --------------------------------------------------\n# Read electrostatic potential",
        1,
    )[0] + '\nos.chdir("../")\n'

    wf_h_post = (
        "import os\nos.chdir('c2_siesta_wf_slab_h')\nimport sisl\n"
        + wf_h.split("\nimport sisl\n", 1)[1]
    )
    wf_p_post = (
        "import os\nimport sisl\nimport numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "os.chdir('c2_siesta_wf_slab_h_non')\n"
        "# --------------------------------------------------\n# Read electrostatic potential"
        + wf_p.split(
            "# --------------------------------------------------\n# Read electrostatic potential",
            1,
        )[1]
    )

    make_notebook(
        original,
        range(0, 27),
        "01_siesta_dft.ipynb",
        {24: wf_h_dft.splitlines(True), 26: wf_p_dft.splitlines(True)},
    )

    post = {
        key: value for key, value in original.items() if key != "cells"
    }
    post["cells"] = []
    for original_index, source in [(24, wf_h_post), (26, wf_p_post)]:
        cell = dict(original["cells"][original_index])
        cell["source"] = patch_source(source.splitlines(True))
        cell["outputs"] = []
        cell["execution_count"] = None
        cell["metadata"] = {"original_cell_index": original_index}
        post["cells"].append(cell)
    (OUTPUT_DIR / "02_siesta_postprocess.ipynb").write_text(
        json.dumps(post, indent=1) + "\n"
    )

    make_notebook(
        original, range(27, 36), "03_siesta_neb.ipynb"
    )
    make_notebook(original, range(36, 66), "04_qe.ipynb")
    print("Prepared four benchmark notebook segments")


if __name__ == "__main__":
    main()
