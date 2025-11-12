import requests
import pandas as pd

try:
    print("Fetching Fear & Greed Index data from Alternative.me...")
    fng_url = "https://api.alternative.me/fng/?limit=0&format=json" # limit=0 gets all data
    res = requests.get(fng_url)
    res.raise_for_status()
    fng_data = res.json()['data']

    fng_df = pd.DataFrame(fng_data)
    fng_df['date'] = pd.to_datetime(fng_df['timestamp'], unit='s')
    fng_df = fng_df.set_index('date').sort_index()
    fng_df = fng_df[['value', 'value_classification']]
    fng_df.columns = ['fear_and_greed_index', 'fng_classification']
    fng_df['fear_and_greed_index'] = pd.to_numeric(fng_df['fear_and_greed_index'])

    # Standardize F&G index to UTC
    fng_df.index = fng_df.index.tz_localize('UTC')

    # Save to a CSV file
    fng_df.to_csv('fear_and_greed_index.csv')
    print(f"\nData saved to fear_and_greed_index.csv")
    
except Exception as e:
    print(f"\nAn error occurred: {e}")