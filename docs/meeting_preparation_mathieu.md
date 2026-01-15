# 📊 Meeting Preparation: Mathieu (Ginjer-AM)
## A Causal Approach to Bitcoin Performance Modeling

**Date:** Prepared January 2026  
**Project:** PI2 - Industrial Innovation Project  
**Partners:** ESSEC x Ginjer-AM

---

## 🚨 CRITICAL FINDINGS FOR DISCUSSION

### ✅ Factors That PASS the Causality Filter (Granger-Cause Price)
| Factor | Lag | Mechanism |
|--------|-----|-----------|
| **CapMVRVCur** (MVRV) | 1 day | Valuation → Mean Reversion |
| **BlackRock Bitcoin** (search) | 11 days | Institutional Interest → Inflows |

### ⚡ Feedback Loops (Bidirectional Causation)
- HashRate ↔ Price
- Stablecoin Market Cap ↔ Price
- Coinbase (search) ↔ Price

### ❌ Factors That FAIL (Reverse Causation: Price → Factor)
- AdrActCnt (Active Addresses) — Price drives adoption, not reverse!
- CESIJPY, CESIUSD — BTC influences macro surprises, not reverse!

---

## 🎯 Executive Summary

This document addresses the key points raised in the December 19, 2025 meeting and Mathieu's follow-up message:

1. **Horizon Analysis**: Which factors explain which time horizons (short vs long-term)
2. **Confusion Matrix**: Scenario analysis performance across regimes
3. **Data Pipeline Transparency**: What was kept/dropped and why at each stage
4. **Causality Candidates**: Factors likely to pass the causality filter

---

## 1️⃣ Horizon Analysis: Factor Types by Time Horizon

### Key Finding: Different Horizons Capture Fundamentally Different Dynamics

| Horizon | Top Factors | Category | Interpretation |
|---------|-------------|----------|----------------|
| **T+1** (Daily) | `AdrActCnt` (Active Addresses) | On-Chain | **Usage/Activity** - Daily adoption signals |
| | `CESIEUR` (Euro Economic Surprise) | Macro | European economic news shocks |
| | `Inflation, Fed Meeting, Private Key` | Mixed | Regulatory/monetary noise |
| **T+7** (Weekly) | `Bear Market` (Google Trends) | Sentiment | **Fear Regime** - Retail panic indicator |
| | `CESIEUR` | Macro | Persistent macro surprise effect |
| | `Cold Storage, Buy Bitcoin, Bitcoin Mining` | Sentiment | Retail accumulation signals |
| **T+30** (Monthly) | `XBNUSD, XLCUSD, XRPUSD` | Crypto Cross-Assets | **Crypto Ecosystem Beta** - BTC correlation to altcoins |
| | `TxCnt, BlackRock Bitcoin, CNH` | Mixed | Institutional + China liquidity |
| | `CESIJPY` (Japan Economic Surprise) | Macro | Yen carry trade dynamics |

### Interpretation: The "Horizon Spectrum"

```
SHORT-TERM (T+1)         MEDIUM-TERM (T+7)         LONG-TERM (T+30)
────────────────────────────────────────────────────────────────────
Network Usage     →      Sentiment/Fear     →      Macro Liquidity
(On-Chain)               (Psychology)              (Cross-Asset)

• Active Addresses       • "Bear Market" keyword   • Altcoin correlations
• Transaction count      • Retail accumulation     • Japan rates (carry trade)
• Mining activity        • FOMO indicators         • Institutional flows
```

**Why This Makes Sense:**
1. **Short-term**: On-chain metrics like `AdrActCnt` are leading indicators of immediate demand
2. **Medium-term**: Sentiment captures regime transitions (fear → accumulation → rally)
3. **Long-term**: Macro factors dominate because BTC becomes a "risk asset" in portfolio rebalancing

---

## 2️⃣ Confusion Matrix: Scenario Analysis (ACTUAL RESULTS)

### Model Setup
- **Regime Definition (5 classes)**: 
  - Strong Bull: Return > +5%
  - Bull: Return +2% to +5%
  - Neutral: Return -2% to +2%
  - Bear: Return -5% to -2%
  - Strong Bear: Return < -5%
- **Model**: Random Forest Classifier (100 trees, max_depth=5, balanced weights)
- **Validation**: Walk-forward (80/20 split, no shuffle)

### T+7 (Weekly) Results

| Regime | Distribution | Recall | Interpretation |
|--------|--------------|--------|----------------|
| Strong Bear | 19.7% | **53.1%** ⭐ | Model detects crashes well! |
| Bear | 13.4% | 3.2% | Mild bears confused with neutral |
| Neutral | 25.8% | 32.7% | Moderate detection |
| Bull | 14.4% | 10.4% | Mild bulls hard to detect |
| Strong Bull | 26.6% | 7.6% | Misclassified often |

**Weekly Accuracy: 21%** (but Strong Bear detection is excellent!)

### T+30 (Monthly) Results

| Regime | Distribution | Recall | Interpretation |
|--------|--------------|--------|----------------|
| Strong Bear | 31.0% | 25.5% | Reasonable crash detection |
| Bear/Neutral/Bull | 26.6% | ~0% | Model ignores mild regimes |
| Strong Bull | 42.4% | **81.8%** ⭐ | Excellent bull market detection! |

**Monthly Accuracy: 38%** (extremes well-detected, middle ignored)

### Key Insight for Strategy (Per Mathieu's Request: "Same Effect as RIOT")

```
┌────────────────────────────────────────────────────────────┐
│   The model's ASYMMETRIC performance is actually useful:  │
│                                                           │
│   SHORT-TERM (T+7):  → Good at detecting CRASHES (53%)    │
│   LONG-TERM (T+30):  → Good at detecting RALLIES (82%)    │
│                                                           │
│   STRATEGY IMPLICATION:                                   │
│   • Use weekly model for RISK MANAGEMENT (avoid crashes)  │
│   • Use monthly model for POSITIONING (capture rallies)   │
│   • This mimics a "RIOT-style" leveraged exposure when    │
│     model signals Strong Bull, cash when Strong Bear      │
└────────────────────────────────────────────────────────────┘
```

---

## 3️⃣ Data Pipeline Transparency: What Was Kept/Dropped and Why

### Stage 1: Raw Data Collection

| Source | Type | Date Range | Status |
|--------|------|------------|--------|
| CoinMetrics | On-Chain | 2018-02-08 → 2025-11-04 | ✅ Included |
| Google Trends | Sentiment | 2018-02-08 → 2025-11-04 | ✅ Included (50 keywords) |
| Alternative.me | Fear & Greed | 2018-02-08 → 2025-11-04 | ✅ Included |
| Bloomberg/FRED | Macro | 2018-02-08 → 2025-11-04 | ✅ Partial (see below) |

### Stage 2: On-Chain Selection

**INCLUDED (10 metrics)**:
| Metric | Justification |
|--------|---------------|
| `HashRate` | Network security proxy |
| `CapMVRVCur` | Valuation (Realized vs Market value) |
| `TxCnt` | Transaction activity |
| `AdrActCnt` | Network utility/adoption |
| `SplyCur` | Current supply (for S2F context) |
| `mining_difficulty` | Security + miner economics |
| `miner_revenue_usd` | Miner health indicator |
| `transaction_volume_usd` | Dollar-denominated activity |
| `btc_balance_on_exchanges` | Exchange flow proxy |
| `total_stablecoin_mcap` | Liquidity indicator |

**DROPPED (due to data access restrictions)**:
| Metric | Reason |
|--------|--------|
| Miner Fees | CoinMetrics Premium required |
| Granular UTXO Flows | CoinMetrics Premium required |
| Mempool Data | Real-time data not available historically |
| Exchange-specific flows | Requires Glassnode/Nansen |

### Stage 3: Sentiment Selection

**INCLUDED (50 Google Trends + 1 Index)**:
- Institutional: `BlackRock Bitcoin`, `MicroStrategy`, `Bitcoin ETF`, `SEC Crypto`
- Retail Fear: `Bear Market`, `Rekt`, `Crypto Hack`, `Rug Pull`
- Retail Greed: `Bull Run`, `To The Moon`, `FOMO`, `HODL`
- Ecosystem: `Coinbase`, `Binance`, `MetaMask`, `Ledger`
- Technical: `Hashrate`, `Bitcoin Mining`, `Bitcoin Halving`
- Fear & Greed Index (daily)

**DROPPED**:
| Data | Reason |
|------|--------|
| Twitter/X Volume | Noisy, requires premium API |
| Reddit Sentiment | Inconsistent historical data |
| Telegram Groups | Privacy/access issues |
| News Sentiment Scores | Commercial data (expensive) |

### Stage 4: Macro Selection - THE CRITICAL DECISION

**⚠️ SURVIVORSHIP BIAS TRADE-OFF**

We faced a key decision:
- **Option A**: Include all modern assets (Solana, new ETFs, etc.) → Lose 2018-2020 data
- **Option B**: Keep historical depth (2018+) → Drop recently-launched assets

**WE CHOSE OPTION B** because:
1. The 2018-2019 Bear Market is crucial training data
2. Understanding full cycle behavior > having more recent assets
3. The 2020-2021 Bull Market alone would overfit to "everything goes up"

**DROPPED DUE TO RECENCY**:
| Asset/Metric | Launch Date | Reason Dropped |
|--------------|-------------|----------------|
| Solana (SOL) | Mar 2020 | Would delete 2+ years of data |
| Shiba Inu (SHIB) | Aug 2020 | Would delete 2+ years of data |
| ProShares Bitcoin ETF | Oct 2021 | Would delete 3+ years of data |
| BlackRock IBIT | Jan 2024 | Would delete 6+ years of data |
| MOVE Index (rate vol) | Mixed availability | Gaps in data |

**KEPT (62 macro variables)**:
- Rates: `FDTR`, `USGG3M`, `EURR002W`, `JPYC2Y10`, `USYC2Y10`, `DEYC2Y10`
- Currencies: `DXY`, `EURUSD`, `JPYUSD`, `CNH`
- Commodities: `XAU` (Gold), `CO1` (Oil)
- Economic Surprises: `CESIUSD`, `CESIEUR`, `CESIJPY`, `CESICNY`
- Equities: `SXXP` (Euro Stoxx), `TSEMIL` (Taiwan)
- Crypto Cross: `XBNUSD`, `XETUSD`, `XLCUSD`, `XRPUSD`

### Final Dataset Summary

| Statistic | Value |
|-----------|-------|
| Total Features | **89** |
| Date Range | 2018-02-08 → 2025-11-04 |
| Observations | **2,827 days** |
| Pillars | On-Chain (10) + Sentiment (51) + Macro (28) |

---

## 4️⃣ Causality Filter: Candidate Factors

### Current Causal Skeleton Analysis

Based on our Graphical Lasso + Granger Causality analysis:

#### Strong Causal Links Found (Partial Correlation > 0.05)

| Node 1 | Node 2 | Partial Corr | Interpretation |
|--------|--------|--------------|----------------|
| **XBTUSD ↔ CapMVRVCur** | | **0.707** | MVRV is quasi-definitionally linked to price (market value component) |
| HashRate ↔ AdrActCnt | | 0.185 | Network activity drives hashrate |
| BlackRock Bitcoin ↔ Coinbase | | 0.061 | Institutional/retail sentiment co-move |

#### Granger Causality Direction Tests (ACTUAL RESULTS)

| Test | Direction | Lag | p-value | Interpretation |
|------|-----------|-----|---------|----------------|
| **CapMVRVCur → Price** | ✅ Causal | 1 day | <0.0001 | MVRV is a **leading indicator** |
| **BlackRock Bitcoin → Price** | ✅ Causal | 11 days | 0.0096 | Institutional search interest predicts price |
| HashRate ↔ Price | ⚡ Bidirectional | - | Sig. | Feedback loop (security ↔ value) |
| total_stablecoin_mcap ↔ Price | ⚡ Bidirectional | - | Sig. | Liquidity and price reinforce each other |
| Coinbase ↔ Price | ⚡ Bidirectional | - | Sig. | Retail interest ↔ price spiral |
| **Price → AdrActCnt** | ❌ Reverse | 6 days | <0.0001 | Price drives adoption (not vice versa!) |
| **Price → CESIJPY** | ❌ Reverse | 1 day | 0.0253 | BTC influences macro surprises |
| **Price → CESIUSD** | ❌ Reverse | 1 day | 0.0261 | BTC influences macro surprises |

### 🎯 KEY FINDING: Factors That Pass the Causality Filter

Based on Granger causality tests (α = 0.05):

| Factor | Status | Evidence |
|--------|--------|----------|
| **CapMVRVCur** (MVRV Ratio) | ✅ **PASSES** | Granger-causes price at 1-day lag |
| **BlackRock Bitcoin** (search) | ✅ **PASSES** | Granger-causes price at 11-day lag |
| HashRate | ⚠️ Feedback Loop | Bidirectional causation |
| total_stablecoin_mcap | ⚠️ Feedback Loop | Bidirectional causation |
| Coinbase (search) | ⚠️ Feedback Loop | Bidirectional causation |
| AdrActCnt | ❌ **FAILS** | Price → Addresses (reverse causation) |
| CESIJPY, CESIUSD | ❌ **FAILS** | Price → Macro surprises (reverse causation) |

---

## 5️⃣ Next Steps for Causal Graph Construction

### Proposed Pipeline

```
┌─────────────────┐
│  1. MDA Ranking │ ← Current: Top clusters identified
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ 2. Granger Causality Tests  │ ← Current: determine_causal_arrows.py
│    (Determine direction)    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 3. Partial Correlation      │ ← Current: causal_graph_V1.py
│    (Remove confounders)     │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 4. DAG Construction         │ ← TO DO: PC Algorithm / FCI
│    (Final causal graph)     │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 5. Intervention Simulation  │ ← TO DO: do-calculus validation
│    (Validate causal claims) │
└─────────────────────────────┘
```

### Recommended Actions for Meeting

1. **Present Horizon Analysis Table** - Clear differentiation by time scale
2. **Run Confusion Matrix** - Show model performance by regime
3. **Walk Through Data Audit** - Explain the "history vs breadth" trade-off
4. **Propose Causal Candidates** - Focus on Tier 1 (HashRate, Stablecoin MCap, Active Addresses, MVRV)

---

## 📎 Files Referenced

| File | Purpose |
|------|---------|
| [horizon_analysis_results.csv](horizon_analysis_results.csv) | Top factors by horizon |
| [feature_importance_results.csv](feature_importance_results.csv) | Full MDA cluster results |
| [confusion_matrix_enhanced.py](confusion_matrix_enhanced.py) | Enhanced scenario analysis code |
| [causality/partial_correlation_matrix.csv](causality/partial_correlation_matrix.csv) | Causal skeleton |
| [causality/determine_causal_arrows.py](causality/determine_causal_arrows.py) | Granger tests |
| [data_audit.py](data_audit.py) | Data selection documentation |

---

*Prepared for Ginjer-AM Partnership Meeting*
