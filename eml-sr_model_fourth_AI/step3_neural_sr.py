#!/usr/bin/env python3
"""Step 3: EQL-style neural symbolic regression (PyTorch + L1 sparsity)."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler

import config
from metrics import dual_scale_metrics
from utils import load_sr_data

ACTIVATIONS = ("identity", "sin", "exp")


def apply_activation(x: torch.Tensor, kind: str) -> torch.Tensor:
    if kind == "sin":
        return torch.sin(x)
    if kind == "exp":
        return torch.exp(torch.clamp(x, max=5.0))
    return x


class EQLNet(nn.Module):
    """Single hidden layer with per-unit activation type."""

    def __init__(self, n_in: int, n_hidden: int):
        super().__init__()
        self.w1 = nn.Parameter(torch.randn(n_in, n_hidden) * 0.1)
        self.b1 = nn.Parameter(torch.zeros(n_hidden))
        self.w2 = nn.Parameter(torch.randn(n_hidden) * 0.1)
        self.b2 = nn.Parameter(torch.zeros(1))
        # activation index per hidden unit (0=identity, 1=sin, 2=exp)
        self.act_idx = nn.Parameter(torch.randint(0, 3, (n_hidden,)).float(), requires_grad=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h_lin = x @ self.w1 + self.b1
        h = torch.zeros_like(h_lin)
        for j in range(h_lin.shape[1]):
            act = ACTIVATIONS[int(self.act_idx[j].item()) % len(ACTIVATIONS)]
            h[:, j] = apply_activation(h_lin[:, j], act)
        return h @ self.w2 + self.b2


def train_eql(X: np.ndarray, y: np.ndarray) -> tuple[EQLNet, StandardScaler]:
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    xt = torch.tensor(Xs, dtype=torch.float32)
    yt = torch.tensor(y.reshape(-1, 1), dtype=torch.float32)

    model = EQLNet(X.shape[1], config.EQL_HIDDEN)
    opt = torch.optim.Adam(model.parameters(), lr=config.EQL_LR)

    for _ in range(config.EQL_EPOCHS):
        opt.zero_grad()
        pred = model(xt)
        mse = torch.mean((pred - yt) ** 2)
        l1 = config.EQL_L1 * (torch.sum(torch.abs(model.w1)) + torch.sum(torch.abs(model.w2)))
        loss = mse + l1
        loss.backward()
        opt.step()

    return model, scaler


def predict_eql(model: EQLNet, scaler: StandardScaler, X: np.ndarray) -> np.ndarray:
    model.eval()
    Xs = scaler.transform(X)
    with torch.no_grad():
        pred = model(torch.tensor(Xs, dtype=torch.float32))
    return pred.numpy().ravel()


def extract_formula(
    model: EQLNet, scaler: StandardScaler, cpgs: list[str], threshold: float
) -> str:
    """Build human-readable approximate formula from sparse EQL weights."""
    mean = scaler.mean_
    scale = scaler.scale_
    terms = []
    w2 = model.w2.detach().numpy()
    w1 = model.w1.detach().numpy()
    b1 = model.b1.detach().numpy()
    b2 = float(model.b2.item())

    for j in range(len(w2)):
        if abs(w2[j]) < threshold:
            continue
        act = ACTIVATIONS[int(model.act_idx[j].item()) % len(ACTIVATIONS)]
        inner_parts = []
        for i, cpg in enumerate(cpgs):
            w = w2[j] * w1[i, j] / scale[i]
            if abs(w) < threshold:
                continue
            inner_parts.append(f"{w:.4f}*{cpg}")
        if not inner_parts:
            continue
        inner = " + ".join(inner_parts)
        bias_term = w2[j] * b1[j]
        if abs(bias_term) > threshold:
            inner = f"{inner} + {bias_term:.4f}"
        terms.append(f"{w2[j]:.4f}*{act}({inner})")

    if abs(b2) > threshold:
        terms.append(f"{b2:.4f}")
    return " + ".join(terms) if terms else "0"


def loocv_eql(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """LOOCV: retrain EQL on n-1 samples per fold (architecture fixed)."""
    n = len(y)
    preds = np.zeros(n)
    epochs = config.EQL_LOOCV_EPOCHS
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        scaler = StandardScaler()
        Xs = scaler.fit_transform(X[mask])
        xt = torch.tensor(Xs, dtype=torch.float32)
        yt = torch.tensor(y[mask].reshape(-1, 1), dtype=torch.float32)
        model = EQLNet(X.shape[1], config.EQL_HIDDEN)
        opt = torch.optim.Adam(model.parameters(), lr=config.EQL_LR)
        for _ in range(epochs):
            opt.zero_grad()
            pred = model(xt)
            mse = torch.mean((pred - yt) ** 2)
            l1 = config.EQL_L1 * (torch.sum(torch.abs(model.w1)) + torch.sum(torch.abs(model.w2)))
            (mse + l1).backward()
            opt.step()
        preds[i] = float(predict_eql(model, scaler, X[i : i + 1])[0])
    return preds


def main() -> None:
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    meta, cpgs, X, y, ages = load_sr_data()

    print(f"Step 3 - EQL neural SR: {X.shape[1]} CpGs, {len(y)} samples")

    model, scaler = train_eql(X, y)
    y_pred = predict_eql(model, scaler, X)
    train_m = dual_scale_metrics(y, y_pred, ages)

    # LOOCV (refit per fold)
    loocv_pred = loocv_eql(X, y)
    loocv_m = dual_scale_metrics(y, loocv_pred, ages)

    formula = extract_formula(model, scaler, cpgs, config.EQL_WEIGHT_THRESHOLD)

    row = {
        "method": "eql_neural_sr",
        "rank": 1,
        "formula_or_model": formula,
        "n_hidden": config.EQL_HIDDEN,
        **{f"train_{k}": v for k, v in train_m.items()},
        **{f"loocv_{k}": v for k, v in loocv_m.items()},
    }

    out_csv = config.RESULTS_DIR / "step3_neural_sr_summary.csv"
    pd.DataFrame([row]).to_csv(out_csv, index=False)

    with open(config.RESULTS_DIR / "step3_neural_sr_summary.json", "w", encoding="utf-8") as f:
        json.dump(row, f, indent=2, ensure_ascii=False)

    out_txt = config.RESULTS_DIR / "step3_neural_sr_results.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("EQL-style neural symbolic regression\n")
        f.write(f"Hidden units: {config.EQL_HIDDEN}\n")
        f.write(f"Extracted formula (L1 threshold={config.EQL_WEIGHT_THRESHOLD}):\n  {formula}\n")
        f.write(f"Train  MSE: {train_m['mse_trans']:.6f}  R²: {train_m['r2_trans']:.4f}\n")
        f.write(f"LOOCV  MSE: {loocv_m['mse_trans']:.6f}  R²: {loocv_m['r2_trans']:.4f}\n")
        f.write(f"LOOCV  r (age): {loocv_m['r_age']:.4f}  MAE: {loocv_m['mae_age']:.4f}\n")

    print(f"  Formula: {formula[:80]}...")
    print(f"  LOOCV r (age): {loocv_m['r_age']:.4f}")
    print(f"Saved {out_csv}")


if __name__ == "__main__":
    main()
