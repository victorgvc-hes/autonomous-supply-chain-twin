# Guía de Inicio Rápido - ASCDT

Esta guía te ayudará a configurar y ejecutar el proyecto paso a paso.

## Requisitos Previos

- Python 3.10 o superior
- Git
- 10+ GB de espacio en disco (para datos M5)
- Cuenta de Kaggle (para descargar datos)

## Paso 1: Clonar o Descargar el Proyecto

```bash
# Si tienes el proyecto en GitHub
git clone https://github.com/tu-usuario/autonomous-supply-chain-twin.git
cd autonomous-supply-chain-twin

# O si descargaste el ZIP
cd autonomous-supply-chain-twin
```

## Paso 2: Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

## Paso 3: Instalar Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar todas las dependencias
pip install -r requirements.txt

# Esto puede tomar varios minutos
```

## Paso 4: Configurar Kaggle API

Para descargar los datos M5 de Walmart:

### 4.1 Obtener Credenciales de Kaggle

1. Ve a https://www.kaggle.com
2. Inicia sesión o crea una cuenta
3. Ve a "Account" → "Settings"
4. Scroll down hasta "API" section
5. Click "Create New API Token"
6. Esto descargará `kaggle.json`

### 4.2 Instalar Credenciales

```bash
# Linux/Mac
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Windows
mkdir %USERPROFILE%\.kaggle
move %USERPROFILE%\Downloads\kaggle.json %USERPROFILE%\.kaggle\
```

### 4.3 Aceptar Reglas de la Competencia

1. Ve a: https://www.kaggle.com/c/m5-forecasting-accuracy/rules
2. Click "I Understand and Accept"

## Paso 5: Descargar Datos M5

```bash
# Descargar dataset completo (puede tomar 10-15 minutos)
python src/utils/download_m5_data.py

# Para crear también un subset pequeño para pruebas rápidas:
python src/utils/download_m5_data.py --create-sample --sample-size 100
```

Esto descargará:
- `calendar.csv` (20 KB)
- `sales_train_validation.csv` (125 MB)
- `sell_prices.csv` (143 MB)
- `sample_submission.csv` (114 MB)

## Paso 6: Procesar Datos

```bash
# Ejecutar pipeline de preprocesamiento
python src/data_generation/preprocess.py
```

Esto creará:
- `data/processed/sales_processed.parquet`
- `data/processed/train.parquet`
- `data/processed/validation.parquet`
- `data/processed/test.parquet`
- `data/processed/hierarchies/` (agregaciones)

## Paso 7: Crear Features

```bash
# Ejecutar feature engineering
python src/data_generation/features.py
```

## Paso 8: Explorar Datos (Opcional)

```bash
# Iniciar Jupyter
jupyter notebook

# Abrir: notebooks/01_exploration/m5_data_analysis.ipynb
# Ejecutar todas las celdas para ver visualizaciones
```

## Verificación del Setup

Ejecuta este script para verificar que todo está configurado correctamente:

```python
# verify_setup.py
import sys
from pathlib import Path

print("Verificando setup...\n")

# 1. Check Python version
print(f"✓ Python version: {sys.version}")

# 2. Check key imports
try:
    import pandas as pd
    import numpy as np
    import torch
    print("✓ Core libraries importadas")
except ImportError as e:
    print(f"✗ Error importando libraries: {e}")

# 3. Check data files
data_path = Path("data/raw/m5")
required_files = ["calendar.csv", "sales_train_validation.csv", "sell_prices.csv"]
all_present = all((data_path / f).exists() for f in required_files)

if all_present:
    print("✓ Datos M5 descargados")
else:
    print("✗ Datos M5 no encontrados")

# 4. Check processed data
processed_path = Path("data/processed")
if (processed_path / "train.parquet").exists():
    print("✓ Datos procesados")
else:
    print("ℹ Ejecuta: python src/data_generation/preprocess.py")

print("\n✅ Setup completo!")
```

Guarda esto como `verify_setup.py` y ejecuta:

```bash
python verify_setup.py
```

## Próximos Pasos

Una vez que hayas completado el setup:

### Semana 2: Modelos Baseline

```bash
# 1. Entrenar modelos baseline
python src/forecasting/baseline.py

# 2. Evaluar performance
python src/forecasting/evaluate.py
```

### Exploración y Experimentación

```bash
# Abrir notebooks para análisis interactivo
jupyter notebook

# Notebooks clave:
# - 01_exploration/m5_data_analysis.ipynb
# - 02_modeling/baseline_models.ipynb
```

## Solución de Problemas

### Error: "kaggle.json not found"

```bash
# Verificar ubicación
ls ~/.kaggle/kaggle.json  # Linux/Mac
dir %USERPROFILE%\.kaggle\kaggle.json  # Windows

# Si no existe, repetir Paso 4
```

### Error: "Competition rules not accepted"

Ir a: https://www.kaggle.com/c/m5-forecasting-accuracy/rules
Click "I Understand and Accept"

### Error de memoria al procesar datos

Si tienes poca RAM (<8GB), usa el sample:

```bash
# Usar solo subset pequeño
python src/data_generation/preprocess.py --sample-size 100
```

### Error con PyTorch / CUDA

```bash
# Para CPU only (si no tienes GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## Comandos Útiles

```bash
# Ver estructura del proyecto
tree -L 2

# Limpiar archivos temporales
find . -type d -name __pycache__ -exec rm -rf {} +

# Ver tamaño de datos
du -sh data/*

# Ejecutar tests
pytest tests/

# Formatear código
black src/
```

## Recursos Adicionales

- [Roadmap Completo](docs/PROJECT_ROADMAP.md)
- [Documentación M5](https://www.kaggle.com/c/m5-forecasting-accuracy/data)
- [PyTorch Forecasting Docs](https://pytorch-forecasting.readthedocs.io/)
- [Ray RLlib Docs](https://docs.ray.io/en/latest/rllib/)

## Soporte

Si encuentras problemas:
1. Revisa esta guía
2. Consulta [PROJECT_ROADMAP.md](docs/PROJECT_ROADMAP.md)
3. Revisa issues en GitHub
4. Abre un nuevo issue con detalles del error

---

**¡Éxito con tu proyecto!** 🚀
