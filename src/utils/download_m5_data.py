"""
Download M5 Walmart dataset from Kaggle.

This script downloads the M5 Forecasting - Accuracy competition data.
You need to have Kaggle API credentials configured.

Setup:
1. Create Kaggle account and get API token from kaggle.com/settings
2. Place kaggle.json in ~/.kaggle/ (Linux/Mac) or C:\\Users\\<username>\\.kaggle (Windows)
3. Run: chmod 600 ~/.kaggle/kaggle.json
"""

import os
import zipfile
from pathlib import Path
import sys
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger

logger = setup_logger(__name__, log_file="logs/data_download.log")


def download_m5_data(data_dir: str = "data/raw/m5"):
    """
    Download M5 dataset from Kaggle.
    
    Args:
        data_dir: Directory to save the data
    """
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting M5 data download...")
    
    try:
        # Check if kaggle is installed
        import kaggle
        logger.info("Kaggle API found")
        
    except ImportError:
        logger.error("Kaggle API not installed.")
        logger.error("Install with: pip install kaggle")
        logger.error("\nSetup instructions:")
        logger.error("1. Go to kaggle.com/settings")
        logger.error("2. Click 'Create New API Token'")
        logger.error("3. Move downloaded kaggle.json to ~/.kaggle/")
        logger.error("4. Run: chmod 600 ~/.kaggle/kaggle.json")
        return
    
    # Download dataset
    competition_name = "m5-forecasting-accuracy"
    
    logger.info(f"Downloading {competition_name} dataset...")
    logger.info("This may take several minutes...")
    
    try:
        # Download all files
        kaggle.api.competition_download_files(
            competition_name,
            path=data_path,
            quiet=False
        )
        
        # Extract zip files
        zip_file = data_path / f"{competition_name}.zip"
        
        if zip_file.exists():
            logger.info(f"Extracting {zip_file}...")
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(data_path)
            
            # Remove zip file
            zip_file.unlink()
            logger.info("Extraction complete")
        
        # Verify files
        required_files = [
            "calendar.csv",
            "sales_train_validation.csv",
            "sell_prices.csv",
            "sample_submission.csv"
        ]
        
        missing_files = []
        for file in required_files:
            file_path = data_path / file
            if file_path.exists():
                file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                logger.info(f"✓ {file} ({file_size:.2f} MB)")
            else:
                missing_files.append(file)
                logger.warning(f"✗ {file} not found")
        
        if missing_files:
            logger.error(f"Missing files: {missing_files}")
        else:
            logger.info("\n" + "="*60)
            logger.info("M5 DATASET INFORMATION")
            logger.info("="*60)
            logger.info("Competition: M5 Forecasting - Accuracy")
            logger.info("Source: Walmart")
            logger.info("Products: 3,049 items")
            logger.info("Stores: 10 stores across 3 states (CA, TX, WI)")
            logger.info("Time period: 2011-01-29 to 2016-06-19 (1,969 days)")
            logger.info("Departments: 3 (FOODS, HOBBIES, HOUSEHOLD)")
            logger.info("Categories: 7")
            logger.info("="*60)
            logger.info("\n✓ All required files downloaded successfully!")
            
    except Exception as e:
        logger.error(f"Error downloading data: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Ensure you have accepted competition rules at:")
        logger.error("   https://www.kaggle.com/c/m5-forecasting-accuracy/rules")
        logger.error("2. Check your Kaggle API credentials are set up correctly")
        logger.error("3. Verify ~/.kaggle/kaggle.json exists with valid credentials")


def create_sample_subset(data_dir: str = "data/raw/m5", sample_size: int = 100):
    """
    Create a small sample for quick testing.
    
    Args:
        data_dir: Directory containing M5 data
        sample_size: Number of products to include in sample
    """
    import pandas as pd
    
    data_path = Path(data_dir)
    sample_path = Path("data/processed/sample")
    sample_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Creating sample subset with {sample_size} products...")
    
    try:
        # Load sales data
        sales = pd.read_csv(data_path / "sales_train_validation.csv")
        
        # Sample random products
        sampled_products = sales.sample(n=min(sample_size, len(sales)), random_state=42)
        
        # Save sample
        sampled_products.to_csv(sample_path / "sales_sample.csv", index=False)
        
        # Copy other files
        for file in ["calendar.csv", "sell_prices.csv"]:
            df = pd.read_csv(data_path / file)
            
            # Filter prices for sampled products
            if file == "sell_prices.csv":
                item_ids = sampled_products['item_id'].unique()
                df = df[df['item_id'].isin(item_ids)]
            
            df.to_csv(sample_path / file, index=False)
        
        logger.info(f"✓ Sample data saved to {sample_path}")
        logger.info(f"  - {len(sampled_products)} products")
        logger.info(f"  - Ready for quick experimentation")
        
    except Exception as e:
        logger.error(f"Error creating sample: {e}")
        logger.error("Make sure M5 data has been downloaded first")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download M5 Walmart dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download full dataset
  python src/utils/download_m5_data.py
  
  # Download and create sample
  python src/utils/download_m5_data.py --create-sample
  
  # Create sample with custom size
  python src/utils/download_m5_data.py --create-sample --sample-size 50
        """
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/raw/m5",
        help="Directory to save data (default: data/raw/m5)"
    )
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create a small sample subset for testing"
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=100,
        help="Number of products in sample (default: 100)"
    )
    
    args = parser.parse_args()
    
    # Download data
    download_m5_data(args.data_dir)
    
    # Create sample if requested
    if args.create_sample:
        create_sample_subset(args.data_dir, args.sample_size)
    
    logger.info("\n✓ Done!")
