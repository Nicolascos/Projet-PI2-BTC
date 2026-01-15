"""Validate the sentiment dataset for completeness."""
import pandas as pd

# Load existing data
df = pd.read_csv('../../data/processed/sentiment_dataset.csv', index_col=0, parse_dates=True)

# Expected keywords
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
ALL_KEYWORDS = [kw for group in KEYWORDS_LIST for kw in group]

print('='*60)
print('SENTIMENT DATASET VALIDATION')
print('='*60)

# Check date range
print(f'\nDate Range: {df.index.min()} to {df.index.max()}')
print(f'Total rows: {len(df)}')
print(f'Total columns: {len(df.columns)}')

# Check which keywords exist
existing_keywords = [col for col in df.columns if col in ALL_KEYWORDS]
missing_keywords = [kw for kw in ALL_KEYWORDS if kw not in df.columns]

print(f'\nKeywords found: {len(existing_keywords)}/50')

if missing_keywords:
    print(f'\nMISSING KEYWORDS ({len(missing_keywords)}):')
    for kw in missing_keywords:
        print(f'  - {kw}')
else:
    print('\nAll 50 keywords present!')

# Check for NaN values in keyword columns
print('\nKeyword columns with NaN values:')
nan_cols = []
for col in existing_keywords:
    nan_count = df[col].isna().sum()
    if nan_count > 0:
        nan_cols.append((col, nan_count))
        print(f'  - {col}: {nan_count} NaN rows')

if not nan_cols:
    print('  None - all keyword data is complete!')

# Check non-keyword columns
other_cols = [c for c in df.columns if c not in ALL_KEYWORDS]
print(f'\nOther columns ({len(other_cols)}): {other_cols}')

# Check for NaN in other columns
print('\nOther columns with NaN values:')
for col in other_cols:
    nan_count = df[col].isna().sum()
    if nan_count > 0:
        print(f'  - {col}: {nan_count} NaN rows')
