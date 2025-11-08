import pandas as pd
from coinmetrics.api_client import CoinMetricsClient

client = CoinMetricsClient()

# Metrics to Fetch
metrics = [
    "CapMVRVCur", # We use "Market Cap MVRV, Current" as "MVRV" is not available on the free Coin Metrics Community API
    "NVTAdj", # Adjusted NVT is a better measure
    "HashRate", # Hash Rate
    "DiffMean", # Mean mining difficulty
    "TxCnt", # Transaction Count
    "AdrActCnt", # Active Address Count
    "RevUSD" # Miner Revenue in USD
]

# Date Range: from 2015-01-01 to today
start_date = "2015-01-01"
# Get current date and format it as YYYY-MM-DD
end_date = pd.to_datetime('today').strftime('%Y-%m-%d')

print("Fetching on-chain data from Coin Metrics...")

try:
    # Fetch all metrics in a single API call
    asset_metrics = client.get_asset_metrics(
        assets='btc', # Bitcoin
        metrics=metrics,
        frequency="1d", # 1-day frequency
        start_time=start_date,
        end_time=end_date,
        # The page size can be increased to make fewer API calls
        page_size=10000
    )

    # Data Processing
    master_df = asset_metrics.to_dataframe()
    
    # Use reset_index() to convert the multi-index into columns
    master_df = master_df.reset_index()
    
    # Ensure the 'time' column is in datetime format
    master_df['time'] = pd.to_datetime(master_df['time'])
    
    # Set the 'time' column as the new index
    master_df = master_df.set_index('time')
    
    # Drop the redundant 'asset' column
    master_df = master_df.drop(columns='asset')
    
    # Rename the index for clarity
    master_df.index.name = 'date'
    
    print("\nSuccessfully fetched and combined data!")
    print("Shape of the final DataFrame:", master_df.shape)
    print("\nFirst 5 rows:")
    print(master_df.head())
    
    # Save to a CSV file
    master_df.to_csv('onchain_data_coinmetrics.csv')
    print(f"\nData saved to onchain_data_coinmetrics.csv")

except Exception as e:
    print(f"\nAn error occurred: {e}")
    print("Please check the metric names and your network connection.")