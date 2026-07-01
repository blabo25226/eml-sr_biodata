#!/usr/bin/env python3
"""Step 2: PySR genetic programming symbolic regression."""
from __future__ import annotations

import json
import os
import sys
import warnings

# Prefer standalone Julia (avoids Anaconda libcurl issues on Windows)
_DEFAULT_JULIA = r"C:\Users\blani\AppData\Local\Programs\Julia-1.12.6\bin\julia.exe"
if "JULIA_EXE" not in os.environ and os.path.isfile(_DEFAULT_JULIA):
    os.environ["JULIA_EXE"] = _DEFAULT_JULIA

import numpy as np
import pandas as pd

import config
from metrics import dual_scale_metrics
from utils import load_sr_data, pearson_r

warnings.filterwarnings("ignore")


def sympy_to_numpy(code: str) -> str:
    replacements = {
        "sin": "np.sin",
        "cos": "np.cos",
        "exp": "np.exp",
        "log": "np.log",
        "sqrt": "np.sqrt",
        "square": "np.square",
    }
    out = code
    for k, v in replacements.items():
        out = out.replace(k, v)
    return out


def eval_pysr_formula(equation_str: str, X: np.ndarray) -> np.ndarray:
    n_features = X.shape[1]
    local = {f"x{i}": X[:, i] for i in range(n_features)}
    py_code = sympy_to_numpy(equation_str)
    y = eval(py_code, {"np": np}, local)
    if np.isscalar(y):
        return np.full(len(X), float(y))
    return np.asarray(y, dtype=float)


def loocv_pysr(equation_str: str, X: np.ndarray, n: int) -> np.ndarray:
    preds = np.zeros(n)
    for i in range(n):
        try:
            preds[i] = float(eval_pysr_formula(equation_str, X[i : i + 1])[0])
        except Exception:
            preds[i] = np.nan
    return preds


def main() -> None:
    try:
        from pysr import PySRRegressor
    except ImportError as exc:
        print("PySR not installed. Skip step 2.", file=sys.stderr)
        print(f"  {exc}", file=sys.stderr)
        sys.exit(0)

    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    meta, cpgs, X, y, ages = load_sr_data()
    n = len(y)

    print(f"Step 2 - PySR: {X.shape[1]} CpGs, {n} samples")

    feature_names = [f"x{i}" for i in range(X.shape[1])]
    model = PySRRegressor(
        niterations=config.PYSR_NITERATIONS,
        populations=config.PYSR_POPULATIONS,
        population_size=config.PYSR_POPULATION_SIZE,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["exp", "log", "sin", "cos"],
        maxsize=20,
        verbosity=0,
        progress=False,
        random_state=42,
    )
    model.fit(X, y, variable_names=feature_names)

    eq_df = model.equations_
    if eq_df is None or len(eq_df) == 0:
        print("PySR returned no equations.")
        return

    eq_df = eq_df.sort_values("loss").reset_index(drop=True)
    top = eq_df.head(config.TOP_K_CANDIDATES)

    results = []
    for rank, row in top.iterrows():
        eq_str = str(row["equation"])
        try:
            y_pred = eval_pysr_formula(eq_str, X)
        except Exception:
            continue
        if not np.all(np.isfinite(y_pred)):
            continue

        train_m = dual_scale_metrics(y, y_pred, ages)
        loocv_pred = loocv_pysr(eq_str, X, n)
        loocv_m = dual_scale_metrics(y, loocv_pred, ages)

        results.append({
            "rank": rank + 1,
            "equation": eq_str,
            "complexity": float(row.get("complexity", np.nan)),
            "loss": float(row.get("loss", np.nan)),
            "score": float(row.get("score", np.nan)),
            **{f"train_{k}": v for k, v in train_m.items()},
            **{f"loocv_{k}": v for k, v in loocv_m.items()},
        })

    out_csv = config.RESULTS_DIR / "step2_pysr_candidates.csv"
    pd.DataFrame(results).to_csv(out_csv, index=False)

    with open(config.RESULTS_DIR / "step2_pysr_candidates.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    out_txt = config.RESULTS_DIR / "step2_pysr_results.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("PySR symbolic regression — eml-sr_model_fourth_AI\n")
        f.write(f"Top {config.TOP_K_CANDIDATES} by loss (structure-fixed LOOCV)\n")
        f.write("=" * 60 + "\n")
        for res in results:
            f.write(f"Rank {res['rank']}\n")
            f.write(f"  Complexity: {res['complexity']}\n")
            f.write(f"  Train MSE: {res['train_mse_trans']:.6f}  R²: {res['train_r2_trans']:.4f}\n")
            f.write(f"  LOOCV MSE: {res['loocv_mse_trans']:.6f}  R²: {res['loocv_r2_trans']:.4f}\n")
            f.write(f"  LOOCV r (age): {res['loocv_r_age']:.4f}\n")
            f.write(f"  Equation: {res['equation']}\n\n")
        f.write("Feature mapping (x_i):\n")
        for i, cpg in enumerate(cpgs):
            f.write(f"  x{i}: {cpg}\n")

    if results:
        print(f"  Best train MSE: {results[0]['train_mse_trans']:.6f}")
        print(f"  Best LOOCV r (age): {results[0]['loocv_r_age']:.4f}")
    print(f"Saved {out_csv}")


if __name__ == "__main__":
    main()
