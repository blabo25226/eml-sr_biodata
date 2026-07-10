#!/usr/bin/env python3
"""Step 1: Multivariate EML-SR (CpG -> age_trans) with top-10 candidates."""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

import config
from metrics import dual_scale_metrics, metric_bundle
from utils import build_var_map, eval_formula, load_sr_data

warnings.filterwarnings("ignore")

try:
    import eml_sr_model_first_AI
except ImportError:
    sys.path.insert(0, str(config.ROOT.parent / "eml-sr_model_first_AI"))
    import eml_sr_model_first_AI


def loocv_formula(py_code: str, X: np.ndarray, n: int) -> np.ndarray:
    preds = np.zeros(n)
    for i in range(n):
        local = build_var_map(X[i : i + 1])
        try:
            preds[i] = float(eval_formula(py_code, local)[0])
        except Exception:
            preds[i] = np.nan
    return preds


def main() -> None:
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    meta, cpgs, X, y, ages = load_sr_data()
    n = len(y)

    print(f"Step 1 - EML-SR: {X.shape[1]} CpGs, {n} samples")

    searcher = eml_sr_model_first_AI.Searcher(
        max_complexity=config.MAX_COMPLEXITY,
        beam_width=config.BEAM_WIDTH,
        complexity_penalty=config.COMPLEXITY_PENALTY,
    )
    candidates = searcher.find_candidates(X.tolist(), y.tolist())
    print(f"  Pareto candidates: {len(candidates)}")

    results = []
    for cand in candidates:
        py_code = cand.to_python()
        local_all = build_var_map(X)
        try:
            y_pred = eval_formula(py_code, local_all)
        except Exception:
            continue
        if not np.all(np.isfinite(y_pred)):
            continue

        train_m = dual_scale_metrics(y, y_pred, ages)
        loocv_pred = loocv_formula(py_code, X, n)
        loocv_m = dual_scale_metrics(y, loocv_pred, ages)

        results.append({
            "formula": cand.formula,
            "latex": cand.to_latex(),
            "python": py_code,
            "complexity": cand.complexity,
            "cand_error": cand.error,
            **{f"train_{k}": v for k, v in train_m.items()},
            **{f"loocv_{k}": v for k, v in loocv_m.items()},
        })

    results.sort(key=lambda r: r["train_mse_trans"])
    top = results[: config.TOP_K_CANDIDATES]

    out_txt = config.RESULTS_DIR / "step1_eml_sr_results.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("EML-SR (first_AI) — eml-sr_model_fourth_AI\n")
        f.write(f"CpGs: top {config.N_CPG_FOR_SR} by |glmnet coef|\n")
        f.write(f"beam_width={config.BEAM_WIDTH}, max_complexity={config.MAX_COMPLEXITY}\n")
        f.write(f"Top {config.TOP_K_CANDIDATES} by train MSE (structure-fixed LOOCV)\n")
        f.write("=" * 60 + "\n")
        for i, res in enumerate(top):
            f.write(f"Rank {i + 1}\n")
            f.write(f"  Complexity: {res['complexity']}\n")
            f.write(f"  Train MSE: {res['train_mse_trans']:.6f}  R²: {res['train_r2_trans']:.4f}\n")
            f.write(f"  LOOCV MSE: {res['loocv_mse_trans']:.6f}  R²: {res['loocv_r2_trans']:.4f}\n")
            f.write(f"  LOOCV r (age): {res['loocv_r_age']:.4f}  MAE: {res['loocv_mae_age']:.4f}\n")
            f.write(f"  Formula: {res['formula']}\n")
            f.write(f"  LaTeX: {res['latex']}\n\n")
        f.write("CpG mapping (v_i):\n")
        for i, cpg in enumerate(cpgs):
            f.write(f"  v{i}: {cpg}\n")

    out_csv = config.RESULTS_DIR / "step1_eml_sr_candidates.csv"
    pd.DataFrame(top).to_csv(out_csv, index=False)

    with open(config.RESULTS_DIR / "step1_eml_sr_candidates.json", "w", encoding="utf-8") as f:
        json.dump(top, f, indent=2, ensure_ascii=False)

    if top:
        print(f"  Best train MSE: {top[0]['train_mse_trans']:.6f}")
        print(f"  Best LOOCV r (age): {top[0]['loocv_r_age']:.4f}")
    print(f"Saved {out_txt}")


if __name__ == "__main__":
    main()
