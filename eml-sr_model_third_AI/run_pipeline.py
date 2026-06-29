#!/usr/bin/env python3
"""Run full third_AI pipeline: R preprocess -> Python SR."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import config


def run_r_preprocess() -> None:
    rscript = Path(config.RSCRIPT)
    if not rscript.exists():
        raise FileNotFoundError(
            f"Rscript not found at {rscript}. Set config.RSCRIPT to your R installation."
        )
    cmd = [str(rscript), str(config.PREPROCESS_R)]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=str(config.ROOT))


def main() -> None:
    steps = sys.argv[1:] or ["all"]

    if "all" in steps or "r" in steps:
        run_r_preprocess()

    if "all" in steps or "eml" in steps:
        from train_eml_sr import main as eml_main

        eml_main()

    if "all" in steps or "link" in steps:
        from train_link_sr import main as link_main

        link_main()

    print("Pipeline finished.")


if __name__ == "__main__":
    main()
