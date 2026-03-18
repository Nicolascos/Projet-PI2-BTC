# Vaissié (2021) — "Bitcoin, un actif comme les autres?"
Vaissié identifies 3 pillars of Bitcoin performance drivers:

### Pillar 1 — On-Chain Fundamentals (medium-term, weeks to months):

MVRV (Market Value / Realized Value) — described as the "primary driver reflecting investor psychology", measures unrealized gains/losses across all holders
Hash Rate & Mining Difficulty — network security and computational power
Miner Revenue — miners are forced sellers; their economics affect supply dynamics
Transaction Activity (volume, count, unique addresses) — organic usage signal
NVT (Network Value to Transactions) — "crypto P/E ratio"
Network Congestion (fees, mempool) — demand for block space

### Pillar 2 — Macro-Economic (long-term, months+):

Interest rates — "interest rates dominate macro influences" (short-term US rates, global rate dynamics)
US yield curve slope — recession/expansion signal
Equity indices (S&P 500, Nasdaq)
Dollar (DXY), currencies, gold, oil
VIX — volatility / risk regime

### Pillar 3 — Technical/Sentiment (short-term, days to weeks):

Search interest, Fear & Greed, exchange balances, stablecoin supply
Vaissié notes "the signal-to-noise ratio improves with longer horizons"
Key insight: Vaissié notes that Bitcoin "generates no cash flows, making traditional DCF valuation impossible" — hence the need for alternative factor frameworks.

# López de Prado (2023) — "Causal Factor Investing"
López de Prado does not specify Bitcoin-specific factors. His contribution is the methodology for avoiding spurious factor discovery:

The problem he identifies:

Type-A Spuriosity: False discoveries from backtest overfitting / p-hacking
Type-B Spuriosity: Non-causal associations from confounding variables
"Current factor investing literature suffers from a fundamental flaw: researchers make associational claims while their models implicitly contain causal content."
His 3-step scientific method:

Phenomenological step — observe associations (correlation, MDA)
Theoretical step — propose a falsifiable causal mechanism (PC, NOTEARS, PCMCI, Granger)
Falsification step — test via interventions (DoWhy ATE + refutation tests)
His recommended tools:

Causal discovery algorithms (constraint-based like PC, score-based like GES)
Backdoor/front-door adjustment for confounders
Do-calculus for estimating causal effects from observational data
Stability testing across time periods