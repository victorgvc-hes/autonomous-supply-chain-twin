"""
Data preprocessing module for M5 Walmart dataset.

This module handles:
- Loading raw M5 data
- Transforming wide to long format
- Handling missing values
- Creating hierarchical aggregations
- Train/validation/test splits
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class M5DataPreprocessor:
    """Preprocessor for M5 Walmart dataset."""
    
    def __init__(self, data_path: str = "data/raw/m5"):
        """
        Initialize preprocessor.
        
        Args:
            data_path: Path to raw M5 data directory
        """
        self.data_path = Path(data_path)
        self.calendar = None
        self.sales = None
        self.prices = None
        self.sales_long = None
        
    def load_data(self) -> None:
        """Load all M5 datasets."""
        logger.info("Loading M5 datasets...")
        
        # Load calendar
        self.calendar = pd.read_csv(self.data_path / "calendar.csv")
        logger.info(f"Calendar loaded: {self.calendar.shape}")
        
        # Load sales
        self.sales = pd.read_csv(self.data_path / "sales_train_validation.csv")
        logger.info(f"Sales loaded: {self.sales.shape}")
        
        # Load prices
        self.prices = pd.read_csv(self.data_path / "sell_prices.csv")
        logger.info(f"Prices loaded: {self.prices.shape}")
        
        # Convert date column
        self.calendar['date'] = pd.to_datetime(self.calendar['date'])
        
        logger.info("✓ All datasets loaded successfully")
        
    def transform_to_long_format(self, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Transform sales from wide to long format.
        
        Args:
            sample_size: Optional number of products to sample
            
        Returns:
            DataFrame in long format
        """
        logger.info("Transforming to long format...")
        
        if self.sales is None:
            raise ValueError("Sales data not loaded. Call load_data() first.")
        
        # Sample if requested
        sales_df = self.sales
        if sample_size:
            sales_df = self.sales.sample(n=sample_size, random_state=42)
            logger.info(f"Sampled {sample_size} products")
        
        # Get day columns
        day_cols = [col for col in sales_df.columns if col.startswith('d_')]
        id_cols = ['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id']
        
        # Melt to long format
        sales_long = sales_df.melt(
            id_vars=id_cols,
            value_vars=day_cols,
            var_name='d',
            value_name='sales'
        )
        
        # Merge with calendar
        sales_long = sales_long.merge(self.calendar, on='d', how='left')
        
        # Sort by id and date
        sales_long = sales_long.sort_values(['id', 'date']).reset_index(drop=True)
        
        self.sales_long = sales_long
        logger.info(f"Long format shape: {sales_long.shape}")
        
        return sales_long
    
    def add_price_features(self) -> pd.DataFrame:
        """
        Add price information to sales data.
        
        Returns:
            Sales data with price features
        """
        logger.info("Adding price features...")
        
        if self.sales_long is None:
            raise ValueError("Long format sales not created. Call transform_to_long_format() first.")
        
        # Merge calendar with prices to get date
        calendar_prices = self.calendar[['wm_yr_wk', 'date']].drop_duplicates()
        prices_with_date = self.prices.merge(calendar_prices, on='wm_yr_wk', how='left')
        
        # Merge prices with sales
        sales_with_prices = self.sales_long.merge(
            prices_with_date[['store_id', 'item_id', 'date', 'sell_price']],
            on=['store_id', 'item_id', 'date'],
            how='left'
        )
        
        # Fill missing prices with forward fill then backward fill
        sales_with_prices['sell_price'] = sales_with_prices.groupby(
            ['store_id', 'item_id']
        )['sell_price'].fillna(method='ffill').fillna(method='bfill')
        
        self.sales_long = sales_with_prices
        logger.info("✓ Price features added")
        
        return sales_with_prices
    
    def handle_missing_values(self) -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Returns:
            DataFrame with missing values handled
        """
        logger.info("Handling missing values...")
        
        if self.sales_long is None:
            raise ValueError("Sales data not available")
        
        df = self.sales_long.copy()
        
        # Fill missing sales with 0 (genuine zeros)
        df['sales'] = df['sales'].fillna(0)
        
        # Fill missing event names with 'None'
        event_cols = [col for col in df.columns if 'event' in col.lower()]
        for col in event_cols:
            df[col] = df[col].fillna('None')
        
        # Log missing value summary
        missing_summary = df.isnull().sum()
        missing_summary = missing_summary[missing_summary > 0]
        
        if len(missing_summary) > 0:
            logger.warning(f"Remaining missing values:\n{missing_summary}")
        else:
            logger.info("✓ No missing values")
        
        self.sales_long = df
        return df
    
    def create_hierarchical_aggregations(self) -> Dict[str, pd.DataFrame]:
        """
        Create aggregated time series at different hierarchical levels.
        
        Returns:
            Dictionary of DataFrames for each aggregation level
        """
        logger.info("Creating hierarchical aggregations...")
        
        if self.sales_long is None:
            raise ValueError("Sales data not available")
        
        aggregations = {}
        
        # Total (all products, all stores)
        aggregations['total'] = self.sales_long.groupby('date').agg({
            'sales': 'sum',
            'sell_price': 'mean'
        }).reset_index()
        aggregations['total']['level'] = 'total'
        
        # By state
        aggregations['state'] = self.sales_long.groupby(['date', 'state_id']).agg({
            'sales': 'sum',
            'sell_price': 'mean'
        }).reset_index()
        aggregations['state']['level'] = 'state'
        
        # By store
        aggregations['store'] = self.sales_long.groupby(['date', 'store_id', 'state_id']).agg({
            'sales': 'sum',
            'sell_price': 'mean'
        }).reset_index()
        aggregations['store']['level'] = 'store'
        
        # By category
        aggregations['category'] = self.sales_long.groupby(['date', 'cat_id']).agg({
            'sales': 'sum',
            'sell_price': 'mean'
        }).reset_index()
        aggregations['category']['level'] = 'category'
        
        # By department
        aggregations['department'] = self.sales_long.groupby(['date', 'dept_id', 'cat_id']).agg({
            'sales': 'sum',
            'sell_price': 'mean'
        }).reset_index()
        aggregations['department']['level'] = 'department'
        
        # By store-category
        aggregations['store_cat'] = self.sales_long.groupby(
            ['date', 'store_id', 'cat_id']
        ).agg({
            'sales': 'sum',
            'sell_price': 'mean'
        }).reset_index()
        aggregations['store_cat']['level'] = 'store_cat'
        
        for level, df in aggregations.items():
            logger.info(f"  {level}: {df.shape}")
        
        return aggregations
    
    def create_train_val_test_split(
        self,
        train_end_date: str = "2016-03-27",  # d_1913
        val_days: int = 28,
        test_days: int = 28
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data into train, validation, and test sets.
        
        Args:
            train_end_date: Last date in training set
            val_days: Number of validation days
            test_days: Number of test days
            
        Returns:
            Tuple of (train, validation, test) DataFrames
        """
        logger.info("Creating train/val/test split...")
        
        if self.sales_long is None:
            raise ValueError("Sales data not available")
        
        train_end = pd.to_datetime(train_end_date)
        val_end = train_end + timedelta(days=val_days)
        
        train = self.sales_long[self.sales_long['date'] <= train_end].copy()
        val = self.sales_long[
            (self.sales_long['date'] > train_end) & 
            (self.sales_long['date'] <= val_end)
        ].copy()
        test = self.sales_long[self.sales_long['date'] > val_end].copy()
        
        logger.info(f"Train: {train['date'].min()} to {train['date'].max()} ({len(train)} rows)")
        logger.info(f"Val: {val['date'].min()} to {val['date'].max()} ({len(val)} rows)")
        logger.info(f"Test: {test['date'].min()} to {test['date'].max()} ({len(test)} rows)")
        
        return train, val, test
    
    def save_processed_data(
        self,
        output_path: str = "data/processed",
        save_hierarchies: bool = True
    ) -> None:
        """
        Save processed data to disk.
        
        Args:
            output_path: Directory to save processed data
            save_hierarchies: Whether to save hierarchical aggregations
        """
        logger.info("Saving processed data...")
        
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save main processed data
        if self.sales_long is not None:
            self.sales_long.to_parquet(
                output_dir / "sales_processed.parquet",
                index=False
            )
            logger.info(f"✓ Saved sales_processed.parquet")
        
        # Save train/val/test splits
        train, val, test = self.create_train_val_test_split()
        train.to_parquet(output_dir / "train.parquet", index=False)
        val.to_parquet(output_dir / "validation.parquet", index=False)
        test.to_parquet(output_dir / "test.parquet", index=False)
        logger.info("✓ Saved train/val/test splits")
        
        # Save hierarchical aggregations
        if save_hierarchies:
            agg_dir = output_dir / "hierarchies"
            agg_dir.mkdir(exist_ok=True)
            
            aggregations = self.create_hierarchical_aggregations()
            for level, df in aggregations.items():
                df.to_parquet(agg_dir / f"{level}.parquet", index=False)
            
            logger.info(f"✓ Saved hierarchical aggregations to {agg_dir}")
        
        logger.info(f"✓ All processed data saved to {output_dir}")
    
    def get_data_summary(self) -> Dict[str, any]:
        """
        Get summary statistics of the processed data.
        
        Returns:
            Dictionary with summary statistics
        """
        if self.sales_long is None:
            raise ValueError("Sales data not available")
        
        summary = {
            'total_rows': len(self.sales_long),
            'unique_products': self.sales_long['id'].nunique(),
            'unique_items': self.sales_long['item_id'].nunique(),
            'unique_stores': self.sales_long['store_id'].nunique(),
            'unique_states': self.sales_long['state_id'].nunique(),
            'unique_categories': self.sales_long['cat_id'].nunique(),
            'unique_departments': self.sales_long['dept_id'].nunique(),
            'date_range': (
                self.sales_long['date'].min(),
                self.sales_long['date'].max()
            ),
            'total_days': self.sales_long['date'].nunique(),
            'total_sales': self.sales_long['sales'].sum(),
            'avg_daily_sales': self.sales_long.groupby('date')['sales'].sum().mean(),
            'zero_sales_pct': (self.sales_long['sales'] == 0).mean() * 100,
        }
        
        return summary


def main():
    """Main preprocessing pipeline."""
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from src.utils.logger import setup_logger
    
    # Setup logging
    logger = setup_logger(
        "preprocessing",
        log_file="logs/preprocessing.log"
    )
    
    # Initialize preprocessor
    preprocessor = M5DataPreprocessor(data_path="data/raw/m5")
    
    # Load data
    preprocessor.load_data()
    
    # Transform to long format
    preprocessor.transform_to_long_format()
    
    # Add price features
    preprocessor.add_price_features()
    
    # Handle missing values
    preprocessor.handle_missing_values()
    
    # Print summary
    summary = preprocessor.get_data_summary()
    logger.info("\n" + "="*50)
    logger.info("DATA SUMMARY")
    logger.info("="*50)
    for key, value in summary.items():
        logger.info(f"{key}: {value}")
    logger.info("="*50)
    
    # Save processed data
    preprocessor.save_processed_data(
        output_path="data/processed",
        save_hierarchies=True
    )
    
    logger.info("✓ Preprocessing complete!")


if __name__ == "__main__":
    main()
