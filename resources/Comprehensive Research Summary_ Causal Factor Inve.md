<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## Comprehensive Research Summary: Causal Factor Investing for Bitcoin Performance Modeling

### Executive Overview

This project combines two critical research frameworks to develop a causal model for Bitcoin performance analysis. The primary goal is to move beyond traditional associational approaches by applying rigorous causal inference methods to understand what drives Bitcoin returns, ultimately designing an interpretable investment strategy for institutional investors.[^1]

***

## Part I: Causal Factor Investing Framework (López de Prado)

### The Core Problem with Current Factor Investing

**The Associational Trap**[^2]

Current factor investing literature suffers from a fundamental flaw: researchers make associational claims while their models implicitly contain causal content. Most academic papers identify correlations between factors and returns without explaining **why** these relationships exist or proposing falsifiable causal mechanisms.

**Two Types of Spurious Claims**[^2]

- **Type-A Spuriosity**: False discoveries due to backtest overfitting and p-hacking. Random statistical flukes mistaken for real patterns.
- **Type-B Spuriosity**: Noncausal associations caused by confounding variables. The relationship exists in data but won't persist under intervention because the true causal structure is misunderstood.


### The Three-Step Scientific Method

**1. Phenomenological Step**[^2]

Observe recurring patterns or anomalies in data. Document that variables X and Y are associated ($P[X = x, Y = y] \neq P[X = x]P[Y = y]$). This is purely descriptive—no explanation required yet.

**2. Theoretical Step**[^2]

Propose a falsifiable causal mechanism explaining the observed association. The mechanism must specify the causal path from X to Y through measurable intermediate variables. This requires extra-statistical information and domain expertise.

**3. Falsification Step**[^2]

Design experiments to test each component of the proposed mechanism. Use interventional studies, natural experiments, or simulated interventions to verify that $P(Y = y | do[X = x]) > P[Y = y]$, meaning X genuinely causes Y.

### Understanding Causation vs. Association

**The Do-Operator**[^2]

Pearl's do-operator distinguishes between:

- **Conditioning**: $P[Y = y | X = x]$ - observing Y when X happens to be x
- **Intervention**: $P[Y = y | do[X = x]]$ - setting X to x and observing the effect on Y

Causation means intervening on X changes the probability distribution of Y, holding all else equal (ceteris paribus).

**Causal Graphs (DAGs)**[^2]

Directed Acyclic Graphs visually represent causal structures, showing:

- Which variables influence others
- Direction of causality (arrows)
- Potential confounders (variables causing both X and Y)
- Mediators (variables on the causal path from X to Y)
- Colliders (variables caused by both X and Y)


### Causal Inference Methods

When experiments are impossible or impractical, three approaches enable causal inference from observational data:[^2]

**Backdoor Adjustment**[^2]

When confounders are observable, condition on variables Z that block all noncausal paths between treatment X and outcome Y. This simulates $do[X = x]$ by removing confounding bias.

**Front-Door Adjustment**[^2]

When confounders are unobservable (latent), use mediators M that fully transmit X's effect on Y. Estimate the causal effect through the mediation path.

**Instrumental Variables**[^2]

Find a variable W that affects Y only through X. W serves as a proxy for the causal effect when direct measurement is confounded.

### Why Factor Investing Needs Causality

**Hidden Causal Assumptions**[^2]

Every factor model makes implicit causal claims through:

- Model specification (choosing Y = Xβ + ε implies X causes Y)
- Least-squares estimation (assumes exogenous errors uncorrelated with X)
- Statistical significance testing (testing whether β ≠ 0)
- Portfolio construction (overweighting stocks with high X exposure)

**The Problem of Under-Controlling**[^2]

Factor researchers typically control for market returns and perhaps a few other factors. But without knowledge of the true causal graph, they cannot know whether they're controlling for the right variables. This leads to:

- Omitted variable bias
- Collider bias (controlling for variables that should not be controlled)
- Incorrect causal attribution

**Time-Varying Risk Premia**[^2]

Many famous factors show unstable performance over time. López de Prado argues this is often due to Type-B spuriosity—the original associations were noncausal, driven by confounders whose influence changed.

### Recommendations for Scientific Factor Investing

**For Researchers**[^2]

1. **Declare the causal graph** consistent with your model specification
2. **Propose falsifiable mechanisms** explaining why the factor should earn returns
3. **Use causal discovery algorithms** to identify relevant variables and relationships
4. **Design experiments** to test specific causal links
5. **Apply do-calculus** to adjust for confounders using observational data
6. **Test stability** of causal mechanisms across time and market conditions

**For Institutional Investors**[^2]

Demand explanations for "why" factors work, not just "that" they have worked historically. Causal investment strategies offer:

- **Efficiency**: Proper risk attribution
- **Interpretability**: Explainable performance
- **Transparency**: Explicit assumptions
- **Reproducibility**: Lower risk of spurious findings
- **Adaptability**: Resilience to structural changes
- **Extrapolation**: Better handling of unprecedented events

***

## Part II: Bitcoin as an Investment Asset (Vaissié)

### The Valuation Challenge

**Why Bitcoin is Different**[^3]

Bitcoin generates no cash flows, making traditional discounted cash flow valuation impossible. Unlike stocks or bonds, there's no intrinsic value anchor. Unlike gold, Bitcoin lacks centuries of historical precedent as a store of value.

**The Missing Valuation Model**[^3]

The major barrier to institutional adoption isn't volatility—it's the absence of an objective valuation framework. Just as the Black-Scholes formula enabled options markets to explode, Bitcoin needs a valuation model to transition from speculative asset to investment-grade instrument.

**Current Valuation Approaches**[^3]

- **Stock-to-Flow**: Models scarcity but ignores demand dynamics
- **Network Value**: Difficult without knowing what value will be exchanged
- **Greater Fool Theory**: Price depends solely on finding a buyer willing to pay more


### Factors Driving Bitcoin Performance

Vaissié's analysis categorizes Bitcoin price drivers into three dimensions:[^3]

**1. Fundamental (On-Chain) Factors**

Most important variables identified:[^3]

- **MVRV (Market Value to Realized Value)**: Ratio of market price to average acquisition cost across all holders—measures unrealized gains/losses. **Primary driver** reflecting investor psychology.
- **Miner Revenue Changes**: Miners are critical ecosystem participants; their economic incentives affect supply dynamics.
- **Hash Rate \& Mining Difficulty**: Network security and computational power required to mine new blocks.
- **Transaction Activity**: Volume exchanged, number of transactions, unique addresses used.
- **Network Congestion**: Transaction fees, mempool size (pending transactions).
- **NVT (Network Value to Transactions)**: Market cap relative to transaction volume.

**2. Macro-Economic Factors**

Interest rates dominate macro influences:[^3]

- **Short-term US rates**: Level and changes
- **Global rate dynamics**: Particularly US, China, Japan movements
- **US yield curve slope**: Term premium signals
- **Inflation concerns**: Fiat currency debasement fears drive "hard money" narrative
- **Traditional market indicators**: Equity indices (S\&P500, Nasdaq, tech sector), commodity prices (oil, gold), volatility indices (VIX), currency movements

**3. Technical Factors**

Classic technical analysis tools prove relevant:[^3]

- **Trend Indicators**: Moving averages (simple and exponential), ADX, Aroon
- **Momentum Indicators**: RSI, Stochastic, CCI, MACD
- **Position Indicators**: Distance from min/max levels, gaps (especially upward), Bollinger Bands
- **Volatility Measures**: Across multiple timeframes


### Time Horizon Analysis

**Model Performance by Horizon**[^3]

- **Short-term (days to weeks)**: Technical factors dominate with high predictive accuracy
- **Medium-term (weeks to months)**: Fundamental on-chain data becomes most important
- **Long-term (months+)**: Macro-economic factors gain relevance

The signal-to-noise ratio improves with longer horizons, making predictions more reliable at monthly/quarterly scales than daily.[^3]

**Market Regime Performance**[^3]

Models perform consistently across most conditions (+2σ moves up, +1σ moves up, neutral, -1σ moves down) **except** extreme capitulation events (-2σ crashes). This reflects:

- Path dependency in complex systems
- Feedback loops during panic selling
- Potential market manipulation in unregulated crypto markets


### Institutional Adoption Parallels

**The Hedge Fund Analogy**[^3]

Twenty years ago, hedge funds faced similar skepticism from institutions—less regulated, less transparent, less liquid, more operationally risky. But institutional demand drove industry maturation: better infrastructure, improved transparency, standardized tools, regulatory frameworks.

**Current Institutionalization Signals**[^3]

Growing interest from central banks (Fed, ECB, BoJ), commercial banks (JP Morgan, Citi, Deutsche Bank, Société Générale), corporations (Square, MicroStrategy, PayPal, Visa), and prominent investors (Paul Tudor Jones, Stanley Druckenmiller, Dan Tapiero).

**The Hard Money Narrative**[^3]

Bitcoin's fixed supply schedule (converging to 21 million by ~2140) contrasts sharply with quantitative easing and unlimited fiat creation post-2008 and post-COVID. This "hard tightening vs. quantitative easing" story resonates as purchasing power concerns mount.

***

## Part III: Your Project Framework

### Project Objectives[^1]

**Primary Goal**: Build a causal model identifying and quantifying key drivers of Bitcoin performance across multiple time horizons (daily, weekly, monthly, quarterly, yearly).

**Secondary Goal**: Design a slow-moving investment strategy capturing upside while mitigating downside risks, based on causal insights.

**Why This Matters**: Institutional investors require transparent, interpretable decision frameworks. Traditional machine learning lacks explainability; causal models provide rational justification for investment choices.

### Methodology Integration

**Applying López de Prado's Framework to Bitcoin**

1. **Phenomenological Phase**: Use Vaissié's empirical findings on which factors correlate with Bitcoin returns across timeframes.
2. **Theoretical Phase**: Propose causal mechanisms explaining these relationships:
    - Why would MVRV cause price movements? (investor behavior, profit-taking thresholds)
    - Why would interest rates affect Bitcoin? (opportunity cost, inflation hedge narrative)
    - Why would on-chain metrics matter? (supply-demand dynamics, network effect)
3. **Causal Discovery**: Apply machine learning feature selection (Clustered Mean Decrease Accuracy on Random Forest) to identify relevant variables while controlling for multicollinearity.[^3]
4. **DAG Construction**: Build Directed Acyclic Graphs representing hypothesized causal relationships.[^1]
5. **Causal Testing**: Use tools like DoWhy or CausalNex to test causal links, applying do-calculus adjustments.[^1]
6. **Validation**: Compare causal model performance against purely associational ML approaches (regression, random forest, LSTM).[^1]

### Key Technical Approaches

**Feature Engineering Strategy**[^3]

For each raw data series, compute:

- Raw levels
- Changes over multiple periods (daily, weekly, monthly)
- 60-day rolling volatility

This captures level effects, momentum/trend effects, and volatility regimes.

**Avoiding Spurious Results**[^3]

Following López de Prado's methods to control for:

- Multicollinearity (eliminate redundant factors)
- Multiple testing (careful statistical significance assessment)
- Overfitting (out-of-sample validation on test data)

**Data Categories to Collect**[^1]

1. **On-chain fundamentals** (Blockchain.com): Transaction counts/volumes, hash rate, mining difficulty, miner revenue, fees, unique addresses, MVRV, NVT
2. **Macro-economic indicators** (Bloomberg): Interest rates (multiple countries/maturities), yield curves, currencies, equity indices, commodity prices, volatility indices
3. **Technical indicators**: Computed from price/volume data across timeframes

### Project Execution Plan[^1]

**Weeks 1-2**: Kick-off, project understanding, initial exploration

**Weeks 3-4**: Data collection and cleaning (APIs, financial databases)

**Weeks 5-6**: Causal model design, preliminary DAG construction

**Weeks 7-8**: Model testing, accuracy validation, ML comparison

**Weeks 9-10**: Investment strategy design, final presentation

**Key Deliverables**:[^1]

- Validated dataset with documentation
- Causal graph (DAG) with interpretations
- Analytical comparison report (causal vs. ML models)
- Investment strategy based on causal insights
- Complete Jupyter notebook and presentation

***

## Critical Insights for Your Project

### Synthesis: Bridging the Two Papers

**The Central Challenge**: Traditional Bitcoin analysis relies on associational machine learning—identifying patterns without understanding mechanisms. This creates:

- Black-box predictions that institutional investors cannot justify
- Vulnerability to regime changes when associations break down
- Inability to distinguish real causal effects from spurious correlations

**Your Solution**: Apply causal inference rigorously to move Bitcoin analysis from phenomenological stage to scientific stage.

### Practical Recommendations

**1. Start with Vaissié's Empirical Findings**[^3]

Use his identified factors as starting hypotheses:

- MVRV as behavioral/psychological driver
- Interest rates as macro regime indicator
- Technical factors for short-term dynamics

**2. Build Competing Causal Hypotheses**

For each factor, propose multiple causal mechanisms:

- Direct causation (factor → Bitcoin price)
- Reverse causation (Bitcoin price → factor)
- Common cause (confounder → both factor and price)
- Mediation (factor → mediator → price)

**3. Use Causal Discovery Algorithms**[^2]

Apply constraint-based (PC algorithm), score-based (GES), or functional causal models to suggest DAG structures from data.

**4. Test Specific Causal Links**

Design quasi-experiments:

- **RDD**: Does Bitcoin react differently just above/below interest rate thresholds?
- **DID**: Compare Bitcoin performance in periods with/without specific interventions
- **Instrumental variables**: Find exogenous shocks affecting factors but not Bitcoin directly

**5. Apply Do-Calculus Adjustments**[^2]

- Backdoor adjustment: Control for observed confounders (macro conditions)
- Front-door adjustment: Use mediators when confounders are latent
- Validate that adjustments successfully block non-causal paths

**6. Distinguish Model Performance from Causal Validity**

A model with high R² or accuracy might still be spurious. Focus on:

- Stability across different time periods
- Robustness to structural changes
- Interpretability of mechanisms
- Falsifiability of predictions


### Addressing Institutional Investor Needs

**Transparency**: DAGs explicitly show all assumptions about causal structure.

**Interpretability**: Each arrow in the graph represents a testable relationship with clear directionality.

**Risk Management**: Understanding causal mechanisms enables:

- Factor timing (when causal effects strengthen/weaken)
- Dynamic position sizing based on mechanism validity
- Early warning when causal links break down

**Regime Adaptation**: Causal models can extrapolate to new conditions better than associational models, crucial for black-swan events.

### Expected Challenges

**1. Limited Historical Data**[^3]

Bitcoin has relatively short history compared to traditional assets. This limits:

- Statistical power for causal tests
- Ability to observe multiple economic regimes
- Confidence in long-term causal stability

**Mitigation**: Focus on mechanisms with strong theoretical support; use multiple validation approaches.

**2. Extreme Events**[^3]

Models struggle with -2σ capitulation scenarios due to:

- Feedback loops and path dependency
- Herding behavior and contagion
- Potential market manipulation

**Mitigation**: Model regime-switching behavior; treat extreme crashes separately.

**3. Unobserved Confounders**

Many potential drivers are difficult to measure:

- Regulatory sentiment
- Social media sentiment evolution
- Institutional positioning
- Whale behavior

**Mitigation**: Use proxy variables; apply front-door adjustment when mediators exist.

**4. Time-Varying Relationships**[^2]

Even true causal effects may change magnitude over time as:

- Market structure evolves
- Participant composition shifts
- Regulatory environment changes

**Mitigation**: Estimate time-varying causal parameters; monitor mechanism stability.

### Strategic Investment Design

**Slow-Moving Strategy Rationale**[^1]

Aligns with causal framework because:

- Causal effects manifest more clearly over longer horizons
- Reduces transaction costs and slippage
- Focuses on fundamental drivers rather than noise
- Matches institutional investment mandates

**Potential Strategy Components**

Based on causal model insights:

- **Entry/Exit signals**: When causal drivers align favorably/unfavorably
- **Position sizing**: Proportional to causal mechanism strength
- **Hedging**: Protect against breakdown of key causal links
- **Rebalancing rules**: Triggered by changes in causal graph structure

**Performance Evaluation**

Compare strategy not just on returns, but on:

- Adherence to causal predictions
- Robustness during structural breaks
- Interpretability of performance attribution
- Ability to explain drawdowns causally

***

## Conclusion: Your Competitive Advantage

By integrating López de Prado's causal factor investing framework with Vaissié's empirical Bitcoin analysis, your project addresses a critical gap: **the lack of scientific rigor in cryptocurrency investment research**.[^2]

Traditional approaches have left Bitcoin in a phenomenological stage—patterns observed but not explained. Your causal model will enable institutional investors to move beyond "Bitcoin has been correlated with X" to "Bitcoin performs well when X causes Y through mechanism Z, and here's how we can verify this relationship continues to hold."

This transforms Bitcoin from a speculative gamble into an analyzable, manageable investment with transparent risk-return drivers—precisely what institutional capital requires for allocation.[^3]

**Your project is not just building a model; you're pioneering the application of rigorous causal inference to a nascent asset class, potentially establishing the scientific foundation for institutional cryptocurrency investment.**

<div align="center">⁂</div>

[^1]: Kick-off-document.pdf

[^2]: causal-factor-investing.pdf

[^3]: Bitcoin-un-actif-comme-les-autres-Mathieu-Vaissie.pdf

