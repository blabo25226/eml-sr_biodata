#!/usr/bin/env python3
"""
lacroix_grammar_search_ode.py

Improved restricted EML-grammar search for LaCroix et al. Fig. 2F.

Why this version exists
-----------------------
The first static grammar search fits

    y_D(t) = 1 + B E(R_D(t))

directly. That can create an artificial early dip because the expression is
forced to map the recruitment variable instantaneously to activity. The LaCroix
time courses are kinetic traces, so the reduced expression should normally be
used as a target of a first-order relaxation equation:

    tau dy_D/dt = -y_D + [1 + B E(R_D(t))].

This script therefore fits the same restricted EML grammar, but embeds it in
a first-order filter. It also includes the linker model and a Hill relaxation
model as comparators.

Grammar
-------
    E ::= R | G(E) | E + E

where

    R_D(t;k) = D * (1 - exp(-k t))

and

    G_{a,b,c}(x) = eml(a ln(c+x), exp(bx)) - c^a
                 = (c+x)^a - b x - c^a.

Response model
--------------
    target_D(t) = 1 + B E(R_D(t;k))
    tau dy_D/dt = -y_D + target_D(t),    y_D(0)=1

By default the script enforces a soft monotonicity penalty on the 2 nM
prediction to discourage the unphysical early dip seen in static fits.

Example
-------
python lacroix_grammar_search_ode.py \
  --input LaCroix-elife-66869-fig2-data.csv \
  --out-prefix lacroix_grammar_ode \
  --search-mode exhaustive \
  --max-depth 3 \
  --max-nodes 5 \
  --plot-format pdf
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import least_squares


DOSES = np.array([2.0, 20.0], dtype=float)


@dataclass
class LacroixData:
    time: np.ndarray
    y2: np.ndarray
    sem2: np.ndarray
    y20: np.ndarray
    sem20: np.ndarray


@dataclass(frozen=True)
class Expr:
    kind: str
    child: Optional["Expr"] = None
    left: Optional["Expr"] = None
    right: Optional["Expr"] = None

    @staticmethod
    def R():
        return Expr("R")

    @staticmethod
    def G(x):
        return Expr("G", child=x)

    @staticmethod
    def Add(a, b):
        return Expr("Add", left=a, right=b) if a.canonical() <= b.canonical() else Expr("Add", left=b, right=a)

    def depth(self):
        if self.kind == "R":
            return 0
        if self.kind == "G":
            return 1 + self.child.depth()
        if self.kind == "Add":
            return max(self.left.depth(), self.right.depth())
        raise ValueError(self.kind)

    def nodes(self):
        if self.kind == "R":
            return 1
        if self.kind == "G":
            return 1 + self.child.nodes()
        if self.kind == "Add":
            return 1 + self.left.nodes() + self.right.nodes()
        raise ValueError(self.kind)

    def gates(self):
        if self.kind == "R":
            return 0
        if self.kind == "G":
            return 1 + self.child.gates()
        if self.kind == "Add":
            return self.left.gates() + self.right.gates()
        raise ValueError(self.kind)

    def canonical(self):
        if self.kind == "R":
            return "R"
        if self.kind == "G":
            return f"G({self.child.canonical()})"
        if self.kind == "Add":
            return f"({self.left.canonical()}+{self.right.canonical()})"
        raise ValueError(self.kind)

    def evaluate(self, R, pars):
        if self.kind == "R":
            return R
        if self.kind == "G":
            a, b, c = pars[:3]
            child_pars = pars[3:3 + 3*self.child.gates()]
            return gate(self.child.evaluate(R, child_pars), a, b, c)
        if self.kind == "Add":
            nleft = 3*self.left.gates()
            return self.left.evaluate(R, pars[:nleft]) + self.right.evaluate(R, pars[nleft:])
        raise ValueError(self.kind)


@dataclass
class FitResult:
    model: str
    expr: str
    depth: int
    nodes: int
    gates: int
    params: np.ndarray
    param_names: list[str]
    pred2: np.ndarray
    pred20: np.ndarray
    train_chi2: float
    valid_chi2: float
    all_chi2: float
    train_wmse: float
    valid_wmse: float
    AIC_train: float
    BIC_train: float
    score: float
    n_parameters: int


def read_lacroix_csv(path: Path, ignore_negative_times=True):
    raw = pd.read_csv(path)
    if str(raw.iloc[0, 0]).strip().lower() in {"time (min)", "time"}:
        rows = raw.iloc[1:].copy()
        out = pd.DataFrame({
            "time": pd.to_numeric(rows.iloc[:, 0], errors="coerce"),
            "y2": pd.to_numeric(rows.iloc[:, 1], errors="coerce"),
            "sem2": pd.to_numeric(rows.iloc[:, 2], errors="coerce"),
            "y20": pd.to_numeric(rows.iloc[:, 4], errors="coerce"),
            "sem20": pd.to_numeric(rows.iloc[:, 5], errors="coerce"),
        })
    else:
        out = pd.DataFrame({
            "time": pd.to_numeric(raw.iloc[:, 0], errors="coerce"),
            "y2": pd.to_numeric(raw.iloc[:, 1], errors="coerce"),
            "sem2": pd.to_numeric(raw.iloc[:, 2], errors="coerce"),
            "y20": pd.to_numeric(raw.iloc[:, 4], errors="coerce"),
            "sem20": pd.to_numeric(raw.iloc[:, 5], errors="coerce"),
        })
    out = out.dropna(subset=["time", "y2", "y20"]).reset_index(drop=True)
    if ignore_negative_times:
        out = out[out["time"] >= 0].reset_index(drop=True)
    return LacroixData(
        out["time"].to_numpy(float),
        out["y2"].to_numpy(float),
        out["sem2"].to_numpy(float),
        out["y20"].to_numpy(float),
        out["sem20"].to_numpy(float),
    )


def split_points(n, mode):
    idx = np.arange(n)
    if mode == "late":
        train = idx < int(0.75*n)
        valid = ~train
    else:
        valid = idx % 4 == 1
        train = ~valid
        train[0] = True
        valid[0] = False
    return train, valid


def weights(data):
    sem = np.concatenate([data.sem2, data.sem20])
    pos = sem[(sem > 0) & np.isfinite(sem)]
    floor = np.median(pos)*0.25 if len(pos) else 1.0
    return np.maximum(sem, floor)


def R_dt(t, D, k):
    return D * (1.0 - np.exp(-k*t))


def gate(x, a, b, c):
    xp = np.maximum(c + x, 1e-9)
    return xp**a - b*x - c**a


def first_order_filter(t, target, tau, y0=1.0):
    y = np.empty_like(t)
    y[0] = y0
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        decay = np.exp(-dt/tau)
        mid = 0.5*(target[i-1]+target[i])
        y[i] = mid + (y[i-1]-mid)*decay
    return y


def generate_exprs(max_depth, max_nodes):
    exprs = {"R": Expr.R()}
    changed = True
    while changed:
        changed = False
        cur = list(exprs.values())
        for e in cur:
            g = Expr.G(e)
            if g.depth() <= max_depth and g.nodes() <= max_nodes and g.canonical() not in exprs:
                exprs[g.canonical()] = g
                changed = True
        cur = list(exprs.values())
        for i, a in enumerate(cur):
            for b in cur[i:]:
                s = Expr.Add(a, b)
                if s.depth() <= max_depth and s.nodes() <= max_nodes and s.canonical() not in exprs:
                    exprs[s.canonical()] = s
                    changed = True
    return sorted(exprs.values(), key=lambda e: (e.depth(), e.nodes(), e.canonical()))


def flatten(data):
    return np.concatenate([data.y2, data.y20])


def predict_expr_ode(expr, p, t):
    # p = [B, k, tau, gate params...]
    B, k, tau = p[:3]
    pars = p[3:]
    pred = []
    for D in DOSES:
        R = R_dt(t, D, k)
        target = 1.0 + B * expr.evaluate(R, pars)
        pred.append(first_order_filter(t, target, tau, y0=1.0))
    return np.concatenate(pred)


def predict_hill_ode(p, t):
    # p = [A, Kd, h, k, tau]
    A, Kd, h, k, tau = p
    pred = []
    for D in DOSES:
        R = R_dt(t, D, k)
        H = R**h/(Kd**h + R**h + 1e-12)
        target = 1.0 + A*H
        pred.append(first_order_filter(t, target, tau, y0=1.0))
    return np.concatenate(pred)


def phi_linker(S, N=4):
    S = np.asarray(S)
    denom = S**N
    for n in range(1, N+1):
        denom = denom + n*S**(N-n)
    return S/denom


def predict_linker(p, t, N=4):
    # p = [A, S0, q, k, tau]
    A, S0, q, k, tau = p
    phi0 = phi_linker(S0, N)
    pred = []
    for D in DOSES:
        S = S0 + q*D*(1-np.exp(-k*t))
        target = 1.0 + A*(phi_linker(S,N)-phi0)
        pred.append(first_order_filter(t, target, tau, y0=1.0))
    return np.concatenate(pred)


def fit_model(data, model, expr_label, depth, nodes, gates, predict, starts, lo, hi, train, valid,
              depth_penalty, node_penalty, max_nfev, monotone_2nm_penalty):
    t = data.time
    y = flatten(data)
    w = weights(data)
    train2 = np.concatenate([train, train])
    valid2 = np.concatenate([valid, valid])
    best = None
    for s in starts:
        s = np.minimum(np.maximum(np.asarray(s, float), lo+1e-10), hi-1e-10)
        def res(p):
            pred = predict(p, t)
            base = (pred[train2]-y[train2])/w[train2]
            if monotone_2nm_penalty > 0 and model == "EML_expr":
                n = len(t)
                pred2 = pred[:n]
                # Penalize downward steps after t=0 for 2 nM.
                neg_steps = np.minimum(np.diff(pred2), 0.0)
                penalty = monotone_2nm_penalty * neg_steps
                return np.concatenate([base, penalty])
            return base
        try:
            fit = least_squares(res, s, bounds=(lo,hi), max_nfev=max_nfev,
                                ftol=1e-9, xtol=1e-9, gtol=1e-9)
        except Exception:
            continue
        chi = float(np.sum(res(fit.x)**2))
        if best is None or chi < best[0]:
            best = (chi, fit)
    if best is None:
        raise RuntimeError(f"Fit failed for {model} {expr_label}")

    train_chi2, fit = best
    pred = predict(fit.x, t)
    all_res = (pred-y)/w
    valid_chi2 = float(np.sum(all_res[valid2]**2))
    all_chi2 = float(np.sum(all_res**2))
    ntrain = int(np.sum(train2)); nvalid = int(np.sum(valid2)); kpar = len(fit.x)
    train_wmse = train_chi2/ntrain
    valid_wmse = valid_chi2/nvalid
    AIC = ntrain*np.log(max(train_chi2,1e-12)/ntrain) + 2*kpar
    BIC = ntrain*np.log(max(train_chi2,1e-12)/ntrain) + kpar*np.log(ntrain)
    score = valid_wmse + depth_penalty*depth + node_penalty*nodes

    if model == "hill":
        names = ["A","K","h","k","tau"]
    elif model.startswith("linker"):
        names = ["A","S0","q","k","tau"]
    else:
        names = ["B","k","tau"]
        for j in range(gates):
            names += [f"a{j+1}", f"b{j+1}", f"c{j+1}"]

    n = len(t)
    return FitResult(model, expr_label, depth, nodes, gates, fit.x, names,
                     pred[:n], pred[n:], train_chi2, valid_chi2, all_chi2,
                     train_wmse, valid_wmse, AIC, BIC, score, kpar)


def expr_start_bounds(expr):
    g = expr.gates()
    lo = [-10.0, 0.001, 0.05]  # B,k,tau
    hi = [10.0, 5.0, 300.0]
    for _ in range(g):
        lo += [0.02, 1e-5, 0.0]
        hi += [30.0, 100.0, 100.0]
    starts = []
    for B, tau in [(0.04, 12.0), (0.08, 20.0), (-0.04, 12.0)]:
        p = [B, 0.3, tau]
        for j in range(g):
            c0 = 1e-6 if j == g-1 else 0.1
            p += [0.55, 1.0 if j == g-1 else 0.5, c0]
        starts.append(np.asarray(p, float))
    return starts, np.asarray(lo,float), np.asarray(hi,float)


def fit_expr(data, expr, train, valid, depth_penalty, node_penalty, max_nfev, monotone_2nm_penalty):
    starts, lo, hi = expr_start_bounds(expr)
    return fit_model(data, "EML_expr", expr.canonical(), expr.depth(), expr.nodes(), expr.gates(),
                     lambda p,t: predict_expr_ode(expr,p,t), starts, lo, hi, train, valid,
                     depth_penalty, node_penalty, max_nfev, monotone_2nm_penalty)


def fit_baselines(data, train, valid, depth_penalty, node_penalty, max_nfev):
    fits = []
    fits.append(fit_model(
        data, "hill", "Hill ODE", 0, 1, 0, predict_hill_ode,
        [np.array([0.03,0.5,1.0,0.3,10.0]), np.array([0.05,2.0,3.0,0.3,20.0])],
        np.array([-1.0,1e-4,0.02,0.001,0.05]), np.array([1.0,100.0,30.0,5.0,300.0]),
        train, valid, depth_penalty, node_penalty, max_nfev, 0.0
    ))
    for N in [2,4]:
        fits.append(fit_model(
            data, f"linker_N{N}", f"Phi_N{N}", 0, 1, 0,
            lambda p,t,N=N: predict_linker(p,t,N=N),
            [np.array([10000,0.8,0.001,0.5,20]), np.array([100,0.5,0.01,0.3,10])],
            np.array([0.0,1e-5,1e-8,0.001,0.05]), np.array([1e6,100.0,100.0,5.0,300.0]),
            train, valid, depth_penalty, node_penalty, max_nfev, 0.0
        ))
    return fits


def results_df(fits):
    rows=[]
    for f in fits:
        rows.append({
            "model": f.model, "expr": f.expr, "depth": f.depth, "nodes": f.nodes, "gates": f.gates,
            "n_parameters": f.n_parameters,
            "parameters": "; ".join(f"{n}={v:.8g}" for n,v in zip(f.param_names, f.params)),
            "train_chi2": f.train_chi2, "valid_chi2": f.valid_chi2, "all_chi2": f.all_chi2,
            "train_wmse": f.train_wmse, "valid_wmse": f.valid_wmse,
            "AIC_train": f.AIC_train, "BIC_train": f.BIC_train, "score": f.score,
        })
    df = pd.DataFrame(rows)
    df["DeltaScore_from_best"] = df["score"] - df["score"].min()
    df["DeltaAIC_from_best"] = df["AIC_train"] - df["AIC_train"].min()
    return df.sort_values("score")


def save_predictions(data, fits, out):
    rows=[]
    for f in fits:
        for D,y,sem,pred in [(2.0,data.y2,data.sem2,f.pred2),(20.0,data.y20,data.sem20,f.pred20)]:
            for t,obs,se,pr in zip(data.time,y,sem,pred):
                rows.append({"model":f.model,"expr":f.expr,"dose_nM":D,"time_min":t,
                             "mean":obs,"sem":se,"prediction":pr})
    pd.DataFrame(rows).to_csv(out,index=False)


def plot_best(data, fits, out, svg_out):
    df = results_df(fits)
    best_row = df.iloc[0]
    best = next(f for f in fits if f.model == best_row.model and f.expr == best_row.expr)
    hill = next(f for f in fits if f.model == "hill")
    linker = next(f for f in fits if f.model == "linker_N4")
    best_eml = min([f for f in fits if f.model == "EML_expr"], key=lambda f: f.score)

    _FS     = 9     # axis labels / tick labels (~10 pt PRE body at 7-inch figure width)
    _FS_LEG = 7.5   # legend entries
    _FS_PNL = 11    # panel labels (a)(b), slightly larger than body text
    _LW_REF = 0.6   # y = 0 reference line width

    with plt.rc_context({'text.usetex': True, 'font.family': 'serif',
                         'font.size': _FS, 'axes.labelsize': _FS,
                         'xtick.labelsize': _FS, 'ytick.labelsize': _FS}):
        fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.2), sharey=True)
        for ax, D, y, sem, lbl in [
            (axes[0],  2.0, data.y2,  data.sem2,  '(a)'),
            (axes[1], 20.0, data.y20, data.sem20, '(b)'),
        ]:
            ax.errorbar(data.time, y, yerr=sem, fmt='o', markersize=2.5, capsize=1.5,
                        label=r'Mean $\pm$ SEM')
            ax.plot(data.time, hill.pred2   if D == 2 else hill.pred20,
                    '--', label='Hill ODE')
            ax.plot(data.time, best_eml.pred2 if D == 2 else best_eml.pred20,
                    '-', linewidth=2.0, label=f'EML ODE: {best_eml.expr}')
            ax.plot(data.time, linker.pred2 if D == 2 else linker.pred20,
                    ':', linewidth=2.2, label='Linker $N=4$')
            ax.set_title(f'{D:g} nM rapamycin', fontsize=_FS)
            ax.set_xlabel('Time after rapamycin (min)')
            ax.axhline(0, color='k', linewidth=_LW_REF, zorder=0)
            # Panel label outside the plot area, top-left corner.
            ax.text(0.0, 1.04, lbl, transform=ax.transAxes,
                    fontsize=_FS_PNL, va='bottom', ha='left', clip_on=False)
        axes[0].set_ylabel('Normalized PKA activity')
        axes[1].legend(frameon=False, fontsize=_FS_LEG)
        # Set y limits from the data + prediction range, rounded to a clean step.
        # This overrides the downward expansion caused by axhline(0).
        all_y = np.concatenate([
            data.y2  - data.sem2,  data.y2  + data.sem2,
            data.y20 - data.sem20, data.y20 + data.sem20,
            hill.pred2, hill.pred20,
            linker.pred2, linker.pred20,
            best_eml.pred2, best_eml.pred20,
        ])
        pad  = 0.10 * (all_y.max() - all_y.min())
        step = 0.02
        ylo = np.floor((all_y.min() - pad) / step) * step
        yhi = np.ceil( (all_y.max() + pad) / step) * step
        axes[0].set_ylim(ylo, yhi)   # sharey=True propagates to axes[1]
        fig.tight_layout(pad=0.8)
        fig.savefig(out,     bbox_inches='tight')
        fig.savefig(svg_out, bbox_inches='tight')
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("LaCroix-elife-66869-fig2-data.csv"))
    ap.add_argument("--out-prefix", type=Path, default=Path("lacroix_grammar_ode"))
    ap.add_argument("--include-negative-times", action="store_true")
    ap.add_argument("--search-mode", choices=["exhaustive","beam"], default="exhaustive")
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--max-nodes", type=int, default=5)
    ap.add_argument("--beam-width", type=int, default=8)
    ap.add_argument("--split", choices=["alternating","late"], default="alternating")
    ap.add_argument("--depth-penalty", type=float, default=0.0)
    ap.add_argument("--node-penalty", type=float, default=0.0)
    ap.add_argument("--monotone-2nm-penalty", type=float, default=500.0)
    ap.add_argument("--max-nfev", type=int, default=800)
    ap.add_argument("--plot-format", choices=["png","pdf"], default="png")
    args = ap.parse_args()

    data = read_lacroix_csv(args.input, ignore_negative_times=not args.include_negative_times)
    train, valid = split_points(len(data.time), args.split)
    exprs = generate_exprs(args.max_depth,args.max_nodes)
    if args.search_mode == "beam":
        exprs = sorted(exprs, key=lambda e:(e.depth(),e.nodes(),e.canonical()))[:args.beam_width*(args.max_depth+1)]
    print(f"Fitting {len(exprs)} EML ODE expressions plus Hill/linker baselines")

    fits = fit_baselines(data, train, valid, args.depth_penalty, args.node_penalty, args.max_nfev)
    for e in exprs:
        print(f"  fitting {e.canonical()}")
        fits.append(fit_expr(data, e, train, valid, args.depth_penalty, args.node_penalty,
                             args.max_nfev, args.monotone_2nm_penalty))

    args.out_prefix.parent.mkdir(parents=True,exist_ok=True)
    summary_path = args.out_prefix.with_name(args.out_prefix.name + "_summary.csv")
    pred_path = args.out_prefix.with_name(args.out_prefix.name + "_predictions.csv")
    plot_path = args.out_prefix.with_name(args.out_prefix.name + f"_best_models.{args.plot_format}")
    svg_path  = args.out_prefix.with_name(args.out_prefix.name + "_best_models.svg")

    df = results_df(fits)
    df.to_csv(summary_path, index=False)
    save_predictions(data, fits, pred_path)
    plot_best(data, fits, plot_path, svg_path)

    print("\nBest models:")
    print(df.head(12)[["model","expr","depth","nodes","gates","n_parameters","valid_wmse","AIC_train","score"]].to_string(index=False))
    print(f"\nSaved summary:     {summary_path}")
    print(f"Saved predictions: {pred_path}")
    print(f"Saved plot:        {plot_path}")
    print(f"Saved SVG:         {svg_path}")

    # --- Fit parameters for caption ---
    hill_f = next(f for f in fits if f.model == "hill")
    print("\n=== Hill ODE fit (for caption) ===")
    for n, v in zip(hill_f.param_names, hill_f.params):
        print(f"  {n} = {v:.4g}")
    print(f"  train wMSE = {hill_f.train_wmse:.4g},  valid wMSE = {hill_f.valid_wmse:.4g}")

    for N in [2, 4]:
        lnk = next(f for f in fits if f.model == f"linker_N{N}")
        print(f"\n=== Linker N={N} fit (for caption) ===")
        for n, v in zip(lnk.param_names, lnk.params):
            print(f"  {n} = {v:.4g}")
        print(f"  train wMSE = {lnk.train_wmse:.4g},  valid wMSE = {lnk.valid_wmse:.4g}")

    best_eml = min([f for f in fits if f.model == "EML_expr"], key=lambda f: f.score)
    print(f"\n=== Best EML ODE fit (for caption) ===")
    print(f"  expr = {best_eml.expr},  depth={best_eml.depth}, nodes={best_eml.nodes}, gates={best_eml.gates}")
    for n, v in zip(best_eml.param_names, best_eml.params):
        print(f"  {n} = {v:.4g}")
    print(f"  train wMSE = {best_eml.train_wmse:.4g},  valid wMSE = {best_eml.valid_wmse:.4g}")


if __name__ == "__main__":
    main()
