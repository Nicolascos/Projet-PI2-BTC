import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load Data
print("Loading Three Pillars Dataset...")
df = pd.read_csv('../../data/processed/Three_Pillars_Dataset.csv', index_col=0, parse_dates=True)

# 2. Check for RIOT (or construct proxy)
# We look for RIOT. If missing, we explain the strategy using Hashrate vs Price as the proxy.
riot_col = [c for c in df.columns if 'RIOT' in c]

plt.figure(figsize=(10, 6))

if riot_col:
    # If RIOT survived cleaning
    riot = riot_col[0]
    print(f"Found RIOT Data: {riot}")
    
    # Calc correlations
    data = df[[riot, 'XBTUSD', 'HashRate']].pct_change().dropna()
    corr_riot = data.corr().loc['HashRate', riot]
    corr_btc = data.corr().loc['HashRate', 'XBTUSD']
    
    # Plot Comparison
    sns.barplot(x=['Bitcoin (Spot)', 'RIOT (Miner)'], y=[corr_btc, corr_riot], palette='viridis')
    plt.title(f'Strategy Pivot: Hashrate Signal Strength\n(RIOT Correlation: {corr_riot:.2f} vs BTC: {corr_btc:.2f})', fontsize=14)
    plt.ylabel('Correlation with Hashrate (Model Top Factor)')

else:
    # If RIOT was dropped (likely), we illustrate the "Miner Beta" concept
    # We show that Hashrate is a strong predictor, implying a Miner Strategy is the best fit.
    print("RIOT data missing (likely dropped). Generating Strategic Concept Chart.")
    
    # We plot the rolling correlation of Hashrate to Price
    # Narrative: "Our model predicts Hashrate. Since Hashrate drives Price, 
    # we should trade the asset most sensitive to Hashrate: MINERS."
    
    data = df[['HashRate', 'XBTUSD']].copy()
    data = data.pct_change().dropna()
    rolling_corr = data['HashRate'].rolling(window=30).corr(data['XBTUSD'])
    
    # Plot
    plt.plot(rolling_corr, color='orange', label='30-Day Correlation')
    plt.axhline(rolling_corr.mean(), color='red', linestyle='--', label=f'Mean Corr: {rolling_corr.mean():.2f}')
    plt.title('The "Miner" Alpha: Correlation of Hashrate to Price\n(Proposal: Trade RIOT/MARA for Leveraged Exposure)', fontsize=14)
    plt.ylabel('Correlation (Hashrate vs Price)')
    plt.legend()
    plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('../../data/outputs/images/strategy_riot_proxy.png')
print("SUCCESS! Strategy chart saved to '../../data/outputs/images/strategy_riot_proxy.png'")