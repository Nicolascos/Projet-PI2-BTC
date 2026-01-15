# A Causal Approach to Bitcoin Performance Modeling

**PI2 Industrial Innovation Project**  
*ESILV × Ginjer Asset Management*

---

## 📋 Project Overview

This project applies rigorous causal inference methods to understand what drives Bitcoin returns, moving beyond traditional associational approaches. The goal is to design an interpretable investment strategy for institutional investors.

### Key Objectives
1. Identify **causal factors** (not just correlated) that drive BTC performance
2. Analyze factor importance across different **time horizons** (daily, weekly, monthly)
3. Build a **causal graph** to understand the true data-generating process
4. Develop an **interpretable strategy** aligned with López de Prado's causal factor investing framework

---

## 📁 Project Structure

```
Projet-PI2-BTC/
├── src/                        # Source Code
│   ├── data_ingestion/         # Scripts that fetch raw data (APIs)
│   │   ├── onchain_coinmetrics.py
│   │   ├── sentiment.py
│   │   └── sentiment_fng_only.py
│   ├── data_processing/        # Pipeline scripts that clean & merge data
│   │   ├── create_master_dataset.py
│   │   ├── finalize_onchain_dataset.py
│   │   └── validate_sentiment.py
│   └── analysis/               # Core analysis, models & causality
│       ├── causality/          # Causal Inference Module
│       ├── confusion_matrix_enhanced.py
│       ├── horizon_analysis.py
│       └── strategy_pivot.py
│
├── notebooks/                  # Interactive Jupyter Notebooks
│   ├── BTC_V3.ipynb            # Latest iterative modeling notebook (Current Best Version)
│   ├── BTC_Prediction.ipynb    # Original base analysis notebook
│   └── ...
│
├── data/                       # Data Storage
│   ├── processed/              # Cleaned datasets
│   │   ├── Three_Pillars_Dataset.csv  # Combined Master Dataset
│   │   ├── onchain_data_finalized.csv
│   │   └── sentiment_dataset.csv
│   └── outputs/                # Generated Results
│       ├── images/             # Plots (*.png)
│       └── metrics/            # CSV Results & Reports
│
├── docs/                       # Project Documentation
│   └── meeting_preparation_mathieu.md
│
└── resources/                  # Research papers and reference docs
```

---

## 🔬 Methodology

### Three Pillars of Data

| Pillar | Source | Examples |
|--------|--------|----------|
| **On-Chain** | CoinMetrics | MVRV, HashRate, Active Addresses |
| **Sentiment** | Google Trends, Alternative.me | Search trends, Fear & Greed Index |
| **Macro** | Bloomberg/FRED | Interest rates, DXY, Gold, Carry trades |

### Causal Inference Pipeline

1. **MDA Ranking**: Cluster features, rank by Mean Decrease Accuracy
2. **Granger Causality**: Determine directional causation
3. **Partial Correlation**: Remove confounding effects (Graphical Lasso)
4. **DAG Construction**: Build final causal graph (PC Algorithm)
5. **Validation**: Intervention simulation via do-calculus

---

## 🎯 Key Findings

### Factors That Pass the Causality Filter
| Factor | Direction | Lag | Significance |
|--------|-----------|-----|--------------|
| **CapMVRVCur** (MVRV) | → Price | 1 day | p < 0.0001 |
| **BlackRock Bitcoin** | → Price | 11 days | p = 0.0096 |

### Factors That FAIL (Reverse Causation)
- Active Addresses (AdrActCnt) — Price drives adoption, not reverse
- Macro surprises (CESIJPY, CESIUSD) — BTC influences these indices

---

## 🚀 Quick Start

```bash
# Activate environment
conda activate pi2

# Run horizon analysis
python src/analysis/horizon_analysis.py

# Run scenario analysis
python src/analysis/confusion_matrix_enhanced.py

# Run causality tests
python src/analysis/causality/determine_causal_arrows.py
```

---

## 📊 Output Files

| File | Description |
|------|-------------|
| `data/outputs/metrics/horizon_analysis_results.csv` | Top factors by time horizon |
| `data/outputs/metrics/feature_importance_results.csv` | Full MDA cluster results |
| `data/outputs/metrics/partial_correlation_matrix.csv` | Causal skeleton |
| `docs/data_audit_report.txt` | Data selection documentation |

---

## 👥 Team & Partners

- **Academic Partner**: ESILV La Défense
- **Industry Partner**: Ginjer Asset Management
- **Framework**: López de Prado Causal Factor Investing + Mathieu Vaissié Bitcoin Research

---

*Last updated: January 2026*