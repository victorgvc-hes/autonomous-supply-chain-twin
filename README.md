# Advanced AI-Powered Demand Forecasting & Inventory Optimization System

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-A31F34?logo=opensourceinitiative&logoColor=white)](https://opensource.org/licenses/MIT)
[![Status: Active](https://img.shields.io/badge/Status-Active-2EA44F)]()
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)]()
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?logo=jupyter&logoColor=white)]()
[![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)]()

[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)]()
[![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)]()
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?logo=scikitlearn&logoColor=white)]()
[![Statsmodels](https://img.shields.io/badge/Statsmodels-2C3E50?logoColor=white)]()
[![Prophet](https://img.shields.io/badge/Prophet-0F172A?logoColor=white)]()
[![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?logoColor=white)]()
[![Seaborn](https://img.shields.io/badge/Seaborn-4C72B0?logoColor=white)]()
[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?logo=kaggle&logoColor=white)]()

An end-to-end AI-powered supply chain system that combines demand forecasting, digital twin simulation, and inventory optimisation for products with intermittent demand patterns.

---

## Project Overview

This project presents a complete AI and analytics pipeline for improving inventory decisions in retail environments where demand is sparse, irregular, and difficult to predict.

It integrates machine learning forecasting, multi-product evaluation, and discrete event simulation to support better reorder policies, stronger service levels, and lower inventory-related costs.

### The Challenge

Retailers managing products with intermittent demand often face three major problems:

- **Overstocking** increases holding costs and ties up working capital.
- **Understocking** leads to missed sales and weaker customer service.
- **Traditional forecasting methods** often perform poorly when demand contains many zero-sales days and unpredictable spikes.

### The Solution

**ASCDT** provides an end-to-end framework that:

1. Forecasts future demand using multiple statistical and machine learning approaches.
2. Simulates inventory operations through a digital twin environment.
3. Evaluates reorder policies using cost-versus-service trade-offs.
4. Scales analysis across multiple products through batch processing.

---

## Key Results

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

## Dataset

- **Source:** [M5 Walmart Forecasting Competition](https://www.kaggle.com/c/m5-forecasting-accuracy)
- **Products:** 10 FOODS category items
- **Time Span:** 5+ years (2011-2016, 1,885 days)
- **Features:** 61 engineered features
- **Challenge:** 61.8% average zero-sales days (intermittent demand)

---

## Technologies Used

| Category | Technologies |
|----------|-------------|
| **Core** | Python 3.12, Pandas, NumPy |
| **Forecasting** | Statsmodels (ARIMA), Prophet, Scikit-learn |
| **Simulation** | Custom DES engine, Object-oriented design |
| **Visualization** | Matplotlib, Seaborn |
| **Development** | Jupyter Notebooks, Git |

---

## Project Structure
```text
autonomous-supply-chain-twin/
├── data/
│   ├── raw/m5/                    # Original M5 dataset (gitignored)
│   └── processed/                 # Cleaned data and engineered features
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
│   ├── data_generation/           # Data preprocessing and feature engineering
│   ├── forecasting/               # Forecasting model implementations
│   ├── simulation/                # Digital twin and DES engine
│   └── utils/                     # Configuration, logging, and metrics
├── scripts/                       # Utility and execution scripts
├── docker/                        # Dockerfile and docker-compose setup
├── configs/                       # YAML configuration files
├── results/                       # Forecast outputs and KPI results
├── docs/                          # Documentation and presentation materials
└── requirements.txt               # Python dependencies
```

---

## Quick Start

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
### 4. Run the Notebooks
```bash
jupyter notebook
```

Then navigate to the `notebooks/` directory and run the notebooks in the following order:

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
```

Open the following address in your browser:

```text
http://localhost:8888
```

### Exposed Ports

| Port | Service |
|------|---------|
| 8888 | Jupyter Lab |
| 8501 | Streamlit (future dashboard) |
| 8050 | Dash (future dashboard) |
| 6006 | TensorBoard |

---
## Methodology

The project follows a structured four-phase methodology designed to move from data understanding to forecasting, simulation, and decision support.

### Phase 1: Exploratory Data Analysis
- Seasonality analysis across weekly, monthly, and yearly patterns
- Event and price impact analysis
- Feature correlation assessment
- Intermittent demand characterisation

### Phase 2: Forecasting Models

**Baseline Models**
- Naive forecast
- Seasonal Naive (weekly)
- Moving Average (7-day and 28-day)
- Historical Mean

**Advanced Models**
- ARIMA with automatic parameter selection
- Prophet (Meta/Facebook)
- Seasonal Exponential Smoothing

### Phase 3: Multi-Product Scaling
- Batch forecasting pipeline
- Automated model comparison
- Performance benchmarking across products
- Ensemble model recommendations

### Phase 4: Digital Twin Simulation
- Discrete Event Simulation (DES)
- Reorder Point (ROP) inventory policy
- Lead time and safety stock modelling
- KPI tracking for service level, costs, and stockouts

---
## Key Features

### 1. Feature Engineering Pipeline
- **61 engineered features**, including:
  - Lag features (7, 14, 21, and 28 days)
  - Rolling statistics (mean, standard deviation, minimum, and maximum)
  - Calendar features with cyclical encoding
  - Price-based features such as momentum and price changes
  - Hierarchical aggregations across store, category, and state levels

### 2. Multi-Model Forecasting Framework
- Unified evaluation across 8 forecasting models
- Consistent train/test splitting methodology
- Standardised performance metrics, including RMSE, MAE, and MAPE
- Product-level model selection

### 3. Digital Twin Capabilities
- Daily inventory simulation
- Forecast-driven replenishment decisions
- Cost optimisation across holding and stockout trade-offs
- What-if scenario testing
- Policy comparison framework

---

## Results & Insights

### Finding 1: No Single Model Dominates
- **ARIMA:** Best performer for 30% of products
- **Prophet:** Best performer for 30% of products
- **MA-28:** Best performer for 30% of products
- **MA-7:** Best performer for 10% of products

**Implication:**  
An ensemble approach or product-specific model selection strategy is more appropriate than relying on a single forecasting method.

### Finding 2: Intermittent Demand is Inherently Challenging
- 61.8% of days recorded zero sales
- Demand spikes were irregular and difficult to predict, with a maximum of 4 units sold in a single day
- Simpler models often performed as well as more complex alternatives

**Implication:**  
For sparse and intermittent demand, robust and interpretable forecasting approaches may be more effective than unnecessarily complex models.

### Finding 3: Simulation Quantifies Inventory Trade-offs
- Higher safety stock improves service level but increases holding cost
- Lower safety stock reduces cost but increases the risk of stockouts

**Implication:**  
The digital twin provides a practical framework for evaluating inventory policies and supporting data-driven decision-making.

---
## Future Enhancements

Planned next steps to further extend the project include:

- [x] **Reinforcement Learning experiment** (Q-Learning vs rule-based policies; completed, see `notebooks/04_reinforcement_learning/`)
- [ ] **Advanced Reinforcement Learning** (DQN or multi-agent approaches for dense-demand products)
- [ ] **Network-level simulation** (multi-store coordination and system-wide optimisation)
- [ ] **Interactive dashboard** (Streamlit-based deployment)
- [ ] **Real-time API** for production-oriented deployment
- [ ] **Causal inference** using DoWhy and EconML to analyse demand drivers
- [ ] **Probabilistic forecasting** with prediction intervals and uncertainty estimates

---

## Documentation

Project documentation includes:

- [Executive Summary](docs/EXECUTIVE_SUMMARY.md)
- [RL Experiment Summary](docs/RL_EXPERIMENT_SUMMARY.md)
- [Quick Start Guide](docs/QUICK_START.md)
- [Results Summary](RESULTS_SUMMARY.md)
- [Executive Presentation Script](docs/PRESENTATION_SCRIPT_EXECUTIVE_FINAL.md)
- [Technical Presentation Script](docs/PRESENTATION_SCRIPT_TECHNICAL_FINAL.md)

---

## Acknowledgments

- **M5 Walmart Forecasting Dataset:** Kaggle competition dataset
- **Core libraries:** Statsmodels, Prophet, Scikit-learn, and Pandas
- **Project inspiration:** Real-world supply chain and inventory management challenges

---

## Project Highlights

This project demonstrates:

- ✅ **End-to-end thinking** from data preparation to forecasting, simulation, and decision support
- ✅ **Business value quantification**, not just predictive performance
- ✅ **Production-ready code** that is clean, documented, and reproducible
- ✅ **Domain expertise** at the intersection of supply chain management and AI/ML
- ✅ **Scalable architecture** designed for multi-product analysis and batch processing

**Portfolio Positioning:** High-impact, senior-level supply chain AI project

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Author

**Victor Vergara**

Procurement and operations professional with 20+ years of experience in supply chain, analytics, and process improvement. Focused on applying AI/ML, forecasting, and digital transformation to real-world operational challenges.

- LinkedIn: https://www.linkedin.com/in/victor-vergara075/
- Email: victorgvc@gmail.com
- Portfolio: https://github.com/victorgvc-hes?tab=repositories

---
