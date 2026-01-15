import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests, adfuller

# Configuration
MAX_LAG = 14  # We test up to 2 weeks of lag
SIGNIFICANCE_LEVEL = 0.05

def check_stationarity(series):
    """
    Granger Causality requires stationary data (no trend).
    We use the ADF test to check.
    """
    result = adfuller(series.dropna())
    return result[1] < 0.05  # Returns True if stationary

def run_granger_test(df, cause, effect):
    """
    Tests if 'cause' Granger-causes 'effect'.
    Returns the minimum p-value found across lags.
    """
    # 1. Check Stationarity
    if not check_stationarity(df[cause]) or not check_stationarity(df[effect]):
        # If not stationary, take 1st difference
        data = df[[effect, cause]].diff().dropna()
    else:
        data = df[[effect, cause]]
        
    # 2. Run Test
    # verbose=False suppresses the massive text output
    try:
        test_result = grangercausalitytests(data, maxlag=MAX_LAG, verbose=False)
        
        # Extract p-values for the F-test (ssr_ftest)
        p_values = [test_result[i+1][0]['ssr_ftest'][1] for i in range(MAX_LAG)]
        min_p_value = min(p_values)
        best_lag = p_values.index(min_p_value) + 1
        
        return min_p_value, best_lag
    except Exception as e:
        print(f"  Error testing {cause} -> {effect}: {e}")
        return 1.0, 0

try:
    print("--- Loading Data ---")
    df = pd.read_csv('../../../data/processed/Three_Pillars_Dataset.csv', index_col=0, parse_dates=True)
    
    # Define our Key Nodes (from MDA)
    nodes = {
        'Fundamental': ['HashRate', 'total_stablecoin_mcap', 'AdrActCnt', 'CapMVRVCur'],
        'Sentiment': ['BlackRock Bitcoin', 'Coinbase'],
        'Macro': ['CESIJPY', 'CESIUSD'],
        'Target': ['XBTUSD']
    }
    
    # Generate Pairs to Test
    print("\n--- Running Granger Causality Tests (Directionality) ---")
    print(f"Testing lags up to {MAX_LAG} days...\n")
    
    arrows = []
    
    # 1. Test Hypothesis: Drivers -> Price
    for category, features in nodes.items():
        if category == 'Target': continue
        
        for feature in features:
            # Forward: Does Feature -> Price?
            p_val_fwd, lag_fwd = run_granger_test(df, feature, 'XBTUSD')
            
            # Reverse: Does Price -> Feature? (To check for feedback loops)
            p_val_rev, lag_rev = run_granger_test(df, 'XBTUSD', feature)
            
            is_fwd_sig = p_val_fwd < SIGNIFICANCE_LEVEL
            is_rev_sig = p_val_rev < SIGNIFICANCE_LEVEL
            
            if is_fwd_sig and not is_rev_sig:
                print(f"[ARROW FOUND] {feature} -> Price (Lag: {lag_fwd} days, p={p_val_fwd:.4f})")
                arrows.append((feature, 'Price'))
            elif is_rev_sig and not is_fwd_sig:
                print(f"[REVERSE] Price -> {feature} (Lag: {lag_rev} days, p={p_val_rev:.4f})")
                arrows.append(('Price', feature))
            elif is_fwd_sig and is_rev_sig:
                print(f"[FEEDBACK LOOP] {feature} <-> Price (Bidirectional)")
                arrows.append((feature, 'Price'))
                arrows.append(('Price', feature))
            else:
                print(f"[NO LINK] {feature} --x-- Price")

    print("\n--- Final Causal Arrow List ---")
    for u, v in arrows:
        print(f"{u} --> {v}")

except Exception as e:
    print(f"\nFATAL ERROR: {e}")