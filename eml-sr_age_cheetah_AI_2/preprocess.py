import os
import re
import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNetCV
import matplotlib.pyplot as plt

def transform_age(age, asm=2.0):
    k = 0.2
    if pd.isna(age):
        return np.nan
    if age < asm:
        return np.log((age + k) / (asm + k))
    else:
        return (age - asm) / (asm + k)

def main():
    file_path = '../age_cheetah/GSE310779_series_matrix.txt'
    
    # Extract metadata (age)
    sample_ids = []
    ages = []
    
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('!Sample_geo_accession'):
                parts = line.strip().split('\t')
                sample_ids = [p.strip('"') for p in parts[1:]]
            elif line.startswith('!Sample_title'):
                parts = line.strip().split('\t')
                titles = [p.strip('"') for p in parts[1:]]
                for title in titles:
                    match = re.search(r'(\d+\.?\d*)y', title)
                    if match:
                        ages.append(float(match.group(1)))
                    else:
                        ages.append(np.nan)
            elif line.startswith('!series_matrix_table_begin'):
                break

    print(f"Loaded {len(sample_ids)} sample IDs and {len(ages)} ages.")
    
    # Prepare labels
    df_meta = pd.DataFrame({'Sample_ID': sample_ids, 'Age': ages})
    df_meta['Age_trans'] = df_meta['Age'].apply(transform_age)
    
    # Read matrix data
    print("Reading matrix data...")
    df_matrix = pd.read_csv(file_path, sep='\t', skiprows=61, index_col=0)
    # The last row might be !series_matrix_table_end
    if df_matrix.index[-1] == '!series_matrix_table_end':
        df_matrix = df_matrix.iloc[:-1]
    
    df_matrix = df_matrix.astype(float)
    
    # Transpose to (samples, features)
    X = df_matrix.T
    y = df_meta['Age_trans'].values
    
    # Drop samples with NaN age or missing data
    valid_idx = ~np.isnan(y)
    X = X[valid_idx]
    y = y[valid_idx]
    df_meta = df_meta[valid_idx]
    
    print(f"Shape of X: {X.shape}, shape of y: {y.shape}")
    
    # Impute remaining NaNs in X with mean if any
    X = X.fillna(X.mean())

    # Perform Elastic Net Feature Selection
    print("Running ElasticNetCV...")
    # alpha=0.5 corresponds to l1_ratio=0.5 in sklearn
    # In R glmnet, alpha=0.5 is exactly l1_ratio=0.5
    regr = ElasticNetCV(l1_ratio=0.5, cv=5, random_state=42, max_iter=10000, n_jobs=-1)
    regr.fit(X, y)
    
    coef = pd.Series(regr.coef_, index=X.columns)
    selected_features = coef[coef != 0]
    
    # Sort by absolute value and take top 50
    selected_features = selected_features.abs().sort_values(ascending=False).head(50)
    # Restore original signs if needed, but for importance we just use abs or we can map back
    selected_features = coef[selected_features.index]
    
    print(f"Optimal alpha: {regr.alpha_}")
    print(f"Selected {len(selected_features)} top features.")
    
    # Save selected features
    selected_features.to_csv('selected_features.csv')
    
    # Save filtered data for EML later
    df_filtered = X[selected_features.index]
    df_filtered['Age'] = df_meta['Age'].values
    df_filtered['Age_trans'] = y
    df_filtered.to_csv('filtered_data.csv')
    
    # Plot feature importance
    plt.figure(figsize=(10, 8))
    selected_features_sorted = selected_features.abs().sort_values(ascending=True)
    selected_features_sorted.plot(kind='barh')
    plt.title('Elastic Net Feature Importance (Absolute Coefficients)')
    plt.xlabel('Absolute Coefficient Value')
    plt.ylabel('CpG Site')
    plt.tight_layout()
    plt.savefig('feature_importance.png')
    plt.close()
    
    print("Preprocessing and feature selection complete. Saved to selected_features.csv, filtered_data.csv, feature_importance.png")

if __name__ == "__main__":
    main()
