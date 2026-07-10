#!/usr/bin/env python3
"""Run fifth_AI pipeline: extract MCDB (if needed) -> R preprocess -> Steps 0-2 -> compare."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import config


def run_extract_mcdb() -> None:
    beta = config.MCDB_BETA_CSV
    meta = config.MCDB_META_CSV
    if beta.exists() and meta.exists():
        print("MCDB subset already present:", beta.name, meta.name)
        return
    script = config.ROOT / "extract_mcdb_cheetah.py"
    subprocess.run([sys.executable, str(script)], check=True, cwd=str(config.ROOT))


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

    if "all" in steps or "extract" in steps:
        run_extract_mcdb()

    if "all" in steps or "r" in steps:
        run_r_preprocess()

    if "all" in steps or "0" in steps:
        from step0_baseline_enet import main as s0

        s0()

    if "all" in steps or "1" in steps:
        from step1_eml_sr_fable import main as s1

        s1()

    if "all" in steps or "2" in steps:
        from step2_pysr import main as s2

        s2()

    if "all" in steps or "compare" in steps:
        from compare_results import main as cmp

        cmp()

    print("Pipeline finished.")


if __name__ == "__main__":
    main()
