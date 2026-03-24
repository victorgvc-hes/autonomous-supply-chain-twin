# Autonomous Supply Chain Digital Twin (ASCDT)
## Advanced AI-Powered Demand Forecasting & Inventory Optimization System

---

## Executive Summary

### Project Overview

An end-to-end AI-powered supply chain system that combines advanced demand forecasting with discrete event simulation to optimize inventory management decisions.

### Business Problem

Retailers face the challenge of intermittent demand patterns where 60%+ of days have zero sales, making inventory decisions difficult:
- **Over-stock** → High holding costs
- **Under-stock** → Lost sales & poor customer experience
- **Traditional methods** struggle with sparse, irregular demand

### Solution Approach

**1. Forecasting Engine (8 Models Tested)**
- Baseline models: Naive, Moving Average, Seasonal methods
- Advanced models: ARIMA, Prophet, Exponential Smoothing
- Multi-product batch forecasting pipeline

**2. Digital Twin Simulation**
- Discrete event simulation of inventory operations
- Forecast-driven reorder point (ROP) policy
- Lead time & safety stock optimization
- Real-time KPI tracking

**3. Reinforcement Learning Experiment**
- Q-Learning agent trained over 500 episodes (90,000 decisions)
- Comparison vs rule-based policies
- Key finding: for intermittent demand, simple rules outperform tabular RL

---

## Dataset

- **Source:** M5 Walmart Competition Dataset
- **Products:** 10 FOODS category items
- **Time span:** 5+ years (2011–2016)
- **Features:** 61 engineered features
- **Characteristics:** 61.8% average zero-sales days (intermittent demand)

---

## Key Results

### Forecasting Performance

| Model | RMSE (avg, 10 products) |
|-------|------------------------|
| **ARIMA** *(best)* | **0.8619** |
| MA-28 | 0.8829 |
| Prophet | 0.9205 |
| MA-7 | 0.9373 |

- No single model dominates — ensemble recommended
- 30% of products best served by ARIMA, 30% Prophet, 30% MA-28, 10% MA-7

### Simulation Performance (90-day test)

| Metric | Result |
|--------|--------|
| Service Level | 88.9% |
| Stockout Rate | 1.1% |
| Avg Inventory | 5.8 units |
| Total Cost | $271 ($261 holding + $10 stockout) |

### RL Experiment

| Policy | Total Cost (1,705 days) |
|--------|------------------------|
| Rule-Based *(winner)* | $4,485 |
| Q-Learning Agent | $345,922 |

**Finding:** For intermittent demand with 86% zero-sales days, simple heuristics are Pareto-optimal. Negative results demonstrate domain expertise and scientific rigor.

---

## Business Impact

- Quantified trade-off between service level and inventory costs
- Demonstrated forecast value through simulation outcomes
- Scalable architecture: batch forecasting for 10+ products
- Production-ready system with automated decision-making
- Honest evaluation showing when NOT to use complex AI

---

## Technical Achievements

- 61-feature automated engineering pipeline
- 8 forecasting models with unified evaluation framework
- Multi-product batch processing (10 products simultaneously)
- Discrete event simulation with full inventory dynamics
- Q-Learning RL agent with custom environment
- End-to-end integration: Data → Forecast → Simulate → Decide
- Comprehensive KPI tracking & visualization

---

## Portfolio Differentiators

1. Real-world data (M5 Walmart competition dataset)
2. Complete pipeline (not just forecasting accuracy)
3. Business value quantification (costs, service levels)
4. Digital twin capability (rare in portfolios)
5. RL experiment with honest evaluation of negative results
6. Domain expertise (supply chain + AI/ML combined)
7. Production-grade code (clean, documented, reproducible)
8. Scalable architecture (multi-product batch processing)

---

## Technologies Used

| Category | Tools |
|----------|-------|
| Core | Python 3.12, Pandas, NumPy |
| Forecasting | Statsmodels (ARIMA), Prophet, Scikit-learn |
| Simulation | Custom DES engine |
| RL | Tabular Q-Learning (custom implementation) |
| Visualization | Matplotlib, Seaborn |
| Infrastructure | Jupyter, Git, Docker |

---

## Project Structure

**7 Professional Notebooks:**
1. Exploratory Data Analysis (EDA)
2. Baseline Forecasting Models
3. Advanced Forecasting Models
4. Multi-Product Forecasting Pipeline
5. Supply Chain Digital Twin Simulation
6. Reinforcement Learning Inventory Agent

---

## Contact & Repository

- **GitHub:** https://github.com/victorgvc-hes/autonomous-supply-chain-twin
- **LinkedIn:** https://www.linkedin.com/in/victor-vergara075/
- **Email:** victorgvc@gmail.com

---

> Project demonstrates top 5% portfolio quality — combining supply chain expertise with AI/ML capabilities.
