import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import warnings

# Adjust path to import the engine if not installed globally
sys.path.append('c:/Document/researches/eml-sr_biodata/eml-sr_model_second_AI')
import eml_sr_model_second_AI

warnings.filterwarnings('ignore')

def main():
    print("--- Running EML-SR with Elastic Net ---")
    df = pd.read_csv('filtered_data.csv', index_col=0)
    
    # We predict 'Age_trans' (log transformed age)
    target_cols = ['Age', 'Age_trans']
    feature_cols = [c for c in df.columns if c not in target_cols]
    
    X = df[feature_cols].values
    y = df['Age_trans'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Deep search configuration
    max_complexity = 10
    beam_width = 1000
    alpha = 0.01
    l1_ratio = 0.5
    
    print(f"Data: {X.shape[1]} features, {X.shape[0]} samples.")
    print(f"Settings: max_complexity={max_complexity}, beam_width={beam_width}, alpha={alpha}, l1_ratio={l1_ratio}")
    
    searcher = eml_sr_model_second_AI.Searcher(max_complexity=max_complexity, beam_width=beam_width)
    
    inputs_train = X_train.tolist()
    targets_train = y_train.tolist()
    
    print("Starting search...")
    # For second_AI, find_candidates takes 4 parameters: inputs, targets, alpha, l1_ratio
    candidates = searcher.find_candidates(inputs_train, targets_train, alpha, l1_ratio)
    print(f"Found {len(candidates)} candidates on the Pareto front.")
    
    local_vars = {f"v{i}": X_test[:, i] for i in range(X_test.shape[1])}
    
    results = []
    for cand in candidates:
        try:
            py_code = cand.to_python()
            py_code = py_code.replace("v_{", "v").replace("}", "")
            py_code = py_code.replace("p_{", "p")
            
            y_pred = eval(py_code, {"np": np}, local_vars)
            
            if np.isscalar(y_pred):
                y_pred = np.full(y_test.shape, y_pred)
                
            if np.isnan(y_pred).any() or np.isinf(y_pred).any():
                continue
                
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            results.append({
                'formula': cand.formula,
                'latex': cand.to_latex(),
                'complexity': cand.complexity,
                'error': cand.error, # Training error including penalty
                'r2': r2,
                'mae': mae
            })
        except Exception as e:
            pass
            
    # Sort by test R2
    results.sort(key=lambda x: x['r2'], reverse=True)
    
    out_file = 'second_AI_results.txt'
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(f"Results for Elastic Net EML-SR (Target: Age_trans)\n")
        f.write(f"Parameters: alpha={alpha}, l1_ratio={l1_ratio}\n")
        f.write("="*50 + "\n")
        for i, res in enumerate(results[:10]):  # Top 10
            f.write(f"Rank {i+1}:\n")
            f.write(f"  Complexity: {res['complexity']}\n")
            f.write(f"  Train Error(Penalized): {res['error']:.4f}\n")
            f.write(f"  Test R2: {res['r2']:.4f}\n")
            f.write(f"  Test MAE: {res['mae']:.4f}\n")
            f.write(f"  Formula: {res['formula']}\n")
            f.write(f"  LaTeX: {res['latex']}\n\n")
            
    print(f"Finished. Results saved to {out_file}")
    if len(results) > 0:
        print(f"Top R2: {results[0]['r2']:.4f}")

if __name__ == "__main__":
    main()
