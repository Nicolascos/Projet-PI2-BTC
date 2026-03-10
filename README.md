# A Causal Approach to Bitcoin Performance Modeling

**PI2 Industrial Innovation Project**
*ESILV x Ginjer Asset Management*

---

## Project Overview

This project applies causal inference to Bitcoin performance modeling, moving beyond correlational analysis to identify the true drivers of BTC returns. The theoretical framework combines:

- **Lopez de Prado (2023)** — *"Causal Factor Investing"*: 3-step framework (Phenomenological, Theoretical, Falsification)
- **Vaissie (2021)** — *"Bitcoin, un actif comme les autres?"*: 3-pillar categorization (On-Chain, Macro, Sentiment)

**Partner:** Mathieu Vaissie, Ginjer Asset Management

### Key Objectives

1. Identify **causal factors** (not merely correlated) driving BTC returns using 4 complementary discovery methods
2. Analyze factor importance across **time horizons** (T+1, T+7, T+30) via Clustered MDA
3. Build a **consensus causal graph** validated by DoWhy intervention tests
4. Map results to Vaissie's 3-pillar framework for investment interpretation

---

## Project Structure

```
Projet-PI2-BTC/
├── notebooks/
│   ├── CausalAnalysis.ipynb          # Main deliverable — full causal pipeline
│   ├── Analysis.ipynb                # Structured pipeline: load -> stationarity -> MDA -> classification
│   ├── BTC_V3.ipynb                  # DoWhy CausalModel + ATE estimation
│   ├── BTC_test.ipynb                # Experimental: deep learning, model comparison
│   ├── CausalityTest.ipynb           # Original research notebook (reference only)
│   ├── indicatorsMY_v02.xlsx         # Bloomberg multi-sheet data (22MB, gitignored)
│   └── causal_graph_interactive.html # Interactive pyvis graph
│
├── src/
│   ├── data_ingestion/               # API data fetchers (CoinMetrics, Google Trends)
│   ├── data_processing/              # Data cleaning & merging pipelines
│   └── analysis/
│       ├── horizon_analysis.py       # Clustered MDA across T+1/7/30 horizons
│       └── confusion_matrix_enhanced.py  # 5-class scenario classification
│
├── reports/
│   └── Causal_Analysis_Report.md     # Full report on CausalAnalysis.ipynb results
│
├── resources/                        # Reference papers
│   ├── causal-factor-investing.pdf
│   ├── Bitcoin un actif comme les autres - Mathieu Vaissie.pdf
│   └── Research_Summary_Causal_Factor_Investing.md
│
├── data/
│   ├── processed/                    # Cleaned intermediate datasets
│   └── outputs/metrics/              # MDA results, feature importance CSVs
│
└── CLAUDE.md                         # Detailed project conventions & design decisions
```

---

## Data: Three Pillars

| Pillar | Sources | Key Features | Dominant Horizon |
|--------|---------|-------------|-----------------|
| **On-Chain** | CoinMetrics, Blockchain.com | MVRV, HashRate, Mining Difficulty, TX Volume, Miner Revenue | Medium-term (weeks–months) |
| **Macro** | Bloomberg | VIX, DXY, SPX, Nasdaq, Yield Curves, M2, Fed Funds Rate | Long-term (months+) |
| **Sentiment** | Alternative.me, Google Trends | Fear & Greed, Stablecoin MCap, Exchange Balance, Search Interest | Short-term (days–weeks) |
| **Crypto Market** | Bloomberg Alternatives + Futures | ETH, BNB, XRP, CFTC Bitcoin Futures Positioning | Cross-horizon |

35 features selected, each justified by Vaissie (2021), domain knowledge, or prior MDA analysis. See the justification table in `CausalAnalysis.ipynb`.

---

## Methodology

### Lopez de Prado's 3-Step Framework

**Step 1 — Phenomenological (observe associations):**
- Stationarity via ADF+KPSS dual confirmation (first-diff for bounded features, pct_change for prices)
- Correlation heatmap + hierarchical clustering dendrogram (Spearman, Ward linkage)
- Clustered MDA feature importance across T+1, T+7, T+30 horizons

**Step 2 — Theoretical (propose causal structures):**

| Method | Type | Key Strength |
|--------|------|-------------|
| **PC Algorithm** | Constraint-based | Handles high dimensions; orients edges via v-structures |
| **NOTEARS** | Score-based (continuous) | Produces edge weights; continuous DAG optimization |
| **PCMCI** | Temporal constraint-based | Detects lagged causes; controls for autocorrelation |
| **Granger Causality** | Predictive | Bidirectional lag detection; simple and interpretable |

**Consensus rule:** A feature must be detected by **2+ of 4 methods** to be a causal candidate.

**Step 3 — Falsification (test with interventions):**
- DoWhy Average Treatment Effect (ATE) at 7-day and 30-day horizons
- 3 refutation tests: Placebo treatment, Random common cause, Data subset
- Feature must pass **2/3 refutations** to be validated

---

## Key Findings

### 10 Validated Causal Drivers of Bitcoin

| Category | Feature | Methods (of 4) | DoWhy Status |
|----------|---------|:-:|---------|
| **On-Chain** | CapMVRVCur (MVRV) | 3 | Survived |
| On-Chain | miner_revenue_usd | 2 | Survived |
| On-Chain | mining_difficulty | 2 | Survived |
| On-Chain | est_tx_volume_usd | 2 | Survived |
| **Sentiment** | total_stablecoin_mcap | 2 | Survived |
| Sentiment | Coinbase (Google Trends) | 2 | Survived |
| Sentiment | Bitcoin (Google Trends) | 2 | Survived |
| **Crypto Market** | XETUSD (ETH) | 3 | Survived |
| Crypto Market | XBNUSD (BNB) | 2 | Survived |
| Crypto Market | XRPUSD (XRP) | 2 | Survived |

**Macro (0 features survived):** Despite showing correlations, no macro feature passed both the multi-method consensus and DoWhy refutation.

### Notable Finding: Fear & Greed is Reverse Causal

`fear_and_greed` shows strong contemporaneous correlation (+0.71 via PCMCI) but is **reverse Granger causal** — BTC price drives sentiment, not the other way around. It is a lagging indicator, not a leading one.

### MDA Horizon Analysis Validates Vaissie's Framework

| Horizon | Top Feature | Category | Interpretation |
|---------|------------|----------|---------------|
| T+1 (short) | CapMVRVCur | On-Chain | Valuation signal dominates at daily scale |
| T+7 (medium) | total_stablecoin_mcap | Sentiment | "Dry powder" deployment drives weekly moves |
| T+30 (long) | FARBAST Index | Macro | Monetary policy stance drives monthly trends |

---

## Quick Start

```bash
# Activate environment
conda activate pi2

# Run the main causal analysis notebook
jupyter notebook notebooks/CausalAnalysis.ipynb

# Run horizon analysis (MDA across T+1/7/30)
python src/analysis/horizon_analysis.py

# Run 5-class scenario classification
python src/analysis/confusion_matrix_enhanced.py
```

### Requirements

Python 3.12 (conda env `pi2`). Key dependencies: pandas, numpy, scikit-learn, scipy, statsmodels, matplotlib, seaborn, networkx, dowhy, causal-learn, tigramite, notears, pyvis.

---

## Output Files

| File | Description |
|------|-------------|
| `data/outputs/metrics/horizon_analysis_results.csv` | Cluster-level MDA by horizon |
| `data/outputs/metrics/horizon_feature_importance.csv` | Per-feature MDA importance |
| `notebooks/causal_graph_interactive.html` | Interactive consensus causal graph (pyvis) |
| `reports/Causal_Analysis_Report.md` | Full methodology & results report |

---

## Team & Partners

- **Academic Partner:** ESILV La Defense
- **Industry Partner:** Ginjer Asset Management (Mathieu Vaissie)
- **Framework:** Lopez de Prado *Causal Factor Investing* (2023) + Vaissie *Bitcoin, un actif comme les autres?* (2021)

---

*Last updated: March 2026*
