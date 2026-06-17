#!/usr/bin/env python3
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional
from scipy.optimize import least_squares
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

@dataclass(frozen=True)
class Expr:
    kind: str
    child: Optional["Expr"] = None
    left: Optional["Expr"] = None
    right: Optional["Expr"] = None
    var_idx: int = -1

    @staticmethod
    def V(idx: int) -> "Expr":
        return Expr("V", var_idx=idx)

    @staticmethod
    def G(x: "Expr") -> "Expr":
        return Expr("G", child=x)

    @staticmethod
    def Add(a: "Expr", b: "Expr") -> "Expr":
        return Expr("Add", left=a, right=b) if a.canonical() <= b.canonical() else Expr("Add", left=b, right=a)

    def depth(self) -> int:
        if self.kind == "V": return 0
        if self.kind == "G": return 1 + self.child.depth()
        if self.kind == "Add": return max(self.left.depth(), self.right.depth())
        raise ValueError(self.kind)

    def nodes(self) -> int:
        if self.kind == "V": return 1
        if self.kind == "G": return 1 + self.child.nodes()
        if self.kind == "Add": return 1 + self.left.nodes() + self.right.nodes()
        raise ValueError(self.kind)

    def gates(self) -> int:
        if self.kind == "V": return 0
        if self.kind == "G": return 1 + self.child.gates()
        if self.kind == "Add": return self.left.gates() + self.right.gates()
        raise ValueError(self.kind)

    def canonical(self) -> str:
        if self.kind == "V": return f"V{self.var_idx}"
        if self.kind == "G": return f"G({self.child.canonical()})"
        if self.kind == "Add": return f"({self.left.canonical()}+{self.right.canonical()})"
        raise ValueError(self.kind)

    def evaluate(self, X: np.ndarray, pars: np.ndarray) -> np.ndarray:
        if self.kind == "V": return X[:, self.var_idx]
        if self.kind == "G":
            a, b, c = pars[:3]
            child_pars = pars[3:3 + 3 * self.child.gates()]
            return gate(self.child.evaluate(X, child_pars), a, b, c)
        if self.kind == "Add":
            nleft = 3 * self.left.gates()
            return self.left.evaluate(X, pars[:nleft]) + self.right.evaluate(X, pars[nleft:])
        raise ValueError(self.kind)

def gate(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    xp = np.maximum(c + x, 1e-9)
    return xp**a - b * x - c**a

def generate_expressions(max_depth: int, max_nodes: int, num_vars: int) -> list[Expr]:
    exprs = {}
    for i in range(num_vars):
        v = Expr.V(i)
        exprs[v.canonical()] = v

    changed = True
    while changed:
        changed = False
        current_exprs = list(exprs.values())
        for e in current_exprs:
            if e.depth() < max_depth and e.nodes() < max_nodes:
                # Apply G
                ne = Expr.G(e)
                if ne.nodes() <= max_nodes and ne.canonical() not in exprs:
                    exprs[ne.canonical()] = ne
                    changed = True
        
        # Apply Add
        current_exprs = list(exprs.values())
        for e1 in current_exprs:
            for e2 in current_exprs:
                if e1.depth() < max_depth and e2.depth() < max_depth:
                    ne = Expr.Add(e1, e2)
                    if ne.depth() <= max_depth and ne.nodes() <= max_nodes and ne.canonical() not in exprs:
                        exprs[ne.canonical()] = ne
                        changed = True
    return list(exprs.values())

def fit_expr(expr: Expr, X: np.ndarray, y: np.ndarray) -> dict:
    def residuals(pars: np.ndarray) -> np.ndarray:
        y0, B = pars[0], pars[1]
        gate_pars = pars[2:]
        y_pred = y0 + B * expr.evaluate(X, gate_pars)
        return y_pred - y

    n_gates = expr.gates()
    init_pars = np.zeros(2 + 3 * n_gates)
    init_pars[1] = 1.0 # B
    if n_gates > 0:
        for i in range(n_gates):
            init_pars[2 + 3*i] = 1.0 # a
            init_pars[2 + 3*i + 1] = 1.0 # b
            init_pars[2 + 3*i + 2] = 1.0 # c

    res = least_squares(residuals, init_pars, method='lm', max_nfev=2000)
    mse = np.mean(res.fun**2)
    
    n_params = len(init_pars)
    n_samples = len(y)
    aic = n_samples * np.log(mse + 1e-15) + 2 * n_params
    bic = n_samples * np.log(mse + 1e-15) + np.log(n_samples) * n_params
    
    return {
        'mse': mse,
        'aic': aic,
        'bic': bic,
        'pars': res.x,
        'success': res.success
    }

def main():
    print("Loading data for MEb static regression...")
    df = pd.read_csv('filtered_data.csv', index_col=0)
    y = df['Age_trans'].values
    
    # Use top 3 CpGs from Elastic Net
    top_cpgs = ['cg10501210', 'cg12544505.2', 'cg23090567']
    X = df[top_cpgs].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")
    
    print("Generating AST expressions...")
    exprs = generate_expressions(max_depth=3, max_nodes=5, num_vars=3)
    print(f"Generated {len(exprs)} expressions.")
    
    best_aic = float('inf')
    best_result = None
    best_expr = None
    
    for i, expr in enumerate(exprs):
        try:
            res = fit_expr(expr, X_train, y_train)
            if res['success'] and res['aic'] < best_aic:
                best_aic = res['aic']
                best_result = res
                best_expr = expr
        except Exception:
            pass
            
    print(f"\nBest Model Canonical: {best_expr.canonical()}")
    print(f"Train MSE: {best_result['mse']:.4f}")
    
    # Evaluate on test
    y0, B = best_result['pars'][0], best_result['pars'][1]
    gate_pars = best_result['pars'][2:]
    
    y_pred_test = y0 + B * best_expr.evaluate(X_test, gate_pars)
    mae_test = mean_absolute_error(y_test, y_pred_test)
    r2_test = r2_score(y_test, y_pred_test)
    
    print(f"Test MAE: {mae_test:.4f}")
    print(f"Test R2: {r2_test:.4f}")
    
    # Save results
    with open('MEb_model_results.txt', 'w') as f:
        f.write(f"MEb Modified Approach\n")
        f.write(f"Canonical Formula: {best_expr.canonical()}\n")
        f.write(f"Parameters (y0, B, gate_a, gate_b, gate_c...): {best_result['pars']}\n")
        f.write(f"Train MSE: {best_result['mse']:.4f}\n")
        f.write(f"Train AIC: {best_result['aic']:.4f}\n")
        f.write(f"Test MAE: {mae_test:.4f}\n")
        f.write(f"Test R2: {r2_test:.4f}\n")
        f.write(f"\nVariables mapped:\n")
        for i, cpg in enumerate(top_cpgs):
            f.write(f"V{i}: {cpg}\n")

if __name__ == "__main__":
    main()
