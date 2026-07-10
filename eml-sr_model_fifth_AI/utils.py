"""Shared helpers for data loading and formula evaluation."""
from __future__ import annotations

import numpy as np
import pandas as pd

import config


def normalize_python_formula(code: str) -> str:
    code = code.replace("v_{", "v").replace("}", "")
    code = code.replace("p_{", "p")
    return code


def eval_formula(code: str, local_vars: dict) -> np.ndarray:
    py_code = normalize_python_formula(code)
    y = eval(py_code, {"np": np}, local_vars)
    if np.isscalar(y):
        return np.full(len(next(iter(local_vars.values()))), float(y))
    return np.asarray(y, dtype=float)


def build_var_map(X: np.ndarray, prefix: str = "v") -> dict:
    return {f"{prefix}{i}": X[:, i] for i in range(X.shape[1])}


def pearson_r(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def asm_inv_transform(y: np.ndarray, asm: float = 2.0, k: float = 0.2) -> np.ndarray:
    """Inverse ASM (CheetahClock_age_sex.Rmd)."""
    out = np.empty_like(y, dtype=float)
    for i, val in enumerate(y):
        if val < 0:
            out[i] = (asm + k) * np.exp(val) - k
        else:
            out[i] = (asm + k) * val + asm
    return out


def load_sr_data():
    """Load top N CpGs and age_trans for symbolic-regression steps."""
    meta = pd.read_csv(config.CLOCK_SAMPLES_CSV, index_col=0)
    beta = pd.read_csv(config.BETA_COMBAT_CSV, index_col=0)
    cpgs_df = pd.read_csv(config.SELECTED_CPGS_CSV)
    cpgs = cpgs_df.head(config.N_CPG_FOR_SR)["CpG"].tolist()
    beta = beta.loc[meta.index, cpgs]
    X = beta.values.astype(float)
    y = meta["age_trans"].values.astype(float)
    ages = meta["Age"].values.astype(float)
    return meta, cpgs, X, y, ages


def loocv_fixed_formula(predict_fn, n: int) -> np.ndarray:
    """Structure-fixed LOOCV: predict held-out i using model/formula fit on all data."""
    preds = np.zeros(n)
    for i in range(n):
        preds[i] = float(predict_fn(i))
    return preds
