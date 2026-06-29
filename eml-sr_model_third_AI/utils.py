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
