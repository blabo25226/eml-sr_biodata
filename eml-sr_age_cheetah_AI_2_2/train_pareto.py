import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import eml_sr_model_first_AI as eml_sr
import warnings

# Suppress warnings from evaluating invalid formulas on test set (e.g. sqrt of negative)
warnings.filterwarnings('ignore')

def train_and_get_pareto(filename):
    print(f"\n--- Processing {filename} ---")
    df = pd.read_csv(filename, index_col=0)
    
    feature_cols = [c for c in df.columns if c != 'Age']
    X = df[feature_cols].values
    y = df['Age'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # We use beam_width=500 and max_complexity=8 to balance search quality and time
    searcher = eml_sr.Searcher(max_complexity=8, beam_width=500)
    
    inputs_train = X_train.tolist()
    targets_train = y_train.tolist()
    
    print("Starting search...")
    candidates = searcher.find_candidates(inputs_train, targets_train)
    print(f"Found {len(candidates)} candidates on the Pareto front.")
    
    local_vars = {f"v{i}": X_test[:, i] for i in range(X_test.shape[1])}
    
    results = []
    for cand in candidates:
        try:
            py_code = cand.to_python()
            # Fix variable syntax for python eval (e.g. v_{0} -> v0)
            py_code = py_code.replace("v_{", "v").replace("}", "")
            py_code = py_code.replace("p_{", "p")
            
            y_pred = eval(py_code, {"np": np}, local_vars)
            
            if np.isscalar(y_pred):
                y_pred = np.full(y_test.shape, y_pred)
                
            # Filter out NaNs and Infs resulting from bad eval (like log of negative)
            if np.isnan(y_pred).any() or np.isinf(y_pred).any():
                continue
                
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            results.append({
                'formula': cand.formula,
                'latex': cand.to_latex(),
                'complexity': cand.complexity,
                'error': cand.error,
                'r2': r2,
                'mae': mae
            })
        except Exception as e:
            pass
            
    # Sort by R2 descending
    results.sort(key=lambda x: x['r2'], reverse=True)
    
    top_5 = results[:5]
    out_file = filename.replace('.csv', '_results.txt')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(f"Results for {filename} (Top 5 by Test R2)\n")
        f.write("="*50 + "\n")
        for i, res in enumerate(top_5):
            f.write(f"Rank {i+1}:\n")
            f.write(f"  Complexity: {res['complexity']}\n")
            f.write(f"  Train Error: {res['error']:.4f}\n")
            f.write(f"  Test R2: {res['r2']:.4f}\n")
            f.write(f"  Test MAE: {res['mae']:.4f}\n")
            f.write(f"  Formula: {res['formula']}\n")
            f.write(f"  LaTeX: {res['latex']}\n\n")
            
    print(f"Finished {filename}. Top 5 R2:")
    for i, res in enumerate(top_5):
        print(f"  Rank {i+1}: R2 = {res['r2']:.4f}, Complexity = {res['complexity']}")

def main():
    files = ['data_raw.csv', 'data_pca.csv', 'data_wgcna.csv']
    for f in files:
        train_and_get_pareto(f)

if __name__ == "__main__":
    main()
