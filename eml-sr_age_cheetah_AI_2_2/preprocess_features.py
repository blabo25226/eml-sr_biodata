import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler

def main():
    print("Loading raw data...")
    df = pd.read_csv('filtered_data.csv', index_col=0)
    
    # Extract target and features
    target_cols = ['Age', 'Age_trans']
    feature_cols = [c for c in df.columns if c not in target_cols]
    
    X = df[feature_cols].values
    
    # 1. RAW Data
    print("Saving Raw data...")
    df_raw = pd.DataFrame(X, columns=feature_cols, index=df.index)
    df_raw['Age'] = df['Age']
    df_raw.to_csv('data_raw.csv')
    
    # Standardize features for PCA and Clustering (to ensure equal weight)
    # The user asked not to log-transform, but standard scaling is usually 
    # necessary for PCA/Clustering. I will NOT log-transform, just standard scale.
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 2. PCA Data
    print("Performing PCA...")
    n_components = 5  # Keep top 5 PCs
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X_scaled)
    pca_cols = [f'PC{i+1}' for i in range(n_components)]
    df_pca = pd.DataFrame(X_pca, columns=pca_cols, index=df.index)
    df_pca['Age'] = df['Age']
    df_pca.to_csv('data_pca.csv')
    print(f"PCA explained variance ratio: {pca.explained_variance_ratio_}")
    
    # 3. WGCNA (Agglomerative Clustering + Module Mean) Data
    print("Performing Agglomerative Clustering (WGCNA approximation)...")
    # Transpose X to cluster the features (CpG sites), not the samples
    # We use correlation distance to group features that move together
    n_modules = 5
    clusterer = AgglomerativeClustering(n_clusters=n_modules, metric='correlation', linkage='average')
    labels = clusterer.fit_predict(X_scaled.T)
    
    X_module = np.zeros((X.shape[0], n_modules))
    module_cols = []
    for i in range(n_modules):
        # Find which features belong to module i
        module_features = X[:, labels == i]
        # Compute the mean of the raw features in this module
        X_module[:, i] = np.mean(module_features, axis=1)
        module_cols.append(f'ME{i+1}')
        print(f"Module {i+1}: {module_features.shape[1]} features")
        
    df_wgcna = pd.DataFrame(X_module, columns=module_cols, index=df.index)
    df_wgcna['Age'] = df['Age']
    df_wgcna.to_csv('data_wgcna.csv')
    
    print("Preprocessing complete. Output files: data_raw.csv, data_pca.csv, data_wgcna.csv")

if __name__ == "__main__":
    main()
