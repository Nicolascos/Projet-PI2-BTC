import pandas as pd
import numpy as np

def process_macro_data(file_path):
    print("  Processing Macro Data...")
    df = pd.read_csv(file_path)
    
    # 1. Filter for Closing Prices only ('px_last')
    df = df[df['Variable'] == 'px_last'].copy()
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # FIX: Handle Duplicates
    df = df.drop_duplicates(subset=['Date', 'Ticker'])
    
    # 2. Create Pivot Table
    pivot_df = df.pivot(index='Date', columns='Ticker', values='Value')
    
    # 3. Clean Column Names
    pivot_df.columns = [col.split()[0].replace('^', '').upper() for col in pivot_df.columns]
    
    # 4. Standardize Index to UTC
    if pivot_df.index.tz is None:
        pivot_df.index = pivot_df.index.tz_localize('UTC')
    else:
        pivot_df.index = pivot_df.index.tz_convert('UTC')
        
    return pivot_df

def load_and_prep_dataset(file_path, name):
    print(f"  Processing {name} Data...")
    df = pd.read_csv(file_path)
    
    # FIX: Robust Date Column Detection
    # 1. Look for 'date' (case insensitive)
    date_cols = [c for c in df.columns if 'date' in c.lower()]
    
    if date_cols:
        date_col = date_cols[0]
    # 2. Look for 'Unnamed: 0' which often holds the index
    elif 'Unnamed: 0' in df.columns:
        date_col = 'Unnamed: 0'
    else:
        raise ValueError(f"Could not find a date column in {name} dataset. Columns: {df.columns.tolist()}")

    print(f"    Using '{date_col}' as date column.")
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    
    # Standardize Index to UTC
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')
    else:
        df.index = df.index.tz_convert('UTC')
        
    return df

try:
    print("--- STARTING FINAL MERGE ---")
    
    # 1. Load and Process All 3 Pillars
    # Note: Ensure these paths match exactly where your files are located
    macro_df = process_macro_data('../../data/processed/clean_bitcoin_macro_dataset.csv')
    onchain_df = load_and_prep_dataset('../../data/processed/onchain_data_complete.csv', 'On-Chain')
    sentiment_df = load_and_prep_dataset('../../data/processed/sentiment_dataset.csv', 'Sentiment')
    
    # 2. Merge Strategy
    print("\n  Merging datasets...")
    
    # Merge On-Chain + Sentiment first
    merged_df = pd.merge(onchain_df, sentiment_df, left_index=True, right_index=True, how='inner')
    
    # Merge Macro
    # Forward-fill macro data to ensure we have values for weekends
    macro_df = macro_df.resample('D').ffill()
    
    final_df = pd.merge(merged_df, macro_df, left_index=True, right_index=True, how='inner')
    
    # 3. Final Cleaning
    final_df = final_df.dropna(axis=1, how='all')
    final_df = final_df.fillna(method='ffill')
    final_df = final_df.dropna()
    
    # 4. Save
    output_filename = '../../data/processed/Three_Pillars_Dataset.csv'
    final_df.to_csv(output_filename)
    
    print(f"\nSUCCESS! Master dataset saved to '{output_filename}'")
    print(f"Shape: {final_df.shape}")
    print(f"Date Range: {final_df.index.min()} to {final_df.index.max()}")
    print(f"Total Features: {len(final_df.columns)}")
    print("\nColumns Sample:")
    print(list(final_df.columns[:10]))

except Exception as e:
    print(f"\nFATAL ERROR: {e}")
    import traceback
    traceback.print_exc()