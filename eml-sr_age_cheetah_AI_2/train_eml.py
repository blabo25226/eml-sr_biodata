import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import eml_sr_model_first_AI as eml_sr

def main():
    print("Loading data...")
    df = pd.read_csv('filtered_data.csv', index_col=0)
    
    # Target is Age_trans
    y = df['Age_trans'].values
    
    # Use top 4 features as requested
    feature_cols = ['cg10501210', 'cg12544505.2', 'cg23090567', 'cg10505126']
    X = df[feature_cols].values
    
    # Split data (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Train size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")
    
    results = {}
    predictions = {}
    
    # --- 1. Baseline: Linear Elastic Net ---
    print("Training Baseline: Elastic Net...")
    enet = ElasticNet(alpha=0.01, l1_ratio=0.5, random_state=42)
    enet.fit(X_train, y_train)
    y_pred_enet = enet.predict(X_test)
    
    mae_enet = mean_absolute_error(y_test, y_pred_enet)
    r2_enet = r2_score(y_test, y_pred_enet)
    results['ElasticNet'] = {'MAE': mae_enet, 'R2': r2_enet}
    predictions['ElasticNet'] = y_pred_enet
    
    # --- 2. Baseline: Random Forest ---
    print("Training Baseline: Random Forest...")
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    
    mae_rf = mean_absolute_error(y_test, y_pred_rf)
    r2_rf = r2_score(y_test, y_pred_rf)
    results['RandomForest'] = {'MAE': mae_rf, 'R2': r2_rf}
    predictions['RandomForest'] = y_pred_rf
    
    # --- 3. EML Symbolic Regression ---
    print("Training EML Symbolic Regression...")
    # EML requires inputs as lists of lists
    inputs_train = X_train.tolist()
    targets_train = y_train.tolist()
    inputs_test = X_test.tolist()
    
    # Use new model-first AI engine, increased beam width for better search
    searcher = eml_sr.Searcher(max_complexity=10, beam_width=500)
    # Fit the searcher
    eml_model = searcher.fit(inputs_train, targets_train)
    
    print("\n[EML Results]")
    print(f"Formula: {eml_model.formula}")
    print(f"Complexity: {eml_model.complexity}")
    
    y_pred_eml = eml_model.predict(inputs_test)
    mae_eml = mean_absolute_error(y_test, y_pred_eml)
    r2_eml = r2_score(y_test, y_pred_eml)
    
    results['EML_SR'] = {'MAE': mae_eml, 'R2': r2_eml}
    predictions['EML_SR'] = y_pred_eml
    
    # --- Save Model info ---
    with open('eml_model_results.txt', 'w') as f:
        f.write(f"Formula: {eml_model.formula}\n")
        f.write(f"Python: {eml_model.to_python()}\n")
        f.write(f"LaTeX: {eml_model.to_latex()}\n")
        f.write(f"Complexity: {eml_model.complexity}\n")
        f.write("\nFeatures mapping (v0, v1...):\n")
        for i, col in enumerate(feature_cols):
            f.write(f"v{i}: {col}\n")

    # --- Plotting ---
    print("\nModel Comparison on Test Set:")
    for model_name, metrics in results.items():
        print(f"{model_name:15} -> MAE: {metrics['MAE']:.4f}, R2: {metrics['R2']:.4f}")
        
    plt.figure(figsize=(15, 5))
    
    for i, (name, y_pred) in enumerate(predictions.items()):
        plt.subplot(1, 3, i+1)
        plt.scatter(y_test, y_pred, alpha=0.7)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
        plt.title(f"{name}\nMAE={results[name]['MAE']:.3f}, R2={results[name]['R2']:.3f}")
        plt.xlabel("True Age_trans")
        plt.ylabel("Predicted Age_trans")
    
    plt.tight_layout()
    plt.savefig('model_comparison.png')
    plt.close()
    
    print("Training complete. Results saved to model_comparison.png and eml_model_results.txt")

if __name__ == "__main__":
    main()
