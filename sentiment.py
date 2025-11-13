import pandas as pd
import requests
from coinmetrics.api_client import CoinMetricsClient
from pytrends.request import TrendReq
from datetime import datetime

START_DATE = "2018-02-01"
END_DATE = datetime.now().strftime('%Y-%m-%d')
# Resampling frequency: 'W-SUN' means weekly, ending on Sunday.
RESAMPLE_FREQ = 'W-SUN' 

try:
    # 1. Fetch Fear & Greed Index (daily)
    print("Fetching Fear & Greed Index data from Alternative.me...")
    fng_url = "https://api.alternative.me/fng/?limit=0&format=json" # limit=0 gets all data
    res = requests.get(fng_url)
    res.raise_for_status()
    fng_data = res.json()['data']
    
    fng_df = pd.DataFrame(fng_data)
    fng_df['date'] = pd.to_datetime(pd.to_numeric(fng_df['timestamp']), unit='s')
    fng_df = fng_df.set_index('date').sort_index()
    fng_df = fng_df[['value', 'value_classification']]
    fng_df.columns = ['fear_and_greed_index', 'fng_classification']
    fng_df['fear_and_greed_index'] = pd.to_numeric(fng_df['fear_and_greed_index'])
    fng_df.index = fng_df.index.tz_localize('UTC')
    fng_df_weekly = fng_df.resample(RESAMPLE_FREQ).mean(numeric_only=True)


    # 2. Fetch On-Chain Sentiment Metrics (daily)
    print("Fetching On-Chain Sentiment from Coin Metrics...")
    client = CoinMetricsClient()
    stablecoins = ['usdt', 'usdc', 'dai', 'tusd', 'busd'] # Common stablecoins: USDT, USDC, DAI, TrueUSD, BUSD
    
    # 'FlowExNtv' is a premium metric -> we will use Supply on Exchanges instead: 'SplyExNtv'
    btc_metrics = ['SplyExNtv', 'DomBtc'] # Supply on Exchanges (Native Units) + Bitcoin Dominance
    stable_metric = ['CapMrktCurUSD'] # Current Market Cap in USD

    # Fetch BTC metrics
    btc_cm_metrics = client.get_asset_metrics(
        assets='btc', # Bitcoin
        metrics=btc_metrics,
        frequency="1d", # 1-day frequency
        start_time=START_DATE,
        end_time=END_DATE
    )
    btc_cm_df = btc_cm_metrics.to_dataframe()

    # Fetch Stablecoin metrics
    stable_dfs = []
    for coin in stablecoins:
        try:
            metrics = client.get_asset_metrics(
                assets=coin, metrics=stable_metric, frequency="1d",
                start_time=START_DATE, end_time=END_DATE
            )
            stable_dfs.append(metrics.to_dataframe())
        except Exception as e:
            print(f"  Could not fetch {coin}: {e}")

    # Combine all Coin Metrics data
    combined_cm_df = pd.concat([btc_cm_df] + stable_dfs)
    
    # Process Coin Metrics data
    onchain_df = combined_cm_df.reset_index()
    onchain_df['time'] = pd.to_datetime(onchain_df['time'])
    
    onchain_df_pivot = onchain_df.pivot(index='time', columns='asset', values=['CapMrktCurUSD', 'SplyExNtv', 'DomBtc'])
    
    onchain_df_pivot.columns = ['_'.join(col).strip() for col in onchain_df_pivot.columns.values]
    
    # Calculate stablecoin sum
    stable_cols = [f'CapMrktCurUSD_{coin}' for coin in stablecoins if f'CapMrktCurUSD_{coin}' in onchain_df_pivot.columns]
    onchain_df_pivot['stablecoin_total_marketcap'] = onchain_df_pivot[stable_cols].sum(axis=1)

    final_onchain_cols = ['SplyExNtv_btc', 'DomBtc_btc', 'stablecoin_total_marketcap']
    onchain_df_final = onchain_df_pivot[final_onchain_cols].copy()
    onchain_df_final.columns = ['btc_balance_on_exchanges_ntv', 'btc_dominance', 'stablecoin_total_marketcap']
    
    # Resample to weekly
    onchain_df_weekly = onchain_df_final.resample(RESAMPLE_FREQ).mean()


    # 3. Fetch Google Trends Data (weekly)
    print("Fetching Google Trends data...")
    pytrends = TrendReq(hl='en-US', tz=360)
    
    # Representative sample of keywords (Google limits to 5 keywords per request)
    kw_group_1 = ['Bitcoin', 'cryptomonnaie', 'blockchain', 'Binance', 'Ledger']
    kw_group_2 = ['Altcoins', 'Metamask', 'Uniswap', 'Coinbase', 'NFT'] 

    # Build the timeframe string
    timeframe = f'{START_DATE} {END_DATE}'

    # Fetch data for group 1
    pytrends.build_payload(kw_group_1, cat=0, timeframe=timeframe, geo='', gprop='')
    trends_df_1 = pytrends.interest_over_time()
    
    import time
    time.sleep(30) # Add a 30-second delay to avoid Google's rate limit
    
    # Fetch data for group 2
    pytrends.build_payload(kw_group_2, cat=0, timeframe=timeframe, geo='', gprop='')
    trends_df_2 = pytrends.interest_over_time()
    
    # Combine trends data
    trends_df = pd.merge(trends_df_1, trends_df_2, left_index=True, right_index=True, how='outer')
    if 'isPartial' in trends_df.columns:
        trends_df = trends_df.drop(columns=['isPartial_x', 'isPartial_y'])
    
    trends_df.index = trends_df.index.tz_localize('UTC') # Add UTC timezone

    # 4. Combine All Datasets
    print("Merging all sentiment datasets...")
    
    # Merge the three weekly dataframes
    sentiment_df = pd.merge(fng_df_weekly, onchain_df_weekly, left_index=True, right_index=True, how='outer')
    sentiment_df = pd.merge(sentiment_df, trends_df, left_index=True, right_index=True, how='outer')

    # Forward-fill to handle any gaps (e.g., if one source starts a week after another)
    sentiment_df = sentiment_df.fillna(method='ffill')
    sentiment_df = sentiment_df.dropna() # Drop any remaining NaNs

    # Final Output
    print("\n--- Sentiment Dataset Creation Complete! ---")
    print(f"Final shape of the sentiment DataFrame: {sentiment_df.shape}")
    print(f"Dataset date range: {sentiment_df.index.min()} to {sentiment_df.index.max()}")
    print("\nDataFrame Info:")
    sentiment_df.info()

    # Save the final sentiment dataset to a CSV file
    sentiment_df.to_csv('sentiment_dataset.csv')
    print("\n\nFinal sentiment dataset saved to 'sentiment_dataset.csv'")

except ImportError as e:
    print(f"\nImportError: {e}")
    print("Please ensure you have all required libraries installed: pip install pandas requests coinmetrics-api-client pytrends")
except Exception as e:
    print(f"\nAn error occurred: {e}")