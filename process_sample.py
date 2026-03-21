import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from src.data_generation.preprocess import M5DataPreprocessor

print("Processing SAMPLE data only...")

# Use sample data
preprocessor = M5DataPreprocessor(data_path="data/processed/sample")
preprocessor.load_data()
preprocessor.transform_to_long_format()
preprocessor.add_price_features()
preprocessor.handle_missing_values()

# Save
preprocessor.save_processed_data(
    output_path="data/processed",
    save_hierarchies=False
)

print("✓ Sample processing complete!")