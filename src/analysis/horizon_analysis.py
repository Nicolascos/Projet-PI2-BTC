"""
Clustered MDA (Mean Decrease Accuracy) across T+1, T+7, T+30 horizons.

Loads data from the Bloomberg Excel file (same source as CausalAnalysis.ipynb),
applies stationarity transforms, then runs RandomForest + permutation importance
grouped by Spearman-correlation clusters.

Outputs:
  - data/outputs/metrics/horizon_analysis_results.csv   (cluster-level)
  - data/outputs/metrics/horizon_feature_importance.csv  (feature-level)

Run from repo root:
    conda run -n pi2 python src/analysis/horizon_analysis.py
"""

import os
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import TimeSeriesSplit
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform

# ============================================================
# CONFIGURATION (aligned with CausalAnalysis.ipynb)
# ============================================================
BTC_TICKER = "XBTUSD Curncy"
BTC_DERIVED = {'price_usd', 'market_cap_usd', BTC_TICKER}
START_DATE = "2015-01-01"
DEFAULT_VAR = "px_last"

# Resolve paths relative to the repo root
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXCEL_PATH = os.path.join(REPO_ROOT, "notebooks", "indicatorsMY_v02.xlsx")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "outputs", "metrics")

# Feature categories (Vaissié's 3-pillar framework)
FEATURE_CATEGORIES = {
    'On-Chain': [
        'HashRate', 'AdrActCnt', 'TxCnt', 'TxTfrCnt', 'CapMVRVCur', 'NVT',
        'NVT_Signal', 'SplyCur', 'mining_difficulty', 'miner_revenue_usd',
        'hashrate_7d_pct', 'tx_fees_usd', 'est_tx_volume_usd', 'avg_block_size',
        'mempool_count', 'mempool_growth', 'utxo_count', 'active_addr_ratio',
        'difficulty_14d_pct', 'cost_per_tx_usd', 'tx_per_second',
        'n_tx_excl_popular', 'mempool_size_bytes',
    ],
    'Macro': [
        'VIX Index', 'MOVE Index', 'DXY Curncy', 'SPX Index', 'CCMP Index',
        'RTY Index', 'XAU Curncy', 'M2 Index', 'ECMAM2 Index',
        'USYC2Y10 Index', 'DEYC2Y10 Index', 'USGG3M Index', 'EURUSD Curncy',
        'JPYUSD Curncy', 'CNH Curncy', 'FARBAST Index', 'LUATTRUU Index',
        'CL1 COMB Comdty', 'NG1 COMB Comdty',
    ],
    'Sentiment': [
        'fear_and_greed', 'btc_balance_on_exchanges', 'total_stablecoin_mcap',
        'btc_dominance_proxy', 'Bitcoin', 'Coinbase', 'BlackRock Bitcoin',
        'Buy Bitcoin', 'FOMO', 'HODL', 'Bull Run', 'Bear Market', 'Crypto',
        'Bitcoin Mining', 'Recession', 'Inflation', 'Interest Rates',
    ],
    'Crypto Market': [
        'XETUSD Curncy', 'XBNUSD Curncy', 'XRPUSD Curncy', 'XLCUSD Curncy',
        # CFTC Bitcoin Futures positioning (from Open_Interests_Futures sheet)
        'TFC2RLFS Index', 'CFC5ROIN Index', 'TFF2RLFD Index', 'TFF2RAIN Index',
        'TFC2RORS Index',
    ],
}

def get_category(ticker):
    for cat, tickers in FEATURE_CATEGORIES.items():
        if ticker in tickers:
            return cat
    return 'Other'

# Bounded/ratio features: use first-diff (not pct_change)
BOUNDED_FEATURES = {
    'fear_and_greed', 'CapMVRVCur', 'NVT', 'NVT_Signal',
    'active_addr_ratio', 'btc_dominance_proxy',
    'VIX Index', 'MOVE Index', 'USYC2Y10 Index', 'DEYC2Y10 Index',
    'CESIUSD Index', 'CESIJPY Index',
}
GOOGLE_TRENDS = {
    'Bitcoin', 'Coinbase', 'BlackRock Bitcoin', 'Bitcoin Halving',
    'Buy Bitcoin', 'FOMO', 'HODL', 'Bull Run', 'Bear Market',
    'Crypto', 'Bitcoin Mining', 'Recession', 'Inflation', 'Interest Rates',
}

# ============================================================
# 1. LOAD DATA (same pipeline as CausalAnalysis.ipynb cells 3-5)
# ============================================================
print(f"Loading data from {EXCEL_PATH}...")
assert os.path.exists(EXCEL_PATH), f"Excel file not found: {EXCEL_PATH}"

sheets = pd.read_excel(EXCEL_PATH, sheet_name=None)
print(f"  Sheets: {list(sheets.keys())}")

df_list = []
for name, sheet in sheets.items():
    sheet = sheet.dropna(how='all', axis=0).dropna(how='all', axis=1)
    if sheet.shape[1] < 3:
        continue
    a1 = str(sheet.columns[0]).strip().lower()
    b1 = str(sheet.columns[1]).strip().upper()

    if b1 == "DATES":
        tmp = sheet.copy()
        tmp.columns = ["Ticker", "Variable"] + list(tmp.columns[2:])
        tmp["Variable"] = tmp["Variable"].astype(str).str.strip()
        tmp = tmp[tmp["Variable"] == DEFAULT_VAR]
        if tmp.empty:
            continue
        melted = tmp.melt(id_vars=["Ticker", "Variable"], var_name="Date", value_name="Value")
    elif a1 == "date":
        tmp = sheet.copy()
        tmp = tmp.rename(columns={tmp.columns[0]: "Ticker"})
        tmp.insert(1, "Variable", DEFAULT_VAR)
        melted = tmp.melt(id_vars=["Ticker", "Variable"], var_name="Date", value_name="Value")
    else:
        continue

    melted["Date"] = pd.to_datetime(melted["Date"], errors="coerce")
    melted["Value"] = pd.to_numeric(melted["Value"], errors="coerce")
    melted = melted.dropna(subset=["Date", "Value"])
    melted["Ticker"] = melted["Ticker"].astype(str).str.strip()
    if melted["Date"].dt.tz is not None:
        melted["Date"] = melted["Date"].dt.tz_localize(None)
    df_list.append(melted)

merged_df = pd.concat(df_list, ignore_index=True)
merged_df["Date"] = pd.to_datetime(merged_df["Date"], errors="coerce").dt.tz_localize(None)

pivot_df = merged_df.pivot_table(index="Date", columns="Ticker", values="Value", aggfunc='mean')
pivot_df = pivot_df.sort_index()
pivot_df = pivot_df[pivot_df.index >= START_DATE]

assert BTC_TICKER in pivot_df.columns, f"{BTC_TICKER} not found in data!"
print(f"  Pivot: {pivot_df.shape[0]} days x {pivot_df.shape[1]} features")

# ============================================================
# 2. SELECT FEATURES (same set as CausalAnalysis.ipynb)
# ============================================================
selected_tickers = list(dict.fromkeys([
    # On-Chain
    'HashRate', 'mining_difficulty', 'miner_revenue_usd', 'hashrate_7d_pct',
    'AdrActCnt', 'TxCnt', 'est_tx_volume_usd', 'avg_block_size',
    'CapMVRVCur', 'NVT', 'SplyCur',
    # Macro
    'VIX Index', 'MOVE Index', 'DXY Curncy', 'SPX Index', 'CCMP Index',
    'RTY Index', 'USYC2Y10 Index', 'DEYC2Y10 Index', 'M2 Index',
    'FARBAST Index',
    # Sentiment
    'fear_and_greed', 'total_stablecoin_mcap', 'btc_balance_on_exchanges',
    'Bitcoin', 'Coinbase', 'BlackRock Bitcoin', 'Buy Bitcoin',
    # Crypto Market (altcoins + BTC futures positioning)
    'XETUSD Curncy', 'XBNUSD Curncy', 'XRPUSD Curncy',
    'TFC2RLFS Index', 'CFC5ROIN Index',
]))

available_tickers = [t for t in selected_tickers
                     if t in pivot_df.columns and t not in BTC_DERIVED]

print(f"  Features selected: {len(available_tickers)}")

# ============================================================
# 3. PREPARE DATA (stationarity transforms + weekly resampling)
# ============================================================
def prepare_data(pivot_df, tickers, resample='W'):
    """Apply stationarity transforms (same logic as CausalAnalysis.ipynb)."""
    cols = [c for c in tickers if c in pivot_df.columns]
    if BTC_TICKER not in cols:
        cols.append(BTC_TICKER)

    df = pivot_df[cols].copy()
    df = df[df.index >= START_DATE]
    df = df.resample(resample).mean()

    # Truncate to common date range (70th percentile of first-valid dates)
    first_valid = df.apply(lambda s: s.first_valid_index())
    common_start = first_valid.quantile(0.7)
    df = df[df.index >= common_start]
    df = df.ffill()

    # Drop features with >50% NaN
    na_frac = df.isna().mean()
    df = df.drop(columns=na_frac[na_frac > 0.5].index.tolist())
    df = df.dropna()

    # Apply stationarity transforms
    df_out = pd.DataFrame(index=df.index)
    for col in df.columns:
        if col in BOUNDED_FEATURES or col in GOOGLE_TRENDS:
            df_out[col] = df[col].diff()
        else:
            df_out[col] = df[col].pct_change()

    df_out = df_out.replace([np.inf, -np.inf], np.nan)
    df_out = df_out.iloc[1:]
    df_out = df_out.ffill().dropna()
    return df_out

# ============================================================
# 4. HELPER FUNCTIONS (Clustering + MDA)
# ============================================================
def get_clusters(X, threshold=0.5):
    """Cluster features by Spearman correlation (Ward linkage)."""
    corr = X.corr(method='spearman')
    dist = 1 - np.abs(corr)
    np.fill_diagonal(dist.values, 0)
    dist = dist.clip(lower=0)
    linkage = hierarchy.linkage(squareform(dist), method='ward')
    cluster_ids = hierarchy.fcluster(linkage, threshold, criterion='distance')
    return cluster_ids


def run_clustered_mda(X, y, cluster_ids, n_estimators=200, n_splits=5):
    """
    Clustered Mean Decrease Accuracy.
    For each cluster, permute all features in it and measure R² drop.
    Returns both cluster-level and feature-level importance.
    """
    rf = RandomForestRegressor(n_estimators=n_estimators, max_depth=5,
                               random_state=42, n_jobs=-1)
    cv = TimeSeriesSplit(n_splits=n_splits)

    cluster_imps = {}
    feature_imps_raw = {}

    for fold, (train, test) in enumerate(cv.split(X)):
        rf.fit(X.iloc[train], y.iloc[train])
        base = r2_score(y.iloc[test], rf.predict(X.iloc[test]))

        # Cluster-level importance
        for cid in np.unique(cluster_ids):
            X_shuff = X.iloc[test].copy()
            cols = X.columns[cluster_ids == cid]
            rng = np.random.RandomState(42 + fold + cid)
            for c in cols:
                X_shuff[c] = rng.permutation(X_shuff[c].values)
            score = r2_score(y.iloc[test], rf.predict(X_shuff))
            cluster_imps[cid] = cluster_imps.get(cid, 0) + (base - score)

        # Individual feature importance (single-feature permutation)
        for i, col in enumerate(X.columns):
            X_shuff = X.iloc[test].copy()
            rng = np.random.RandomState(42 + fold + i)
            X_shuff[col] = rng.permutation(X_shuff[col].values)
            score = r2_score(y.iloc[test], rf.predict(X_shuff))
            feature_imps_raw[col] = feature_imps_raw.get(col, 0) + (base - score)

    # Average across folds
    n = n_splits
    cluster_imps = {k: v / n for k, v in cluster_imps.items()}
    feature_imps = {k: v / n for k, v in feature_imps_raw.items()}
    return cluster_imps, feature_imps


# ============================================================
# 5. RUN ANALYSIS FOR T+1, T+7, T+30
# ============================================================
horizons = [1, 7, 30]
cluster_results = []
feature_results = []

print("\n--- Starting Horizon Analysis ---")

for h in horizons:
    print(f"\n  Horizon T+{h}...")

    # Prepare weekly data
    df_w = prepare_data(pivot_df, available_tickers, resample='W')

    # Create target: future h-week BTC return
    df_w[f'target_{h}w'] = df_w[BTC_TICKER].rolling(h).sum().shift(-h)
    temp = df_w.dropna()

    X = temp.drop(columns=[c for c in temp.columns if c.startswith('target_') or c == BTC_TICKER])
    y = temp[f'target_{h}w']

    if len(X) < 30:
        print(f"    Skipping T+{h}: only {len(X)} samples")
        continue

    print(f"    Data: {X.shape[0]} weeks x {X.shape[1]} features")

    # Cluster and run MDA
    c_ids = get_clusters(X)
    cluster_imps, feature_imps = run_clustered_mda(X, y, c_ids)

    # --- Cluster-level results (top 5) ---
    sorted_clusters = sorted(cluster_imps.items(), key=lambda x: x[1], reverse=True)[:5]
    for rank, (cid, score) in enumerate(sorted_clusters):
        feats = X.columns[c_ids == cid].tolist()
        cats = [get_category(f) for f in feats]
        dominant_cat = max(set(cats), key=cats.count)
        cluster_results.append({
            'Horizon': f'T+{h}',
            'Rank': rank + 1,
            'Cluster_ID': int(cid),
            'Importance': round(score, 5),
            'Category': dominant_cat,
            'Top_Features': ', '.join(feats[:5]),
            'N_Features': len(feats),
        })

    # --- Feature-level results ---
    for feat, imp in sorted(feature_imps.items(), key=lambda x: x[1], reverse=True):
        feature_results.append({
            'Horizon': f'T+{h}',
            'Feature': feat,
            'Importance': round(imp, 5),
            'Category': get_category(feat),
        })

    # Print top 10 features for this horizon
    top10 = sorted(feature_imps.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"    Top 10 features:")
    for rank, (feat, imp) in enumerate(top10, 1):
        print(f"      {rank:2d}. {feat:30s}  MDA={imp:+.5f}  ({get_category(feat)})")

# ============================================================
# 6. SAVE RESULTS
# ============================================================
os.makedirs(OUTPUT_DIR, exist_ok=True)

cluster_df = pd.DataFrame(cluster_results)
cluster_path = os.path.join(OUTPUT_DIR, 'horizon_analysis_results.csv')
cluster_df.to_csv(cluster_path, index=False)

feature_df = pd.DataFrame(feature_results)
feature_path = os.path.join(OUTPUT_DIR, 'horizon_feature_importance.csv')
feature_df.to_csv(feature_path, index=False)

print(f"\n{'='*60}")
print(f"Cluster results saved to: {cluster_path}")
print(f"Feature results saved to: {feature_path}")
print(f"{'='*60}")
print("\nCluster-level results:")
print(cluster_df.to_string(index=False))
print("\nTop 5 features per horizon:")
for h in horizons:
    hdf = feature_df[feature_df['Horizon'] == f'T+{h}'].head(5)
    if not hdf.empty:
        print(f"\n  T+{h}:")
        for _, row in hdf.iterrows():
            print(f"    {row['Feature']:30s}  MDA={row['Importance']:+.5f}  ({row['Category']})")