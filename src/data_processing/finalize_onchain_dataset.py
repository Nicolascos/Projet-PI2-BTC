"""
On-Chain Dataset Finalization Script

This script:
1. Calculates NVT and NVT Signal (missing from raw data)
2. Fetches Lightning Network data (mempool.space)
3. Fetches Developer Activity data (GitHub API)
4. Cleans up redundant columns
5. Saves the finalized dataset
"""

import pandas as pd
import numpy as np
import requests
import time
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
INPUT_FILE = Path(__file__).parent.parent.parent / "data" / "processed" / "onchain_data_complete.csv"
OUTPUT_FILE = Path(__file__).parent.parent.parent / "data" / "processed" / "onchain_data_finalized.csv"


def fetch_bitcoin_price():
    """Fetches historical Bitcoin price from Blockchain.com to calculate Market Cap."""
    print("\n" + "="*60)
    print("FETCHING BITCOIN PRICE FOR NVT CALCULATION")
    print("="*60)
    
    url = "https://api.blockchain.info/charts/market-price?timespan=all&format=json"
    
    try:
        print("  Fetching from Blockchain.com...")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        data = r.json()
        
        df = pd.DataFrame(data['values'])
        df['date'] = pd.to_datetime(df['x'], unit='s').dt.normalize()
        df = df.set_index('date')
        df = df.rename(columns={'y': 'price_usd'})
        df = df[['price_usd']]
        
        # Remove duplicates
        df = df[~df.index.duplicated(keep='last')]
        
        print(f"  ✓ Retrieved {len(df)} price data points")
        print(f"  Range: {df.index.min().date()} to {df.index.max().date()}")
        
        return df
        
    except Exception as e:
        print(f"  ✗ Error fetching price: {e}")
        return None


def calculate_nvt_metrics(df):
    """Calculate NVT and NVT Signal metrics."""
    print("\n" + "="*60)
    print("CALCULATING NVT METRICS")
    print("="*60)
    
    metrics_added = 0
    
    # Check required columns
    if 'SplyCur' not in df.columns:
        print("  ✗ 'SplyCur' not found - cannot calculate Market Cap")
        return df, 0
    
    if 'est_tx_volume_usd' not in df.columns:
        print("  ✗ 'est_tx_volume_usd' not found - cannot calculate NVT")
        return df, 0
    
    if 'price_usd' not in df.columns:
        print("  ✗ 'price_usd' not found - cannot calculate Market Cap")
        return df, 0
    
    # Calculate Market Cap = Supply × Price
    df['market_cap_usd'] = df['SplyCur'] * df['price_usd']
    print("  ✓ market_cap_usd: Supply × Price")
    metrics_added += 1
    
    # Calculate NVT = Market Cap / Transaction Volume
    # Avoid division by zero
    df['NVT'] = np.where(
        df['est_tx_volume_usd'] > 0,
        df['market_cap_usd'] / df['est_tx_volume_usd'],
        np.nan
    )
    print("  ✓ NVT: Market Cap / Daily Transaction Volume")
    metrics_added += 1
    
    # Calculate NVT Signal = Market Cap / 90-day MA of Volume
    df['tx_volume_90d_ma'] = df['est_tx_volume_usd'].rolling(window=90, min_periods=30).mean()
    df['NVT_Signal'] = np.where(
        df['tx_volume_90d_ma'] > 0,
        df['market_cap_usd'] / df['tx_volume_90d_ma'],
        np.nan
    )
    print("  ✓ NVT_Signal: Market Cap / 90-day MA of Volume (less noisy)")
    metrics_added += 1
    
    print(f"\n  Total NVT metrics added: {metrics_added}")
    
    return df, metrics_added


def cleanup_redundant_columns(df):
    """Remove redundant/duplicate columns to keep dataset clean."""
    print("\n" + "="*60)
    print("CLEANING UP REDUNDANT COLUMNS")
    print("="*60)
    
    # Columns to drop (keeping CoinMetrics versions where duplicated)
    cols_to_drop = [
        'n_transactions',       # Duplicate of TxCnt
        'hash_rate',            # Duplicate of HashRate
        'unique_addresses',     # Duplicate of AdrActCnt
        'output_volume_btc',    # Less useful than USD version
        'est_tx_volume_btc',    # We use USD version
        'tx_fees_btc',          # We use USD version
        'trade_volume_usd',     # Exchange volume (not fundamental on-chain)
        'tx_volume_90d_ma',     # Intermediate calculation (used for NVT_Signal)
        'tx_volume_7d_ma',      # Intermediate calculation
        'active_addr_7d_ma',    # Intermediate calculation
    ]
    
    # Only drop columns that exist
    existing_to_drop = [c for c in cols_to_drop if c in df.columns]
    
    if existing_to_drop:
        df = df.drop(columns=existing_to_drop)
        print(f"  Dropped {len(existing_to_drop)} redundant columns:")
        for col in existing_to_drop:
            print(f"    - {col}")
    else:
        print("  No redundant columns to drop")
    
    return df


def fetch_lightning_network_data():
    """
    Fetch Lightning Network statistics from mempool.space API.
    Note: Only recent data is available (last ~3 years), not full historical.
    """
    print("\n" + "="*60)
    print("FETCHING LIGHTNING NETWORK DATA")
    print("="*60)
    
    try:
        # mempool.space provides LN statistics
        url = "https://mempool.space/api/v1/lightning/statistics/3y"
        headers = {"User-Agent": "Mozilla/5.0 Bitcoin Research"}
        
        print("  Fetching from mempool.space...")
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        if isinstance(data, list) and len(data) > 0:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['added'], unit='s').dt.normalize()
            df = df.set_index('date')
            
            # Select relevant columns
            ln_cols = {
                'channel_count': 'ln_channel_count',
                'node_count': 'ln_node_count', 
                'total_capacity': 'ln_capacity_sat',
            }
            
            df = df.rename(columns=ln_cols)
            df = df[[c for c in ln_cols.values() if c in df.columns]]
            
            # Remove duplicates
            df = df[~df.index.duplicated(keep='last')]
            
            print(f"  ✓ Retrieved {len(df)} days of Lightning Network data")
            print(f"  Range: {df.index.min().date()} to {df.index.max().date()}")
            return df
        else:
            print("  ⚠️ No data returned from API")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return pd.DataFrame()


def fetch_github_developer_activity():
    """
    Fetch Bitcoin Core GitHub commit activity.
    GitHub API returns last 52 weeks of commit data.
    """
    print("\n" + "="*60)
    print("FETCHING DEVELOPER ACTIVITY (GitHub)")
    print("="*60)
    
    try:
        url = "https://api.github.com/repos/bitcoin/bitcoin/stats/commit_activity"
        headers = {
            "User-Agent": "Mozilla/5.0 Bitcoin Research",
            "Accept": "application/vnd.github.v3+json"
        }
        
        print("  Fetching from GitHub API (bitcoin/bitcoin repo)...")
        r = requests.get(url, headers=headers, timeout=30)
        
        if r.status_code == 202:
            # GitHub is computing stats, retry after a moment
            print("  Waiting for GitHub to compute statistics...")
            time.sleep(3)
            r = requests.get(url, headers=headers, timeout=30)
        
        r.raise_for_status()
        data = r.json()
        
        if isinstance(data, list) and len(data) > 0:
            # Each entry is a week with 'week' (timestamp) and 'total' (commits)
            records = []
            for week in data:
                week_start = datetime.fromtimestamp(week['week'])
                # Expand to daily (distribute commits across week)
                weekly_commits = week['total']
                for day_offset in range(7):
                    date = week_start + timedelta(days=day_offset)
                    records.append({
                        'date': date,
                        'btc_commits_weekly': weekly_commits,  # Same for whole week
                    })
            
            df = pd.DataFrame(records)
            df['date'] = pd.to_datetime(df['date']).dt.normalize()
            df = df.set_index('date')
            df = df[~df.index.duplicated(keep='last')]
            
            print(f"  ✓ Retrieved {len(df)} days of developer activity")
            print(f"  Range: {df.index.min().date()} to {df.index.max().date()}")
            return df
        else:
            print("  ⚠️ No data returned from API")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return pd.DataFrame()


def validate_final_dataset(df):
    """Validate the finalized dataset."""
    print("\n" + "="*60)
    print("FINAL DATASET VALIDATION")
    print("="*60)
    
    print(f"\n  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"  Date Range: {df.index.min().date()} to {df.index.max().date()}")
    
    # Check for missing values
    print("\n  Missing Values (>1%):")
    has_significant_missing = False
    for col in df.columns:
        nan_pct = df[col].isna().sum() / len(df) * 100
        if nan_pct > 1:
            print(f"    • {col}: {nan_pct:.1f}%")
            has_significant_missing = True
    
    if not has_significant_missing:
        print("    All columns have <1% missing values ✓")
    
    # Key metrics summary
    print("\n  Key Metrics Present:")
    key_metrics = ['CapMVRVCur', 'NVT', 'NVT_Signal', 'HashRate', 'mining_difficulty', 
                   'miner_revenue_usd', 'market_cap_usd', 'days_since_halving']
    for metric in key_metrics:
        status = "✓" if metric in df.columns else "✗"
        print(f"    {status} {metric}")


def main():
    """Main function to finalize the on-chain dataset."""
    print("\n" + "#"*60)
    print("# ON-CHAIN DATASET FINALIZATION")
    print("#"*60)
    
    start_time = time.time()
    
    # 1. Load the dataset
    print(f"\nLoading dataset from: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    
    # Parse date column
    date_col = [c for c in df.columns if 'date' in c.lower()][0]
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    
    print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # 2. Fetch Bitcoin price
    price_df = fetch_bitcoin_price()
    
    if price_df is not None:
        # Merge price data - reindex to match our dates
        price_df = price_df.reindex(df.index, method='ffill')
        price_df = price_df.bfill()  # Fill any NaN at start
        df = df.join(price_df, how='left')
        print(f"  ✓ Merged price data")
    
    # 3. Calculate NVT metrics
    df, nvt_count = calculate_nvt_metrics(df)
    
    # 4. Fetch Lightning Network data (new!)
    ln_df = fetch_lightning_network_data()
    if not ln_df.empty:
        ln_df = ln_df.reindex(df.index, method='ffill')
        df = df.join(ln_df, how='left')
        print(f"  ✓ Merged Lightning Network data")
    
    # 5. Fetch Developer Activity (new!)
    dev_df = fetch_github_developer_activity()
    if not dev_df.empty:
        dev_df = dev_df.reindex(df.index, method='ffill')
        df = df.join(dev_df, how='left')
        print(f"  ✓ Merged Developer Activity data")
    
    # 6. Clean up redundant columns
    df = cleanup_redundant_columns(df)
    
    # 7. Validate
    validate_final_dataset(df)
    
    # 8. Save
    df.to_csv(OUTPUT_FILE)
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*60)
    print("FINALIZATION COMPLETE!")
    print("="*60)
    print(f"  Output: {OUTPUT_FILE}")
    print(f"  Final Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"  Execution time: {elapsed:.1f} seconds")
    
    print("\n  Final Columns:")
    for i, col in enumerate(df.columns, 1):
        print(f"    {i:2}. {col}")
    
    return df


if __name__ == "__main__":
    df = main()
