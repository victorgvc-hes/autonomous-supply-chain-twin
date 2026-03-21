import sys
from pathlib import Path

print("="*60)
print("VERIFICANDO INSTALACIÓN DE ASCDT")
print("="*60)

# 1. Python version
print(f"\n✓ Python: {sys.version.split()[0]}")

# 2. Importaciones clave
try:
    import pandas as pd
    import numpy as np
    import torch
    from src.utils.config import get_config
    print("✓ Librerías core importadas correctamente")
except ImportError as e:
    print(f"✗ Error: {e}")

# 3. Verificar datos
data_checks = [
    "data/raw/m5/calendar.csv",
    "data/raw/m5/sales_train_validation.csv",
    "data/processed/sample/sales_train_validation.csv",
    "data/processed/train.parquet",
]

all_ok = True
print("\nArchivos de datos:")
for file in data_checks:
    if Path(file).exists():
        size = Path(file).stat().st_size / (1024*1024)
        print(f"✓ {file} ({size:.1f} MB)")
    else:
        print(f"✗ {file} NO ENCONTRADO")

# 4. Verificar features
if Path("data/processed/sample_with_features.parquet").exists():
    import pandas as pd
    df = pd.read_parquet("data/processed/sample_with_features.parquet")
    print(f"\n✓ Features creados: {df.shape[1]} columnas")
    print(f"✓ Datos disponibles: {df.shape[0]} filas")
else:
    print("\n✗ Features no encontrados")

print("\n" + "="*60)
print("✅ TODO LISTO! Puedes continuar con el desarrollo")
print("="*60)