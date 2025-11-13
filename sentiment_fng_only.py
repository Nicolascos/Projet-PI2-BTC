import pandas as pd
import requests
from datetime import datetime

START_DATE = "2018-02-01"
END_DATE = datetime.now().strftime('%Y-%m-%d')
RESAMPLE_FREQ = 'W-SUN' 

try:
    # Fetch Fear & Greed Index (daily) - NO API KEY NEEDED
    print("Fetching Fear & Greed Index data from Alternative.me...")
    fng_url = "https://api.alternative.me/fng/?limit=0&format=json"
    res = requests.get(fng_url)
    res.raise_for_status()
    fng_data = res.json()['data']
    
    fng_df = pd.DataFrame(fng_data)
    fng_df['date'] = pd.to_datetime(pd.to_numeric(fng_df['timestamp']), unit='s')
    fng_df = fng_df.set_index('date').sort_index()
    fng_df = fng_df[['value', 'value_classification']]
    fng_df.columns = ['fear_and_greed_index', 'fng_classification']
    fng_df['fear_and_greed_index'] = pd.to_numeric(fng_df['fear_and_greed_index'])
    
    # Resample to weekly
    fng_df_weekly = fng_df[['fear_and_greed_index']].resample(RESAMPLE_FREQ).mean()
    
    print("\n" + "="*60)
    print("✓ Sentiment Dataset Creation Complete!")
    print("="*60)
    print(f"Final shape: {fng_df_weekly.shape[0]} rows × {fng_df_weekly.shape[1]} columns")
    print(f"Date range: {fng_df_weekly.index.min().date()} to {fng_df_weekly.index.max().date()}")

    # Save the dataset
    fng_df_weekly.to_csv('sentiment_fng_dataset.csv')
    print(f"\n✓ Dataset saved to 'sentiment_fng_dataset.csv'")
    
    # Display preview
    print("\n--- Preview (first 10 rows) ---")
    print(fng_df_weekly.head(10))
    print("\n--- Preview (last 10 rows) ---")
    print(fng_df_weekly.tail(10))
    
    print("\n--- Summary Statistics ---")
    print(fng_df_weekly.describe())

except Exception as e:
    print(f"\n❌ An error occurred: {e}")
    import traceback
    traceback.print_exc()
