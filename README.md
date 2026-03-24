**Advanced AI-Powered Demand Forecasting & Inventory Optimization System**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/Status-Active-success.svg)]()

---

## 🎯 Project Overview

An **end-to-end AI-powered supply chain system** that combines advanced demand forecasting with discrete event simulation to optimize inventory management decisions for products with intermittent demand patterns.

### The Challenge
Retailers managing products with **intermittent demand** (60%+ zero-sales days) face critical inventory decisions:
- ❌ **Over-stock** → High holding costs, capital tied up
- ❌ **Under-stock** → Lost sales, poor customer experience
- ❌ **Traditional methods** struggle with sparse, irregular patterns

### The Solution
**ASCDT** provides a complete pipeline:
1. **Forecast** future demand using 8+ ML/statistical models
2. **Simulate** inventory operations with digital twin
3. **Optimize** reorder policies based on cost-service trade-offs
4. **Scale** to multiple products with batch processing

---

## 🏆 Key Results

### Forecasting Performance
- **Best Model:** ARIMA (RMSE: 0.8619 across 10 products)
- **Models Tested:** 8 total (Naive, MA, ARIMA, Prophet, Exp Smoothing)
- **Scalability:** Batch pipeline for 10+ products simultaneously

### Simulation Performance (90-day test)
| Metric | Result |
|--------|--------|
| **Service Level** | 88.9% |
| **Stockout Rate** | 1.1% |
| **Avg Inventory** | 5.8 units |
| **Total Cost** | $271 |

**Business Impact:** Quantified the cost-service trade-off, demonstrating how forecasting drives inventory decisions.

---

## 📊 Dataset

- **Source:** [M5 Walmart Forecasting Competition](https://www.kaggle.com/c/m5-forecasting-accuracy)
- **Products:** 10 FOODS category items
- **Time Span:** 5+ years (2011-2016, 1,885 days)
- **Features:** 61 engineered features
- **Challenge:** 61.8% average zero-sales days (intermittent demand)

---

## 🛠️ Technologies Used

| Category | Technologies |
|----------|-------------|
| **Core** | Python 3.12, Pandas, NumPy |
| **Forecasting** | Statsmodels (ARIMA), Prophet, Scikit-learn |
| **Simulation** | Custom DES engine, Object-oriented design |
| **Visualization** | Matplotlib, Seaborn |
| **Development** | Jupyter Notebooks, Git |

---

## 📁 Project Structure
```
autonomous-supply-chain-twin/
├── data/
│   ├── raw/m5/                    # Original M5 dataset (gitignored)
│   └── processed/                 # Processed data & features
├── notebooks/
│   ├── 01_exploration/
│   │   └── m5_data_exploration.ipynb
│   ├── 02_modeling/
│   │   ├── baseline_forecasting_models.ipynb
│   │   ├── advanced_forecasting_models.ipynb
│   │   └── multi_product_forecasting.ipynb
│   ├── 03_simulation/
│   │   └── supply_chain_digital_twin.ipynb
│   └── 04_reinforcement_learning/
│       └── rl_inventory_agent.ipynb
├── src/
│   ├── data_generation/           # Preprocessing & features
│   ├── forecasting/               # Model implementations
│   ├── simulation/                # Digital twin engine
│   └── utils/                     # Config, logging, metrics
├── scripts/                       # Utility scripts
├── docker/                        # Dockerfile & docker-compose
├── configs/                       # YAML configuration
├── results/                       # Model outputs & KPIs (CSV)
├── docs/                          # Documentation & presentations
└── requirements.txt               # Dependencies
```

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/victorgvc-hes/autonomous-supply-chain-twin.git
cd autonomous-supply-chain-twin
```

### 2. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate.bat
pip install -r requirements.txt
```

### 3. Download Data
```bash
# Configure Kaggle API credentials
# Place kaggle.json in ~/.kaggle/

python src/utils/download_m5_data.py
```

### 4. Run Notebooks
```bash
jupyter notebook
```

Navigate to `notebooks/` and run in order:
1. `01_exploration/m5_data_exploration.ipynb`
2. `02_modeling/baseline_forecasting_models.ipynb`
3. `02_modeling/advanced_forecasting_models.ipynb`
4. `02_modeling/multi_product_forecasting.ipynb`
5. `03_simulation/supply_chain_digital_twin.ipynb`
6. `04_reinforcement_learning/rl_inventory_agent.ipynb`

### Alternative: Run with Docker

```bash
# Build and start the container (Jupyter Lab on port 8888)
cd docker
docker-compose up --build

# Open in browser: http://localhost:8888
```

Ports exposed by the container:

| Port | Service |
|------|---------|
| 8888 | Jupyter Lab |
| 8501 | Streamlit (future dashboard) |
| 8050 | Dash (future dashboard) |
| 6006 | TensorBoard |

---

## 📈 Methodology

### Phase 1: Exploratory Data Analysis
- Seasonality analysis (weekly, monthly, yearly patterns)
- Event & price impact analysis
- Feature correlation studies
- Intermittent demand characterization

### Phase 2: Forecasting Models
**Baseline Models:**
- Naive forecast
- Seasonal Naive (weekly)
- Moving Average (7-day, 28-day)
- Historical Mean

**Advanced Models:**
- ARIMA with auto parameter selection
- Prophet (Meta/Facebook)
- Exponential Smoothing (seasonal)

### Phase 3: Multi-Product Scaling
- Batch forecasting pipeline
- Automated model comparison
- Performance benchmarking across products
- Ensemble recommendations

### Phase 4: Digital Twin Simulation
- Discrete Event Simulation (DES)
- Reorder Point (ROP) inventory policy
- Lead time & safety stock handling
- KPI tracking: service level, costs, stockouts

---

## 🎓 Key Features

### 1. Feature Engineering Pipeline
- **61 automated features** including:
  - Lag features (7, 14, 21, 28 days)
  - Rolling statistics (mean, std, min, max)
  - Calendar features (cyclical encoding)
  - Price features (momentum, changes)
  - Hierarchical aggregations (store, category, state)

### 2. Multi-Model Framework
- Unified evaluation across 8 models
- Consistent train/test splitting
- Standardized metrics (RMSE, MAE, MAPE)
- Model selection per product

### 3. Digital Twin Capabilities
- Daily inventory simulation
- Forecast-driven ordering
- Cost optimization (holding vs stockout)
- What-if scenario testing
- Policy comparison framework

---

## 📊 Results & Insights

### Finding 1: No Single Model Dominates
- **ARIMA:** 30% of products
- **Prophet:** 30% of products
- **MA-28:** 30% of products
- **MA-7:** 10% of products

**Implication:** Ensemble or product-specific model selection recommended.

### Finding 2: Intermittent Demand is Challenging
- 61.8% of days have zero sales
- Unpredictable spikes (max 4 units in single day)
- Simple models often match complex methods

**Implication:** Focus on robust, interpretable methods for sparse data.

### Finding 3: Simulation Quantifies Trade-offs
- Higher safety stock → Higher service level + Higher holding cost
- Lower safety stock → Lower costs + More stockouts

**Implication:** Digital twin enables data-driven policy optimization.

---

## 🔮 Future Enhancements

- [x] **Reinforcement Learning experiment** (Q-Learning vs rule-based — completed, see `notebooks/04_reinforcement_learning/`)
- [ ] **Advanced RL** (DQN / multi-agent for dense-demand products)
- [ ] **Network-level simulation** (multi-store coordination)
- [ ] **Interactive dashboard** (Streamlit deployment)
- [ ] **Real-time API** for production deployment
- [ ] **Causal inference** (DoWhy, EconML) for demand drivers
- [ ] **Probabilistic forecasting** (prediction intervals)

---

## 📚 Documentation

- [Executive Summary](docs/EXECUTIVE_SUMMARY.md)
- [RL Experiment Summary](docs/RL_EXPERIMENT_SUMMARY.md)
- [Quick Start Guide](docs/QUICK_START.md)
- [Results Summary](RESULTS_SUMMARY.md)
- [Executive Presentation Script](docs/PRESENTATION_SCRIPT_EXECUTIVE_FINAL.md)
- [Technical Presentation Script](docs/PRESENTATION_SCRIPT_TECHNICAL_FINAL.md)

---

## 👤 Author

**Victor Vergara**
- LinkedIn: https://www.linkedin.com/in/victor-vergara075/
- Email: victorgvc@gmail.com
- Portfolio: https://github.com/victorgvc-hes?tab=repositories

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **M5 Walmart Dataset:** Kaggle Competition
- **Libraries:** Statsmodels, Prophet, Scikit-learn, Pandas
- **Inspiration:** Real-world supply chain challenges

---

## ⭐ Project Highlights

This project demonstrates:
- ✅ **End-to-end thinking** (data → forecast → simulate → decide)
- ✅ **Business value quantification** (not just model accuracy)
- ✅ **Production-ready code** (clean, documented, reproducible)
- ✅ **Domain expertise** (supply chain + AI/ML combined)
- ✅ **Scalable architecture** (multi-product batch processing)

**Portfolio Status: Top 5% tier** 🌟

---

*Built with ❤️ for supply chain optimization*
"""