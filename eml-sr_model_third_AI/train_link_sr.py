#!/usr/bin/env python3
"""Discover GLM link g(Age) via univariate symbolic regression (first_AI)."""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet

import config
from utils import eval_formula, pearson_r

warnings.filterwarnings("ignore")

try:
    import eml_sr_model_first_AI
except ImportError:
    sys.path.insert(0, str(config.ROOT.parent / "eml-sr_model_first_AI"))
    import eml_sr_model_first_AI


def asm_transform(age: np.ndarray) -> np.ndarray:
    k = config.ASM_K
    asm = config.ASM
    out = np.empty_like(age, dtype=float)
    for i, x in enumerate(age):
        if x < asm:
            out[i] = np.log((x + k) / (asm + k))
        else:
            out[i] = (x - asm) / (asm + k)
    return out


def load_data():
    meta = pd.read_csv(config.CLOCK_SAMPLES_CSV, index_col=0)
    beta = pd.read_csv(config.BETA_COMBAT_CSV, index_col=0)
    cpgs = pd.read_csv(config.SELECTED_CPGS_CSV)
    top = cpgs.head(config.N_CPG_FOR_SR)["CpG"].tolist()
    X = beta.loc[meta.index, top].values.astype(float)
    ages = meta["Age"].values.astype(float)
    age_trans = meta["age_trans"].values.astype(float)
    return ages, age_trans, X, cpgs


def run_link_sr(ages: np.ndarray, targets: np.ndarray, label: str, searcher) -> list:
    xs = ages.reshape(-1, 1).tolist()
    ys = targets.tolist()
    candidates = searcher.find_candidates(xs, ys)

    rows = []
    for cand in candidates:
        py_code = cand.to_python()
        local = {"v0": ages}
        try:
            pred = eval_formula(py_code, local)
        except Exception:
            continue
        if np.isnan(pred).any() or np.isinf(pred).any():
            continue
        mse = float(np.mean((pred - targets) ** 2))
        r = pearson_r(targets, pred)
        rows.append({
            "task": label,
            "formula": cand.formula,
            "latex": cand.to_latex(),
            "python": py_code,
            "complexity": cand.complexity,
            "mse": mse,
            "r": r,
        })
    rows.sort(key=lambda x: x["mse"])
    return rows


def main():
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ages, age_trans, X, cpgs = load_data()

    searcher = eml_sr_model_first_AI.Searcher(
        max_complexity=min(config.MAX_COMPLEXITY, 8),
        beam_width=config.BEAM_WIDTH,
        complexity_penalty=config.COMPLEXITY_PENALTY,
    )

    # Reference linear score from Elastic Net (same CpGs)
    enet = ElasticNet(alpha=0.01, l1_ratio=config.ENET_L1_RATIO, max_iter=10000)
    enet.fit(X, age_trans)
    enet_score = enet.predict(X)

    asm_ref = asm_transform(ages)
    asm_mse = float(np.mean((asm_ref - age_trans) ** 2))

    all_results = []

    # A: reproduce ASM link (Age -> age_trans)
    res_a = run_link_sr(ages, age_trans, "A_ASM_reproduction", searcher)
    all_results.extend(res_a[:5])

    # B: data-driven link (Age -> EN linear score)
    res_b = run_link_sr(ages, enet_score, "B_EN_score_link", searcher)
    all_results.extend(res_b[:5])

    out = config.RESULTS_DIR / "link_sr_results.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write("Link function symbolic regression (first_AI, univariate)\n")
        f.write(f"ASM reference MSE vs stored age_trans: {asm_mse:.6e}\n")
        f.write("=" * 60 + "\n")

        f.write("\n## Task A: Age -> age_trans (compare to fixed ASM)\n")
        for i, r in enumerate(res_a[:5]):
            f.write(f"Rank {i+1}: MSE={r['mse']:.6f}, r={r['r']:.4f}, complexity={r['complexity']}\n")
            f.write(f"  {r['formula']}\n  LaTeX: {r['latex']}\n\n")

        f.write("\n## Task B: Age -> EN methylation score\n")
        for i, r in enumerate(res_b[:5]):
            f.write(f"Rank {i+1}: MSE={r['mse']:.6f}, r={r['r']:.4f}, complexity={r['complexity']}\n")
            f.write(f"  {r['formula']}\n  LaTeX: {r['latex']}\n\n")

    with open(config.RESULTS_DIR / "link_sr_results.json", "w", encoding="utf-8") as f:
        json.dump({"A": res_a[:5], "B": res_b[:5], "asm_mse": asm_mse}, f, indent=2)

    print(f"ASM reference MSE: {asm_mse:.6e}")
    if res_a:
        print(f"Task A best MSE: {res_a[0]['mse']:.6f}")
    if res_b:
        print(f"Task B best MSE: {res_b[0]['mse']:.6f}")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
