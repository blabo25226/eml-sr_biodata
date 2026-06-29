#!/usr/bin/env python3
"""Multivariate symbolic regression (CpG -> age_trans) with eml-sr_model_first_AI."""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

import config
from utils import build_var_map, eval_formula, pearson_r

warnings.filterwarnings("ignore")

try:
    import eml_sr_model_first_AI
except ImportError:
    sys.path.insert(0, str(config.ROOT.parent / "eml-sr_model_first_AI"))
    import eml_sr_model_first_AI


def load_data():
    meta = pd.read_csv(config.CLOCK_SAMPLES_CSV, index_col=0)
    beta = pd.read_csv(config.BETA_COMBAT_CSV, index_col=0)
    cpgs = pd.read_csv(config.SELECTED_CPGS_CSV)
    top = cpgs.head(config.N_CPG_FOR_SR)["CpG"].tolist()
    beta = beta.loc[meta.index, top]
    X = beta.values.astype(float)
    y = meta["age_trans"].values.astype(float)
    ages = meta["Age"].values.astype(float)
    return meta, top, X, y, ages


def loocv_predict_formula(formula_py: str, X: np.ndarray, y: np.ndarray) -> np.ndarray:
    n = len(y)
    preds = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        X_tr, y_tr = X[mask], y[mask]
        # Structure fixed; coefficients were fit on full data by eml-sr.
        # LOOCV: evaluate on held-out row using formula from full-data search.
        local = build_var_map(X[i : i + 1])
        try:
            preds[i] = float(eval_formula(formula_py, local)[0])
        except Exception:
            preds[i] = np.nan
    return preds


def main():
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    meta, cpgs, X, y, ages = load_data()

    print(f"EML-SR: {X.shape[1]} CpGs, {X.shape[0]} samples")
    print(f"Settings: max_complexity={config.MAX_COMPLEXITY}, beam_width={config.BEAM_WIDTH}")

    searcher = eml_sr_model_first_AI.Searcher(
        max_complexity=config.MAX_COMPLEXITY,
        beam_width=config.BEAM_WIDTH,
        complexity_penalty=config.COMPLEXITY_PENALTY,
    )

    inputs = X.tolist()
    candidates = searcher.find_candidates(inputs, y.tolist())
    print(f"Found {len(candidates)} Pareto candidates")

    results = []
    for cand in candidates:
        py_code = cand.to_python()
        local_all = build_var_map(X)
        try:
            y_pred = eval_formula(py_code, local_all)
        except Exception:
            continue
        if np.isnan(y_pred).any() or np.isinf(y_pred).any():
            continue

        # age_trans scale metrics
        mse = float(np.mean((y_pred - y) ** 2))
        r_trans = pearson_r(y, y_pred)

        results.append({
            "formula": cand.formula,
            "latex": cand.to_latex(),
            "python": py_code,
            "complexity": cand.complexity,
            "train_mse": mse,
            "train_r_age_trans": r_trans,
            "cand_error": cand.error,
        })

    results.sort(key=lambda r: r["train_mse"])

    out_txt = config.RESULTS_DIR / "eml_sr_results.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("EML-SR (first_AI) on paper-style preprocessed data\n")
        f.write(f"CpGs: top {config.N_CPG_FOR_SR} by |glmnet coef|\n")
        f.write(f"beam_width={config.BEAM_WIDTH}, max_complexity={config.MAX_COMPLEXITY}\n")
        f.write("=" * 60 + "\n")
        for i, res in enumerate(results[:15]):
            f.write(f"Rank {i + 1}\n")
            f.write(f"  Complexity: {res['complexity']}\n")
            f.write(f"  Train MSE (age_trans): {res['train_mse']:.6f}\n")
            f.write(f"  Train r (age_trans): {res['train_r_age_trans']:.4f}\n")
            f.write(f"  Formula: {res['formula']}\n")
            f.write(f"  LaTeX: {res['latex']}\n\n")

        f.write("CpG mapping (v_i):\n")
        for i, cpg in enumerate(cpgs):
            f.write(f"  v{i}: {cpg}\n")

    with open(config.RESULTS_DIR / "eml_sr_results.json", "w", encoding="utf-8") as f:
        json.dump(results[:15], f, indent=2, ensure_ascii=False)

    if results:
        print(f"Best train MSE: {results[0]['train_mse']:.6f}, r: {results[0]['train_r_age_trans']:.4f}")
    print(f"Saved {out_txt}")


if __name__ == "__main__":
    main()
