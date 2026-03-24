# Technical Presentation Script (Final)
**Duration:** 15–20 minutes | **Audience:** Data scientists, ML engineers, AI researchers, technical architects
**Goal:** Demonstrate technical depth, methodology, reproducibility, and RL capability

---

## [SLIDE 1: TITLE & TECHNICAL OVERVIEW — 1 minute]

Good [morning/afternoon]. I'm presenting the Autonomous Supply Chain Digital Twin — a complete ML system integrating forecasting, simulation, and reinforcement learning for inventory optimization under intermittent demand.

I'm [Your Name] — 20+ years supply chain, 10+ years ML/AI, credentials from MIT and Oxford. This project demonstrates production-grade ML engineering combined with deep domain expertise.

**Technical Stack:**
- Core: Python 3.12, pandas, NumPy, scikit-learn
- Forecasting: statsmodels, Prophet, custom implementations
- Simulation: Custom DES engine (object-oriented)
- RL: Tabular Q-Learning (epsilon-greedy exploration)
- Infrastructure: Jupyter, Git, Docker, modular architecture

All code is reproducible, documented, and on GitHub.

---

## [SLIDE 2: PROBLEM FORMULATION & DATASET — 2 minutes]

**Dataset: M5 Walmart Forecasting Competition**
- Source: Kaggle (real Walmart POS data)
- Scope: 10 products (FOODS category) from 30,490 SKU universe
- Temporal: 1,885 daily observations (2011-01-29 to 2016-03-27)
- Train/Test: 1,857 / 28 days (last 28 held out)

**Challenge: Intermittent Demand Time Series**
- Zero-inflation: 61.8% of observations are zeros
- High variance: μ=0.58 units/day, σ=1.22, max=25
- Coefficient of variation: CV = 2.1 (highly variable)
- Violates standard assumptions: non-continuous, non-stationary, sparse

**Mathematical Formulation:**

Objective: Minimize total cost over horizon T

```
min Σ(t=1 to T) [c_h × I_t + c_s × S_t]

where:
  I_t = inventory at time t
  S_t = stockout at time t
  c_h = holding cost per unit ($0.50/day)
  c_s = stockout cost per unit ($5.00)

subject to:
  I_t = I_{t-1} + O_{t-L} - D_t
  S_t = max(0, D_t - I_{t-1})
  Service Level ≥ 0.90
```

---

## [SLIDE 3: FEATURE ENGINEERING PIPELINE — 2.5 minutes]

Engineered 61 features across 5 categories using domain knowledge:

**1. Lag Features (4 features)**
- `sales_lag_{7,14,21,28}`
- Captures autocorrelation structure
- Best: lag_7 (r=0.40 with target)

**2. Rolling Statistics (12 features)**
- `sales_rolling_{mean,std,min,max}_{7,14,28}`
- Best: rolling_mean_28 (r=0.59) — strongest single predictor
- Handles non-stationarity via moving window

**3. Calendar Features (14 features)**
- Temporal: year, month, day, day_of_week, week_of_year
- Cyclical: `sin(2π × dow / 7)`, `cos(2π × dow / 7)`
- Boolean: is_weekend, is_month_start, is_month_end
- Events: has_event_{1,2}, event_type_encoded

**4. Price Features (6 features)**
- price_change, price_change_pct, price_momentum
- price_vs_ma_{7,28}, price_rank_in_category
- Finding: Elasticity near zero (r=-0.07) — necessity product, price-insensitive

**5. Hierarchical Features (6 features)**
- {store,cat,dept,state}_avg_sales
- item_share_of_{cat,store}
- Best: store_avg_sales (r=0.71) — STRONGEST predictor

**Feature Selection Insight:** Store-level aggregations >> individual product patterns → recommendation: top-down forecasting approach

---

## [SLIDE 4: MODEL ARCHITECTURE & SELECTION — 3 minutes]

### Baseline Models (5 implementations)

| Model | RMSE | Notes |
|-------|------|-------|
| Naive | 0.8018 | Fails on zero-inflated data |
| Seasonal Naive (s=7) | 0.8864 | Worst — weak seasonality |
| MA-7 | **0.7759** | Best baseline — smooths noise |
| MA-28 | 0.7930 | Over-smooths intermittent demand |
| Historical Mean | 0.7882 | Competitive for sparse data |

### Advanced Models (3 implementations)

**ARIMA(p,d,q)**
```
y_t = φ₁y_{t-1} + θ₁ε_{t-1} + ε_t
Order selection: Grid search, Best: ARIMA(1,0,1)
RMSE: 0.7745 (single) | Avg RMSE: 0.8619 (10 products) ← BEST OVERALL
```

**Prophet (Meta/Facebook)**
```
y(t) = g(t) + s(t) + h(t) + ε_t
Hyperparams: changepoint_prior_scale=0.05, seasonality_mode='additive'
RMSE: 0.7816 (single) | Avg RMSE: 0.9205 (10 products)
Analysis: Over-parameterized for simple intermittent patterns
```

**Exponential Smoothing (Holt-Winters)**
```
State space: level + trend + seasonal (weekly, period=7)
RMSE: 0.7919 (single product)
```

### Multi-Product Results

| Model | Avg RMSE | Products Best At |
|-------|----------|-----------------|
| ARIMA | **0.8619** | 30% |
| MA-28 | 0.8829 | 30% |
| Prophet | 0.9205 | 30% |
| MA-7 | 0.9373 | 10% |

**Key finding:** No universal best model → product-specific selection required → ensemble recommendation: 0.6×ARIMA + 0.4×MA-28

---

## [SLIDE 5: DIGITAL TWIN SIMULATION ENGINE — 3 minutes]

**Architecture: Custom Discrete Event Simulation**
- Class: `InventorySimulator` (OOP)
- Paradigm: Event-driven state machine
- Time: Discrete daily timesteps

**Inventory Policy: (s, Q) Reorder Point**
```
s (reorder point) = μ_forecast + z × σ_error × √L
  z = 1.65 (for 95% service level)
  L = lead time (1 day)

Q (order quantity) = μ_forecast × review_period (7 days)
```

**Simulation Algorithm (Daily Loop):**
```python
def simulate_day(day, demand, forecast):
    # 1. Receive orders
    for (arrival_day, qty) in orders_in_transit:
        if arrival_day == day:
            inventory += qty

    # 2. Fulfill demand
    fulfilled = min(demand, inventory)
    stockout = max(0, demand - inventory)
    inventory = max(0, inventory - demand)

    # 3. Check reorder condition
    if inventory <= reorder_point:
        place_order(order_quantity)

    # 4. Calculate costs
    holding_cost = inventory × c_h
    stockout_cost = stockout × c_s

    # 5. Record KPIs
    return {inventory, fulfilled, stockout, costs}
```

**Simulation Results (90-day run):**

| Metric | Value |
|--------|-------|
| Service Level | 88.9% (target: 95%) |
| Stockout Rate | 1.1% |
| Avg Inventory | 5.8 units |
| Turnover | 3.1× annually |
| Total Cost | $271 ($261 holding + $10 stockout) |

**Validation:** Compared forecast-driven vs simple historical average → identical results (88.9% service, $271 cost).

**Interpretation:** For low-volume intermittent demand, complex forecasts don't improve inventory decisions. Digital twin value = **risk quantification**, not accuracy improvement.

---

## [SLIDE 6: REINFORCEMENT LEARNING IMPLEMENTATION — 3.5 minutes]

**Algorithm: Tabular Q-Learning**
```
Q(s,a) ← Q(s,a) + α[r + γ max_{a'} Q(s',a') - Q(s,a)]

where:
  s = state (inventory level, recent demand)
  a = action (order quantity)
  r = reward (-cost)
  α = 0.1, γ = 0.95
```

**Environment Design:**
- State Space: Inventory bins [0,2,4,...,20] × Demand bins [0,0.5,1.0,2.0] = 44 states
- Action Space: {0, 1, 2, 3, 4, 5} units = 6 actions
- Reward: `r_t = -(holding_cost_t + stockout_cost_t)`

**Training Configuration:**

| Parameter | Value |
|-----------|-------|
| Episodes | 500 |
| Days/episode | 180 |
| Total steps | 90,000 |
| ε₀ | 1.0 → 0.082 (at eval) |

**Results:**

| Policy | Total Cost (1,705 days) |
|--------|------------------------|
| Rule-Based | $4,485 ✅ |
| RL Agent | $345,922 ❌ |

**Root Cause Analysis:**

1. **Sparse Reward Signal** — 86% zero demand → agent learned to over-order to avoid rare stockouts
2. **Insufficient Training** — only 30/44 states visited
3. **Tabular Limitation** — no function approximation, can't generalize
4. **Exploration Residual** — ε=0.082 still exploring at eval (should use ε=0)

**Technical Lessons:**
- RL requires dense rewards for stable learning
- Tabular methods don't scale to large state spaces → need DQN
- Domain heuristics often beat ML for simple problems
- Honest negative results build credibility

---

## [SLIDE 7: EXPERIMENTAL DESIGN & REPRODUCIBILITY — 2 minutes]

| Split | Period |
|-------|--------|
| Forecasting Train | Days 1–1,857 (5+ years) |
| Forecasting Test | Days 1,858–1,885 (28 days) |
| RL Train | Days 1–180 (6 months) |
| RL Test | Days 181–1,885 (4.5 years) |

**Reproducibility:**
- Random seed: 42 (global)
- Environment: Python 3.12, Windows 10, venv
- Dependencies: requirements.txt (60+ packages pinned)
- Data: Public (Kaggle M5)
- Runtime: ~15 minutes total

**Compute:** Standard laptop (no GPU). Prophet is the bottleneck (~1–2 min/product). Embarrassingly parallel across products.

---

## [SLIDE 8: TECHNICAL CHALLENGES & SOLUTIONS — 2.5 minutes]

| Challenge | Solution | Lesson |
|-----------|----------|--------|
| Zero-inflated time series (61.8% zeros) | ARIMA surprisingly robust | Simpler >> complex for sparse data |
| TFT failed (PyTorch conflicts on Windows) | Pivoted to statistical methods | Match tools to infrastructure constraints |
| ARIMA improved RMSE only 0.18% but no cost improvement | Accuracy ≠ value for intermittent demand | Measure impact on decisions, not just metrics |
| RL significantly underperformed | Reported honestly, analyzed root cause | Honest evaluation builds trust |

---

## [SLIDE 9: TECHNICAL CONTRIBUTIONS — 2 minutes]

1. **End-to-End System** — Data → Forecast → Simulate → RL → Quantify (rare in portfolios)
2. **Intermittent Demand Benchmarking** — Systematic comparison of 9 models on sparse retail data
3. **Custom Digital Twin** — Production-ready DES with forecast integration, policy testing, cost-service quantification
4. **RL for Inventory (Negative Result)** — Validates when NOT to use RL; research-level rigor
5. **Production Architecture** — Modular `src/`, config-driven (YAML), batch processing, Docker-ready

---

## [SLIDE 10: FUTURE WORK — 2 minutes]

**Immediate (1–3 months):**
- Probabilistic forecasting (quantile regression, prediction intervals)
- Hierarchical forecasting (top-down: store → products)
- Deep Q-Network (DQN) with function approximation, experience replay

**Advanced (3–6 months):**
- Multi-agent RL (coordinated replenishment, shared capacity)
- Causal inference (DoWhy, event impact, price elasticity)
- Network simulation (multi-echelon, transshipment, risk pooling)

**Production (6–12 months):**
- MLOps pipeline (automated retraining, drift detection, A/B testing)
- Real-time API (FastAPI + PostgreSQL)
- Interactive dashboard (Streamlit, what-if scenarios)
- Container orchestration (Docker + Kubernetes)

---

## [CLOSING — 1 minute]

**Summary of Technical Contributions:**
1. Complete ML system: 61 features → 9 models → Simulation → RL
2. Production architecture: Modular, documented, reproducible
3. Methodological rigor: Proper splits, baselines, evaluation
4. Domain integration: Supply chain + ML depth
5. Novel application: Digital twin + RL for intermittent demand
6. Honest evaluation: Negative RL result demonstrates maturity

This project demonstrates **senior-level ML engineering:**
- ✅ Problem formulation
- ✅ Feature engineering
- ✅ Model selection & validation
- ✅ Simulation & optimization
- ✅ Production architecture
- ✅ Critical evaluation

Code available on GitHub. Happy to deep-dive on any component. Thank you.

---

## Q&A Preparation

**Q: "Why not deep learning (LSTM, Transformer)?"**
A: Attempted TFT but insufficient data (10 products). For sparse time series (62% zeros), statistical methods often outperform DL. Our ARIMA result validates this.

**Q: "How would you improve RL performance?"**
A: (1) 5000+ episodes, (2) dense demand products (<30% zeros), (3) DQN with function approximation, (4) reward shaping, (5) multi-product joint learning.

**Q: "Computational complexity at scale?"**
A: ARIMA O(n) per product, parallelizable. At 10K products: sequential ~200 min, parallel (16 cores) ~13 min, cloud (Ray) <5 min.

**Q: "Why tabular Q-learning vs DQN?"**
A: Pedagogical + computational. Tabular is easier to implement, interpret, and debug. DQN is the next iteration for continuous state spaces.

**Q: "Statistical significance of improvements?"**
A: Current: single train/test split. Proper approach: time series cross-validation (rolling origin) + Diebold-Mariano test. Future work.
