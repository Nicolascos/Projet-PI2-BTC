"""
Sentiment Data Extraction for Bitcoin Performance Modeling

This script fetches and combines sentiment data from multiple sources:
1. Fear & Greed Index (Alternative.me API)
2. On-Chain Metrics (CoinMetrics Free API)
3. Google Trends (50 keywords via pytrends)

Output: Weekly sentiment dataset saved to data/processed/sentiment_dataset.csv
"""

import pandas as pd
import requests
import time
import random
from datetime import datetime
from pathlib import Path
from coinmetrics.api_client import CoinMetricsClient
from pytrends.request import TrendReq

# CONFIGURATION
START_DATE = "2018-02-01"
END_DATE = datetime.now().strftime('%Y-%m-%d')
RESAMPLE_FREQ = 'W-SUN'  # Weekly, ending on Sunday
# Path relative to project root: src/data_ingestion -> ../../data/processed
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "sentiment_dataset.csv"

# Set to True to skip Google Trends fetching and use existing data
# (useful when Google rate-limits your IP)
USE_EXISTING_TRENDS = True

# All 50 Google Trends keywords (10 groups of 5)
KEYWORDS_LIST = [
    ['Bitcoin', 'Crypto', 'Buy Bitcoin', 'Altcoin', 'HODL'],
    ['Bull Run', 'Bear Market', 'To The Moon', 'Rekt', 'FOMO'],
    ['Ethereum', 'Tether', 'USDC', 'Solana', 'XRP'],
    ['Binance', 'Coinbase', 'Kraken', 'Metamask', 'Ledger'],
    ['Trezor', 'Trust Wallet', 'Uniswap', 'PancakeSwap', 'Cold Storage'],
    ['BlackRock Bitcoin', 'Bitcoin ETF', 'SEC Crypto', 'Gary Gensler', 'MicroStrategy'],
    ['Inflation', 'Recession', 'Interest Rates', 'Fed Meeting', 'Banking Crisis'],
    ['Bitcoin Mining', 'Hashrate', 'Bitcoin Halving', 'Satoshi Nakamoto', 'Blockchain'],
    ['Crypto Hack', 'Rug Pull', 'Private Key', 'Seed Phrase', 'Crypto Tax'],
    ['Elon Musk Bitcoin', 'Michael Saylor', 'Vitalik Buterin', 'PlanB', 'Cathie Wood']
]

# Flat list of all keywords for validation
ALL_KEYWORDS = [kw for group in KEYWORDS_LIST for kw in group]

# Stablecoins for total market cap calculation
STABLECOINS = ['usdt', 'usdc', 'dai', 'tusd', 'busd']

# HELPER FUNCTIONS

def fetch_with_retry(func, max_retries=3, base_delay=60):
    """Execute a function with exponential backoff retry logic."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            delay = base_delay * (2 ** attempt) + random.uniform(0, 10)
            print(f"  Attempt {attempt + 1} failed: {e}. Retrying in {delay:.0f}s...")
            time.sleep(delay)


def fetch_fear_and_greed_index():
    """
    Fetch Fear & Greed Index from Alternative.me API.
    This is the standard free source for crypto sentiment.
    Returns daily data resampled to weekly.
    """
    print("\n" + "="*60)
    print("1. FETCHING FEAR & GREED INDEX (Alternative.me)")
    print("="*60)
    
    fng_url = "https://api.alternative.me/fng/?limit=0&format=json"
    
    def fetch():
        res = requests.get(fng_url, timeout=30)
        res.raise_for_status()
        return res.json()['data']
    
    fng_data = fetch_with_retry(fetch)
    
    # Process data
    fng_df = pd.DataFrame(fng_data)
    fng_df['date'] = pd.to_datetime(pd.to_numeric(fng_df['timestamp']), unit='s')
    fng_df = fng_df.set_index('date').sort_index()
    fng_df = fng_df[['value']].copy()
    fng_df.columns = ['fear_and_greed']
    fng_df['fear_and_greed'] = pd.to_numeric(fng_df['fear_and_greed'])
    
    # Localize to UTC and resample to weekly
    fng_df.index = fng_df.index.tz_localize('UTC')
    fng_df_weekly = fng_df.resample(RESAMPLE_FREQ).mean(numeric_only=True)
    
    print(f"  ✓ Retrieved {len(fng_df)} daily records")
    print(f"  ✓ Resampled to {len(fng_df_weekly)} weekly records")
    print(f"  ✓ Date range: {fng_df.index.min().date()} to {fng_df.index.max().date()}")
    
    return fng_df_weekly


def fetch_onchain_metrics():
    """
    Fetch on-chain sentiment metrics from CoinMetrics (free tier).
    
    Metrics:
    - BTC Supply on Exchanges (SplyExNtv): Indicates selling pressure
    - Total Stablecoin Market Cap: Dry powder / buying power indicator
    - BTC Dominance proxy: Calculated from market caps
    """
    print("\n" + "="*60)
    print("2. FETCHING ON-CHAIN METRICS (CoinMetrics)")
    print("="*60)
    
    client = CoinMetricsClient()
    
    # BTC metrics: Supply on Exchanges (free alternative to FlowExNtv)
    print("  Fetching BTC exchange balance...")
    btc_metrics_data = client.get_asset_metrics(
        assets='btc',
        metrics=['SplyExNtv', 'CapMrktCurUSD'],
        frequency="1d",
        start_time=START_DATE,
        end_time=END_DATE
    )
    btc_df = btc_metrics_data.to_dataframe()
    btc_df = btc_df.reset_index()
    btc_df['time'] = pd.to_datetime(btc_df['time'])
    btc_df = btc_df.set_index('time')
    
    # Fetch stablecoin market caps for total stablecoin supply
    print("  Fetching stablecoin market caps...")
    stable_dfs = []
    for coin in STABLECOINS:
        try:
            metrics = client.get_asset_metrics(
                assets=coin,
                metrics=['CapMrktCurUSD'],
                frequency="1d",
                start_time=START_DATE,
                end_time=END_DATE
            )
            df = metrics.to_dataframe().reset_index()
            df['time'] = pd.to_datetime(df['time'])
            df = df.set_index('time')
            df = df[['CapMrktCurUSD']].rename(columns={'CapMrktCurUSD': f'{coin}_mcap'})
            stable_dfs.append(df)
            print(f"    ✓ {coin.upper()}: {len(df)} records")
        except Exception as e:
            print(f"    ✗ {coin.upper()}: {e}")
    
    # Combine stablecoin data
    if stable_dfs:
        stablecoin_df = pd.concat(stable_dfs, axis=1)
        stablecoin_df['total_stablecoin_mcap'] = stablecoin_df.sum(axis=1)
    else:
        stablecoin_df = pd.DataFrame()
    
    # Fetch ETH for dominance calculation
    print("  Fetching ETH market cap for dominance calculation...")
    try:
        eth_metrics = client.get_asset_metrics(
            assets='eth',
            metrics=['CapMrktCurUSD'],
            frequency="1d",
            start_time=START_DATE,
            end_time=END_DATE
        )
        eth_df = eth_metrics.to_dataframe().reset_index()
        eth_df['time'] = pd.to_datetime(eth_df['time'])
        eth_df = eth_df.set_index('time')
        eth_df = eth_df[['CapMrktCurUSD']].rename(columns={'CapMrktCurUSD': 'eth_mcap'})
    except Exception as e:
        print(f"    ✗ ETH: {e}")
        eth_df = pd.DataFrame()
    
    # Combine all on-chain data
    onchain_df = btc_df[['SplyExNtv', 'CapMrktCurUSD']].copy()
    onchain_df.columns = ['btc_balance_on_exchanges', 'btc_mcap']
    
    if not stablecoin_df.empty:
        onchain_df = onchain_df.join(stablecoin_df[['total_stablecoin_mcap']], how='outer')
    
    if not eth_df.empty:
        onchain_df = onchain_df.join(eth_df, how='outer')
        # Calculate BTC dominance proxy: BTC / (BTC + ETH + Stablecoins)
        total_mcap = onchain_df['btc_mcap'] + onchain_df.get('eth_mcap', 0) + onchain_df.get('total_stablecoin_mcap', 0)
        onchain_df['btc_dominance_proxy'] = onchain_df['btc_mcap'] / total_mcap
    
    # Select final columns
    final_cols = ['btc_balance_on_exchanges', 'total_stablecoin_mcap', 'btc_dominance_proxy']
    onchain_df = onchain_df[[c for c in final_cols if c in onchain_df.columns]]
    
    # Localize and resample
    if onchain_df.index.tz is None:
        onchain_df.index = onchain_df.index.tz_localize('UTC')
    onchain_df_weekly = onchain_df.resample(RESAMPLE_FREQ).mean()
    
    print(f"  ✓ Combined on-chain data: {len(onchain_df_weekly)} weekly records")
    print(f"  ✓ Columns: {list(onchain_df_weekly.columns)}")
    
    return onchain_df_weekly


def load_existing_trends():
    """
    Load Google Trends data from existing sentiment_dataset.csv.
    This is useful when Google rate-limits your IP.
    """
    print("\n" + "="*60)
    print("3. LOADING EXISTING GOOGLE TRENDS DATA")
    print("="*60)
    
    if not OUTPUT_FILE.exists():
        print(f"  ✗ No existing file found at {OUTPUT_FILE}")
        return pd.DataFrame()
    
    try:
        existing_df = pd.read_csv(OUTPUT_FILE, index_col=0, parse_dates=True)
        
        # Extract only the keyword columns
        keyword_cols = [col for col in existing_df.columns if col in ALL_KEYWORDS]
        
        if not keyword_cols:
            print("  ✗ No Google Trends keywords found in existing file")
            return pd.DataFrame()
        
        trends_df = existing_df[keyword_cols].copy()
        
        # Ensure timezone
        if trends_df.index.tz is None:
            trends_df.index = trends_df.index.tz_localize('UTC')
        
        print(f"  ✓ Loaded {len(keyword_cols)} keywords from existing file")
        print(f"  ✓ Date range: {trends_df.index.min().date()} to {trends_df.index.max().date()}")
        print(f"  ✓ Keywords: {keyword_cols[:5]}... (and {len(keyword_cols)-5} more)")
        
        return trends_df
        
    except Exception as e:
        print(f"  ✗ Error loading existing file: {e}")
        return pd.DataFrame()


def fetch_google_trends():
    """
    Fetch Google Trends data for all 50 keywords.
    Uses adaptive rate limiting to avoid 429 errors.
    
    Note: Uses minimal pytrends configuration to avoid urllib3 compatibility issues.
    """
    print("\n" + "="*60)
    print("3. FETCHING GOOGLE TRENDS (50 Keywords)")
    print("="*60)
    
    timeframe = f'{START_DATE} {END_DATE}'
    all_trends_dfs = []
    
    for i, keywords in enumerate(KEYWORDS_LIST):
        group_num = i + 1
        print(f"\n  Group {group_num}/10: {keywords}")
        
        def fetch_group():
            # Create fresh TrendReq instance with minimal config to avoid urllib3 issues
            # Don't use retries/backoff_factor as they cause compatibility problems
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo='', gprop='')
            return pytrends.interest_over_time()
        
        try:
            trends_df = fetch_with_retry(fetch_group, max_retries=5, base_delay=120)
            
            if trends_df is not None and not trends_df.empty:
                # Remove isPartial column if present
                if 'isPartial' in trends_df.columns:
                    trends_df = trends_df.drop(columns=['isPartial'])
                all_trends_dfs.append(trends_df)
                print(f"    ✓ Retrieved {len(trends_df)} weekly records")
            else:
                print(f"    ✗ Empty response for group {group_num}")
                
        except Exception as e:
            print(f"    ✗ Failed to fetch group {group_num}: {e}")
        
        # Longer adaptive delays between requests to avoid rate limiting
        if i < len(KEYWORDS_LIST) - 1:
            delay = 90 + (i * 10) + random.uniform(10, 30)
            print(f"    Waiting {delay:.0f}s before next request...")
            time.sleep(delay)
    
    # Combine all trends dataframes
    if all_trends_dfs:
        # Merge all on date index
        combined_trends = all_trends_dfs[0]
        for df in all_trends_dfs[1:]:
            combined_trends = combined_trends.join(df, how='outer')
        
        # Localize timezone
        if combined_trends.index.tz is None:
            combined_trends.index = combined_trends.index.tz_localize('UTC')
        
        print(f"\n  ✓ Combined Google Trends: {combined_trends.shape[1]} keywords")
        print(f"  ✓ Date range: {combined_trends.index.min().date()} to {combined_trends.index.max().date()}")
        
        return combined_trends
    else:
        print("  ✗ No Google Trends data retrieved!")
        return pd.DataFrame()


def combine_all_datasets(fng_df, onchain_df, trends_df):
    """Combine all sentiment datasets into a single DataFrame."""
    print("\n" + "="*60)
    print("4. COMBINING ALL DATASETS")
    print("="*60)
    
    # Start with Fear & Greed
    sentiment_df = fng_df.copy()
    print(f"  Base (Fear & Greed): {sentiment_df.shape}")
    
    # Merge on-chain data
    if not onchain_df.empty:
        sentiment_df = sentiment_df.join(onchain_df, how='outer')
        print(f"  + On-chain metrics: {sentiment_df.shape}")
    
    # Merge Google Trends
    if not trends_df.empty:
        sentiment_df = sentiment_df.join(trends_df, how='outer')
        print(f"  + Google Trends: {sentiment_df.shape}")
    
    # Forward-fill then drop remaining NaNs
    sentiment_df = sentiment_df.ffill()
    initial_len = len(sentiment_df)
    sentiment_df = sentiment_df.dropna()
    dropped = initial_len - len(sentiment_df)
    
    if dropped > 0:
        print(f"  - Dropped {dropped} rows with NaN values")
    
    return sentiment_df


# MAIN EXECUTION

def main():
    """Main function to fetch and combine all sentiment data."""
    print("\n" + "#"*60)
    print("# SENTIMENT DATA EXTRACTION")
    print(f"# Period: {START_DATE} to {END_DATE}")
    if USE_EXISTING_TRENDS:
        print("# Mode: Using existing Google Trends data")
    else:
        print("# Mode: Fetching fresh Google Trends (may take 20+ minutes)")
    print("#"*60)
    
    start_time = time.time()
    
    try:
        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # 1. Fetch Fear & Greed Index
        fng_df = fetch_fear_and_greed_index()
        
        # 2. Fetch On-Chain Metrics
        onchain_df = fetch_onchain_metrics()
        
        # 3. Get Google Trends (50 keywords)
        if USE_EXISTING_TRENDS:
            trends_df = load_existing_trends()
            if trends_df.empty:
                print("\n  ⚠️  No existing trends data - will fetch fresh data")
                trends_df = fetch_google_trends()
        else:
            trends_df = fetch_google_trends()
        
        # 4. Combine all datasets
        sentiment_df = combine_all_datasets(fng_df, onchain_df, trends_df)
        
        # 5. Save to CSV
        sentiment_df.to_csv(OUTPUT_FILE)
        
        # Final summary
        elapsed = time.time() - start_time
        print("\n" + "="*60)
        print("SENTIMENT DATASET CREATION COMPLETE!")
        print("="*60)
        print(f"  Shape: {sentiment_df.shape[0]} rows × {sentiment_df.shape[1]} columns")
        print(f"  Date range: {sentiment_df.index.min().date()} to {sentiment_df.index.max().date()}")
        print(f"  Saved to: {OUTPUT_FILE}")
        print(f"  Execution time: {elapsed/60:.1f} minutes")
        print("\nColumns:")
        for i, col in enumerate(sentiment_df.columns, 1):
            print(f"  {i:2}. {col}")
        
        return sentiment_df
        
    except ImportError as e:
        print(f"\nImportError: {e}")
        print("Please install required libraries:")
        print("  pip install pandas requests coinmetrics-api-client pytrends")
        raise
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    sentiment_df = main()