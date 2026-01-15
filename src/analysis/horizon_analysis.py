import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import TimeSeriesSplit
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform

# 1. Load Data
print("Loading Three Pillars Dataset...")
df = pd.read_csv('../../data/processed/Three_Pillars_Dataset.csv', index_col=0, parse_dates=True)

# 2. Define Helper Functions (Clustering + MDA)
def get_clusters(X, threshold=0.5):
    corr = X.corr(method='spearman')
    dist = 1 - np.abs(corr)
    linkage = hierarchy.linkage(squareform(dist), method='ward')
    cluster_ids = hierarchy.fcluster(linkage, threshold, criterion='distance')
    return cluster_ids

def run_mda_score(X, y, cluster_ids):
    rf = RandomForestRegressor(n_estimators=50, max_depth=4, random_state=42, n_jobs=-1)
    cv = TimeSeriesSplit(n_splits=3) # 3 splits for speed
    imps = {}
    
    for train, test in cv.split(X):
        rf.fit(X.iloc[train], y.iloc[train])
        base = r2_score(y.iloc[test], rf.predict(X.iloc[test]))
        
        unique_clusters = np.unique(cluster_ids)
        for cid in unique_clusters:
            X_shuff = X.iloc[test].copy()
            cols = X.columns[cluster_ids == cid]
            for c in cols: X_shuff[c] = np.random.permutation(X_shuff[c].values)
            score = r2_score(y.iloc[test], rf.predict(X_shuff))
            imps[cid] = imps.get(cid, 0) + (base - score)
            
    return imps

# 3. Run Analysis for T+1, T+7, T+30
horizons = [1, 7, 30]
results = []

print("--- Starting Horizon Analysis ---")

for h in horizons:
    print(f"  Processing Horizon T+{h}...")
    # Create Target: Future Return
    target_col = f'target_{h}d'
    df[target_col] = df['XBTUSD'].pct_change(h).shift(-h)
    
    # Prep Data
    temp = df.dropna()
    X = temp.drop(columns=[c for c in temp.columns if 'target' in c])
    y = temp[target_col]
    
    # Run MDA
    c_ids = get_clusters(X)
    scores = run_mda_score(X, y, c_ids)
    
    # Get Top 3 Clusters
    sorted_clusters = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    for rank, (cid, score) in enumerate(sorted_clusters):
        feats = X.columns[c_ids == cid].tolist()
        # Take first 3 features as representative name
        feat_name = ", ".join(feats[:3]) 
        
        results.append({
            'Horizon': f'T+{h}',
            'Rank': rank + 1,
            'Importance': round(score, 5),
            'Top_Features': feat_name
        })

# 4. Save Results
results_df = pd.DataFrame(results)
output_file = '../../data/outputs/metrics/horizon_analysis_results.csv'
results_df.to_csv(output_file, index=False)

print(f"\nSUCCESS! Results saved to '{output_file}'")
print(results_df)