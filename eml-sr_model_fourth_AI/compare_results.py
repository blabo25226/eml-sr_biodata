#!/usr/bin/env python3
"""Aggregate LOOCV metrics from all pipeline steps."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import config

METRIC_COLS = [
    "loocv_mse_trans", "loocv_r2_trans", "loocv_r_trans", "loocv_mae_trans",
    "loocv_mse_age", "loocv_r2_age", "loocv_r_age", "loocv_mae_age",
]


def _row(method: str, n_features, formula: str, metrics: dict) -> dict:
    row = {
        "method": method,
        "n_features": n_features,
        "formula_or_model": formula,
    }
    for c in METRIC_COLS:
        row[c] = metrics.get(c)
    return row


def main() -> None:
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = []

    step0 = config.RESULTS_DIR / "step0_baseline.csv"
    if step0.exists():
        df = pd.read_csv(step0)
        rows.append(df.iloc[0].to_dict())

    step1 = config.RESULTS_DIR / "step1_eml_sr_candidates.csv"
    if step1.exists() and len(pd.read_csv(step1)) > 0:
        df = pd.read_csv(step1)
        best = df.iloc[0]
        rows.append(_row(
            "eml_sr",
            config.N_CPG_FOR_SR,
            best.get("formula", ""),
            {c.replace("loocv_", "loocv_"): best.get(c) for c in df.columns if c.startswith("loocv_")},
        ))

    step2 = config.RESULTS_DIR / "step2_pysr_candidates.csv"
    if step2.exists() and len(pd.read_csv(step2)) > 0:
        df = pd.read_csv(step2)
        best = df.iloc[0]
        rows.append(_row(
            "pysr",
            config.N_CPG_FOR_SR,
            best.get("equation", ""),
            {c: best.get(c) for c in df.columns if c.startswith("loocv_")},
        ))

    step3 = config.RESULTS_DIR / "step3_neural_sr_summary.csv"
    if step3.exists():
        df = pd.read_csv(step3)
        best = df.iloc[0]
        rows.append(_row(
            "eql_neural_sr",
            config.N_CPG_FOR_SR,
            best.get("formula_or_model", ""),
            {c: best.get(c) for c in df.columns if c.startswith("loocv_")},
        ))

    step4 = config.RESULTS_DIR / "step4_sim_summary.csv"
    if step4.exists():
        df = pd.read_csv(step4)
        best = df.iloc[0]
        rows.append(_row(
            "sparse_sim",
            config.N_CPG_FOR_SR,
            best.get("formula_or_model", ""),
            {c: best.get(c) for c in df.columns if c.startswith("loocv_")},
        ))

    out = pd.DataFrame(rows)
    out_path = config.RESULTS_DIR / "comparison_summary.csv"
    out.to_csv(out_path, index=False)

    with open(config.RESULTS_DIR / "comparison_summary.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    print("Comparison summary (LOOCV):")
    if len(out):
        display_cols = ["method", "loocv_r2_trans", "loocv_r_age", "loocv_mae_age"]
        print(out[display_cols].to_string(index=False))
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
