#!/bin/bash

# Crear estructura de directorios
mkdir -p src/{data_generation,forecasting,simulation,agents,causal,dashboard,utils}
mkdir -p data/{raw,processed,synthetic}
mkdir -p experiments/{baseline,disruption,new_product,systemic_optimization}
mkdir -p notebooks/{01_exploration,02_modeling,03_simulation,04_rl}
mkdir -p tests/{unit,integration}
mkdir -p docs/{architecture,tutorials}
mkdir -p results/{figures,metrics,videos}
mkdir -p docker
mkdir -p configs
mkdir -p logs
mkdir -p models
mkdir -p checkpoints

# Crear archivos __init__.py
touch src/__init__.py
touch src/data_generation/__init__.py
touch src/forecasting/__init__.py
touch src/simulation/__init__.py
touch src/agents/__init__.py
touch src/causal/__init__.py
touch src/dashboard/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

echo "✅ Estructura del proyecto creada"
