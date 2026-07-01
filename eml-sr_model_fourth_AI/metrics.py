"""Unified evaluation metrics for all pipeline steps."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import config
from utils import asm_inv_transform, pearson_r


@dataclass
class MetricBundle:
    mse: float
    r2: float
    r: float
    mae: float


def metric_bundle(y_true: np.ndarray, y_pred: np.ndarray) -> MetricBundle:
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    yt = np.asarray(y_true, dtype=float)[mask]
    yp = np.asarray(y_pred, dtype=float)[mask]
    if len(yt) < 2:
        return MetricBundle(float("nan"), float("nan"), float("nan"), float("nan"))
    return MetricBundle(
        mse=float(mean_squared_error(yt, yp)),
        r2=float(r2_score(yt, yp)),
        r=pearson_r(yt, yp),
        mae=float(mean_absolute_error(yt, yp)),
    )


def dual_scale_metrics(
    y_trans_true: np.ndarray,
    y_trans_pred: np.ndarray,
    ages_true: np.ndarray | None = None,
) -> dict[str, float]:
    trans = metric_bundle(y_trans_true, y_trans_pred)
    out = {
        "mse_trans": trans.mse,
        "r2_trans": trans.r2,
        "r_trans": trans.r,
        "mae_trans": trans.mae,
    }
    if ages_true is not None:
        age_pred = asm_inv_transform(y_trans_pred, config.ASM, config.ASM_K)
        age = metric_bundle(ages_true, age_pred)
        out.update({
            "mse_age": age.mse,
            "r2_age": age.r2,
            "r_age": age.r,
            "mae_age": age.mae,
        })
    return out


def metrics_to_row(prefix: str, m: dict[str, float]) -> dict[str, float]:
    return {f"{prefix}_{k}": v for k, v in m.items()}
