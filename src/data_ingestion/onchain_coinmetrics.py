"""
On-Chain Data Extraction for Bitcoin Performance Modeling

This script fetches Bitcoin on-chain metrics from multiple free sources:
1. CoinMetrics Community API (MVRV, TxCnt, AdrActCnt, HashRate, Supply)
2. Blockchain.com API (Difficulty, Transaction Volume, Miner Revenue)

Output: Daily on-chain dataset saved to data/processed/onchain_data_complete.csv

Free Data Sources Used:
- CoinMetrics Free API: Best for MVRV, network activity metrics
- Blockchain.com Charts API: Mining difficulty, revenue, transaction volume
"""

import pandas as pd
import requests
import time
from datetime import datetime
from pathlib import Path
from coinmetrics.api_client import CoinMetricsClient

# =============================================================================
# CONFIGURATION
# =============================================================================

START_DATE = "2015-01-01"  # Start from 2015 for maximum historical depth
END_DATE = datetime.now().strftime('%Y-%m-%d')
# Path relative to project root: src/data_ingestion -> ../../data/processed
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "onchain_data_complete.csv"

# CoinMetrics Free Tier Metrics (tested and confirmed available Jan 2025)
COINMETRICS_METRICS = {
    'CapMVRVCur': 'MVRV Ratio (Market Cap / Realized Cap)',
    'TxCnt': 'Transaction Count',
    'AdrActCnt': 'Active Addresses',
    'TxTfrCnt': 'Transfer Count',
    'HashRate': 'Network Hash Rate',
    'SplyCur': 'Current Supply',
    'BlkCnt': 'Block Count',
}

# Blockchain.com Charts API endpoints (free, no API key required)
# Full list based on partner requirements - all tested and available Jan 2025
BLOCKCHAIN_CHARTS = {
    # Market & Volume
    'trade-volume': 'https://api.blockchain.info/charts/trade-volume?timespan=all&format=json',
    'output-volume': 'https://api.blockchain.info/charts/output-volume?timespan=all&format=json',
    'estimated-transaction-volume': 'https://api.blockchain.info/charts/estimated-transaction-volume?timespan=all&format=json',
    'estimated-transaction-volume-usd': 'https://api.blockchain.info/charts/estimated-transaction-volume-usd?timespan=all&format=json',
    
    # Block Metrics
    'avg-block-size': 'https://api.blockchain.info/charts/avg-block-size?timespan=all&format=json',
    'n-transactions-per-block': 'https://api.blockchain.info/charts/n-transactions-per-block?timespan=all&format=json',
    
    # Confirmation Times
    'median-confirmation-time': 'https://api.blockchain.info/charts/median-confirmation-time?timespan=all&format=json',
    'avg-confirmation-time': 'https://api.blockchain.info/charts/avg-confirmation-time?timespan=all&format=json',
    
    # Mining
    'hash-rate': 'https://api.blockchain.info/charts/hash-rate?timespan=all&format=json',
    'difficulty': 'https://api.blockchain.info/charts/difficulty?timespan=all&format=json',
    'miners-revenue': 'https://api.blockchain.info/charts/miners-revenue?timespan=all&format=json',
    
    # Fees
    'transaction-fees': 'https://api.blockchain.info/charts/transaction-fees?timespan=all&format=json',
    'transaction-fees-usd': 'https://api.blockchain.info/charts/transaction-fees-usd?timespan=all&format=json',
    'cost-per-transaction': 'https://api.blockchain.info/charts/cost-per-transaction?timespan=all&format=json',
    
    # Network Activity
    'n-unique-addresses': 'https://api.blockchain.info/charts/n-unique-addresses?timespan=all&format=json',
    'n-transactions': 'https://api.blockchain.info/charts/n-transactions?timespan=all&format=json',
    'n-transactions-excluding-popular': 'https://api.blockchain.info/charts/n-transactions-excluding-popular?timespan=all&format=json',
    'transactions-per-second': 'https://api.blockchain.info/charts/transactions-per-second?timespan=all&format=json',
    
    # Mempool
    'mempool-count': 'https://api.blockchain.info/charts/mempool-count?timespan=all&format=json',
    'mempool-growth': 'https://api.blockchain.info/charts/mempool-growth?timespan=all&format=json',
    'mempool-size': 'https://api.blockchain.info/charts/mempool-size?timespan=all&format=json',
    
    # UTXO
    'utxo-count': 'https://api.blockchain.info/charts/utxo-count?timespan=all&format=json',
}

# Bitcoin Halving Dates (for computing halving metrics)
BITCOIN_HALVINGS = [
    pd.Timestamp('2012-11-28'),  # Block 210,000 - 50 -> 25 BTC
    pd.Timestamp('2016-07-09'),  # Block 420,000 - 25 -> 12.5 BTC
    pd.Timestamp('2020-05-11'),  # Block 630,000 - 12.5 -> 6.25 BTC
    pd.Timestamp('2024-04-19'),  # Block 840,000 - 6.25 -> 3.125 BTC
]
# Estimated next halving (approximately every 4 years / 210,000 blocks)
NEXT_HALVING_ESTIMATE = pd.Timestamp('2028-04-01')


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def fetch_with_retry(func, max_retries=3, base_delay=5):
    """Execute a function with exponential backoff retry logic."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            delay = base_delay * (2 ** attempt)
            print(f"  Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)


def fetch_coinmetrics_data():
    """
    Fetch Bitcoin on-chain metrics from CoinMetrics Community API.
    Returns a DataFrame with daily data.
    """
    print("\n" + "="*60)
    print("SOURCE 1: COINMETRICS (Free API)")
    print("="*60)
    
    metrics_list = list(COINMETRICS_METRICS.keys())
    print(f"\nMetrics: {len(metrics_list)}")
    for metric, desc in COINMETRICS_METRICS.items():
        print(f"  • {metric}: {desc}")
    
    client = CoinMetricsClient()
    
    def fetch():
        return client.get_asset_metrics(
            assets='btc',
            metrics=metrics_list,
            frequency="1d",
            start_time=START_DATE,
            end_time=END_DATE,
            page_size=10000
        )
    
    print("\nFetching data from CoinMetrics API...")
    asset_metrics = fetch_with_retry(fetch)
    
    # Convert to DataFrame
    df = asset_metrics.to_dataframe()
    df = df.reset_index()
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')
    
    # Drop the asset column, status columns, and index column (redundant)
    cols_to_drop = [col for col in df.columns if 'asset' in col.lower() or 'status' in col.lower() or col == 'index']
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
    
    # Rename index for clarity
    df.index.name = 'date'
    
    # Remove timezone info for compatibility
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    
    print(f"  ✓ Retrieved {len(df)} days of data")
    return df


def fetch_blockchain_chart(chart_name, url):
    """Fetch data from Blockchain.com Charts API."""
    print(f"  Fetching {chart_name}...")
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # Convert to DataFrame
        values = data.get('values', [])
        df = pd.DataFrame(values)
        df['date'] = pd.to_datetime(df['x'], unit='s').dt.normalize()  # Normalize to midnight
        df = df.set_index('date')
        df = df.rename(columns={'y': chart_name})
        df = df[[chart_name]]
        
        # Remove duplicates (keep last if same date)
        df = df[~df.index.duplicated(keep='last')]
        
        print(f"    ✓ {len(df)} data points")
        return df
        
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return pd.DataFrame()


def fetch_blockchain_data():
    """
    Fetch supplementary metrics from Blockchain.com Charts API.
    Returns a DataFrame with sparse data (every ~4 days).
    """
    print("\n" + "="*60)
    print("SOURCE 2: BLOCKCHAIN.COM (Charts API)")
    print("="*60)
    print("\nFree API - No rate limits, all historical data")
    
    dfs = []
    
    for chart_name, url in BLOCKCHAIN_CHARTS.items():
        df = fetch_blockchain_chart(chart_name, url)
        if not df.empty:
            dfs.append(df)
        time.sleep(1)  # Be nice to the API
    
    if dfs:
        # Merge all blockchain.com data - use how='outer' to get union of dates
        blockchain_df = dfs[0]
        for df in dfs[1:]:
            blockchain_df = blockchain_df.join(df, how='outer')
        
        # Forward fill within each column to fill gaps from outer join
        blockchain_df = blockchain_df.ffill()
        
        # Rename columns to snake_case for consistency
        rename_map = {
            'trade-volume': 'trade_volume_usd',
            'output-volume': 'output_volume_btc',
            'estimated-transaction-volume': 'est_tx_volume_btc',
            'estimated-transaction-volume-usd': 'est_tx_volume_usd',
            'avg-block-size': 'avg_block_size',
            'n-transactions-per-block': 'tx_per_block',
            'median-confirmation-time': 'median_confirm_time',
            'avg-confirmation-time': 'avg_confirm_time',
            'hash-rate': 'hash_rate',
            'difficulty': 'mining_difficulty',
            'miners-revenue': 'miner_revenue_usd',
            'transaction-fees': 'tx_fees_btc',
            'transaction-fees-usd': 'tx_fees_usd',
            'cost-per-transaction': 'cost_per_tx_usd',
            'n-unique-addresses': 'unique_addresses',
            'n-transactions': 'n_transactions',
            'n-transactions-excluding-popular': 'n_tx_excl_popular',
            'transactions-per-second': 'tx_per_second',
            'mempool-count': 'mempool_count',
            'mempool-growth': 'mempool_growth',
            'mempool-size': 'mempool_size_bytes',
            'utxo-count': 'utxo_count',
        }
        blockchain_df = blockchain_df.rename(columns=rename_map)
        
        return blockchain_df
    
    return pd.DataFrame()


def compute_derived_metrics(df):
    """
    Compute additional derived metrics from base data.
    These provide extra analytical value for causal analysis.
    """
    print("\n" + "="*60)
    print("COMPUTING DERIVED METRICS")
    print("="*60)
    
    derived_count = 0
    
    # 1. Hash Rate 7-day change (momentum indicator)
    if 'HashRate' in df.columns:
        df['hashrate_7d_pct'] = df['HashRate'].pct_change(7, fill_method=None) * 100
        print("  ✓ hashrate_7d_pct: 7-day hash rate momentum")
        derived_count += 1
    
    # 2. Active Address Momentum
    if 'AdrActCnt' in df.columns:
        df['active_addr_7d_ma'] = df['AdrActCnt'].rolling(7).mean()
        df['active_addr_ratio'] = df['AdrActCnt'] / df['active_addr_7d_ma']
        print("  ✓ active_addr_ratio: Active addresses vs 7d MA")
        derived_count += 1
    
    # 3. Mining difficulty change (security momentum)
    if 'mining_difficulty' in df.columns:
        df['difficulty_14d_pct'] = df['mining_difficulty'].pct_change(14, fill_method=None) * 100
        print("  ✓ difficulty_14d_pct: 14-day difficulty change")
        derived_count += 1
    
    # 4. Halving metrics (partner requirement)
    df['days_since_halving'] = 0
    df['days_to_next_halving'] = 0
    
    for i, date in enumerate(df.index):
        # Find most recent halving before this date
        past_halvings = [h for h in BITCOIN_HALVINGS if h <= date]
        if past_halvings:
            last_halving = max(past_halvings)
            df.loc[date, 'days_since_halving'] = (date - last_halving).days
        
        # Find next halving after this date
        future_halvings = [h for h in BITCOIN_HALVINGS if h > date]
        if future_halvings:
            next_halving = min(future_halvings)
        else:
            next_halving = NEXT_HALVING_ESTIMATE
        df.loc[date, 'days_to_next_halving'] = (next_halving - date).days
    
    print("  ✓ days_since_halving: Days since last BTC halving")
    print("  ✓ days_to_next_halving: Days until next BTC halving")
    derived_count += 2
    
    # 5. NVT Ratio approximation (if we have market cap proxy and tx volume)
    # NVT = Network Value / Transaction Volume
    if 'CapMVRVCur' in df.columns and 'est_tx_volume_usd' in df.columns:
        # MVRV * Realized Cap approximates Market Cap, but we can use a simpler proxy
        # Using transaction volume directly for NVT-like ratio
        df['tx_volume_7d_ma'] = df['est_tx_volume_usd'].rolling(7).mean()
        print("  ✓ tx_volume_7d_ma: 7-day transaction volume MA")
        derived_count += 1
    
    print(f"\n  Total derived metrics added: {derived_count}")
    
    return df


def validate_data(df):
    """Validate the fetched data for completeness."""
    print("\n" + "="*60)
    print("DATA VALIDATION")
    print("="*60)
    
    print(f"\n  Date Range: {df.index.min().date()} to {df.index.max().date()}")
    print(f"  Total Rows: {len(df)}")
    print(f"  Total Columns: {len(df.columns)}")
    
    # Check for missing values
    print("\n  Missing Values (showing only columns with >0 NaN):")
    has_missing = False
    for col in df.columns:
        nan_count = df[col].isna().sum()
        if nan_count > 0:
            print(f"    • {col}: {nan_count} ({nan_count/len(df)*100:.1f}%)")
            has_missing = True
    
    if not has_missing:
        print("    None - all data complete!")
    
    return df


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main function to fetch and process on-chain data."""
    print("\n" + "#"*60)
    print("# ON-CHAIN DATA EXTRACTION (MULTI-SOURCE)")
    print(f"# Period: {START_DATE} to {END_DATE}")
    print("#"*60)
    
    start_time = time.time()
    
    try:
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # 1. Fetch from CoinMetrics
        coinmetrics_df = fetch_coinmetrics_data()
        
        # 2. Fetch from Blockchain.com
        blockchain_df = fetch_blockchain_data()
        
        # 3. Merge both datasets
        print("\n" + "="*60)
        print("MERGING DATA SOURCES")
        print("="*60)
        
        if not blockchain_df.empty:
            # Blockchain.com provides sparse data (every ~4 days), so we need to:
            # 1. Filter to CoinMetrics date range
            # 2. Reindex to CoinMetrics dates with forward fill
            
            print(f"  Blockchain.com data: {len(blockchain_df)} rows, index type: {blockchain_df.index.dtype}")
            print(f"  CoinMetrics data: {len(coinmetrics_df)} rows, index type: {coinmetrics_df.index.dtype}")
            
            # Filter to match CoinMetrics date range
            blockchain_df = blockchain_df[blockchain_df.index >= coinmetrics_df.index.min()]
            blockchain_df = blockchain_df[blockchain_df.index <= coinmetrics_df.index.max()]
            print(f"  After filtering: {len(blockchain_df)} rows")
            
            # Reindex to CoinMetrics dates and forward fill, then backward fill any remaining
            blockchain_df = blockchain_df.reindex(coinmetrics_df.index, method='ffill')
            blockchain_df = blockchain_df.bfill()  # Fill any NaN at the start
            print(f"  After reindex+ffill+bfill: {blockchain_df.notna().sum().sum()} non-null values")
            
            # Join on date index
            df = coinmetrics_df.join(blockchain_df, how='left')
            print(f"  ✓ Merged {len(coinmetrics_df.columns)} CoinMetrics + {len(blockchain_df.columns)} Blockchain.com columns")
        else:
            df = coinmetrics_df
            print("  ⚠ Using CoinMetrics data only (Blockchain.com failed)")
        
        # 4. Compute derived metrics
        df = compute_derived_metrics(df)
        
        # 5. Validate data
        df = validate_data(df)
        
        # 6. Save to CSV
        df.to_csv(OUTPUT_FILE)
        
        # Final summary
        elapsed = time.time() - start_time
        print("\n" + "="*60)
        print("ON-CHAIN DATA EXTRACTION COMPLETE!")
        print("="*60)
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"  Saved to: {OUTPUT_FILE}")
        print(f"  Execution time: {elapsed:.1f} seconds")
        
        print("\nColumns:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2}. {col}")
        
        return df
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("  1. Check your internet connection")
        print("  2. Verify API endpoints are accessible")
        raise


if __name__ == "__main__":
    onchain_df = main()
