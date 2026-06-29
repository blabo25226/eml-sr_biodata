"""Shared helpers for evaluating eml-sr formulas."""
from __future__ import annotations

import re
import numpy as np


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


def invert_link(python_code: str, eta_target: float, y_min: float, y_max: float, n_grid: int = 800) -> float:
    """Find y such that g(y) ~= eta_target for link g defined by python_code (v0 -> g)."""
    ys = np.linspace(y_min, y_max, n_grid)
    g_vals = eval_formula(python_code, {"v0": ys})
    idx = int(np.argmin((g_vals - eta_target) ** 2))
    return float(ys[idx])
