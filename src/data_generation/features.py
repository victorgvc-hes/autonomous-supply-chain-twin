"""
Feature engineering module for demand forecasting.

Creates features from raw M5 data including:
- Lag features
- Rolling statistics
- Calendar features
- Price features
- Event encodings
- Hierarchical features
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering for time series forecasting."""
    
    def __init__(self):
        """Initialize feature engineer."""
        self.feature_names = []
        
    def create_lag_features(
        self,
        df: pd.DataFrame,
        target_col: str = 'sales',
        lags: List[int] = [7, 14, 21, 28],
        group_cols: List[str] = ['id']
    ) -> pd.DataFrame:
        """
        Create lag features.
        
        Args:
            df: Input DataFrame
            target_col: Column to create lags for
            lags: List of lag periods
            group_cols: Columns to group by
            
        Returns:
            DataFrame with lag features added
        """
        logger.info(f"Creating lag features: {lags}")
        
        df_copy = df.copy()
        
        for lag in lags:
            feature_name = f'{target_col}_lag_{lag}'
            df_copy[feature_name] = df_copy.groupby(group_cols)[target_col].shift(lag)
            self.feature_names.append(feature_name)
        
        logger.info(f"✓ Created {len(lags)} lag features")
        return df_copy
    
    def create_rolling_features(
        self,
        df: pd.DataFrame,
        target_col: str = 'sales',
        windows: List[int] = [7, 14, 28],
        group_cols: List[str] = ['id'],
        stats: List[str] = ['mean', 'std', 'min', 'max']
    ) -> pd.DataFrame:
        """
        Create rolling statistics features.
        
        Args:
            df: Input DataFrame
            target_col: Column to compute statistics for
            windows: List of window sizes
            group_cols: Columns to group by
            stats: Statistics to compute
            
        Returns:
            DataFrame with rolling features added
        """
        logger.info(f"Creating rolling features: windows={windows}, stats={stats}")
        
        df_copy = df.copy()
        
        for window in windows:
            for stat in stats:
                feature_name = f'{target_col}_rolling_{stat}_{window}'
                
                if stat == 'mean':
                    df_copy[feature_name] = df_copy.groupby(group_cols)[target_col].transform(
                        lambda x: x.shift(1).rolling(window=window, min_periods=1).mean()
                    )
                elif stat == 'std':
                    df_copy[feature_name] = df_copy.groupby(group_cols)[target_col].transform(
                        lambda x: x.shift(1).rolling(window=window, min_periods=1).std()
                    )
                elif stat == 'min':
                    df_copy[feature_name] = df_copy.groupby(group_cols)[target_col].transform(
                        lambda x: x.shift(1).rolling(window=window, min_periods=1).min()
                    )
                elif stat == 'max':
                    df_copy[feature_name] = df_copy.groupby(group_cols)[target_col].transform(
                        lambda x: x.shift(1).rolling(window=window, min_periods=1).max()
                    )
                
                self.feature_names.append(feature_name)
        
        logger.info(f"✓ Created {len(windows) * len(stats)} rolling features")
        return df_copy
    
    def create_calendar_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create calendar-based features.
        
        Args:
            df: Input DataFrame with 'date' column
            
        Returns:
            DataFrame with calendar features added
        """
        logger.info("Creating calendar features...")
        
        df_copy = df.copy()
        
        # Ensure date is datetime
        if not pd.api.types.is_datetime64_any_dtype(df_copy['date']):
            df_copy['date'] = pd.to_datetime(df_copy['date'])
        
        # Basic date features
        df_copy['year'] = df_copy['date'].dt.year
        df_copy['month'] = df_copy['date'].dt.month
        df_copy['day'] = df_copy['date'].dt.day
        df_copy['day_of_week'] = df_copy['date'].dt.dayofweek
        df_copy['day_of_year'] = df_copy['date'].dt.dayofyear
        df_copy['week_of_year'] = df_copy['date'].dt.isocalendar().week
        df_copy['quarter'] = df_copy['date'].dt.quarter
        
        # Weekend indicator
        df_copy['is_weekend'] = (df_copy['day_of_week'] >= 5).astype(int)
        
        # Month start/end
        df_copy['is_month_start'] = df_copy['date'].dt.is_month_start.astype(int)
        df_copy['is_month_end'] = df_copy['date'].dt.is_month_end.astype(int)
        
        # Cyclical encoding for day of week and month
        df_copy['day_of_week_sin'] = np.sin(2 * np.pi * df_copy['day_of_week'] / 7)
        df_copy['day_of_week_cos'] = np.cos(2 * np.pi * df_copy['day_of_week'] / 7)
        df_copy['month_sin'] = np.sin(2 * np.pi * df_copy['month'] / 12)
        df_copy['month_cos'] = np.cos(2 * np.pi * df_copy['month'] / 12)
        
        calendar_features = [
            'year', 'month', 'day', 'day_of_week', 'day_of_year', 
            'week_of_year', 'quarter', 'is_weekend', 'is_month_start', 
            'is_month_end', 'day_of_week_sin', 'day_of_week_cos',
            'month_sin', 'month_cos'
        ]
        
        self.feature_names.extend(calendar_features)
        logger.info(f"✓ Created {len(calendar_features)} calendar features")
        
        return df_copy
    
    def create_price_features(
        self,
        df: pd.DataFrame,
        price_col: str = 'sell_price',
        group_cols: List[str] = ['id']
    ) -> pd.DataFrame:
        """
        Create price-based features.
        
        Args:
            df: Input DataFrame with price column
            price_col: Name of price column
            group_cols: Columns to group by for price features
            
        Returns:
            DataFrame with price features added
        """
        logger.info("Creating price features...")
        
        df_copy = df.copy()
        
        # Price change from previous period
        df_copy['price_change'] = df_copy.groupby(group_cols)[price_col].diff()
        
        # Price change percentage
        df_copy['price_change_pct'] = df_copy.groupby(group_cols)[price_col].pct_change()
        
        # Price momentum (change in change)
        df_copy['price_momentum'] = df_copy.groupby(group_cols)['price_change'].diff()
        
        # Price relative to rolling average
        df_copy['price_vs_ma_7'] = df_copy[price_col] / (
            df_copy.groupby(group_cols)[price_col].transform(
                lambda x: x.rolling(window=7, min_periods=1).mean()
            )
        )
        
        df_copy['price_vs_ma_28'] = df_copy[price_col] / (
            df_copy.groupby(group_cols)[price_col].transform(
                lambda x: x.rolling(window=28, min_periods=1).mean()
            )
        )
        
        # Price rank within category/store
        if 'cat_id' in df_copy.columns and 'store_id' in df_copy.columns:
            df_copy['price_rank_in_category'] = df_copy.groupby(
                ['date', 'cat_id', 'store_id']
            )[price_col].rank(pct=True)
        
        price_features = [
            'price_change', 'price_change_pct', 'price_momentum',
            'price_vs_ma_7', 'price_vs_ma_28'
        ]
        if 'price_rank_in_category' in df_copy.columns:
            price_features.append('price_rank_in_category')
        
        self.feature_names.extend(price_features)
        logger.info(f"✓ Created {len(price_features)} price features")
        
        return df_copy
    
    def create_event_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create event-based features.
        
        Args:
            df: Input DataFrame with event columns
            
        Returns:
            DataFrame with event features added
        """
        logger.info("Creating event features...")
        
        df_copy = df.copy()
        
        # Binary indicators for event presence
        if 'event_name_1' in df_copy.columns:
            df_copy['has_event_1'] = (df_copy['event_name_1'] != 'None').astype(int)
        
        if 'event_name_2' in df_copy.columns:
            df_copy['has_event_2'] = (df_copy['event_name_2'] != 'None').astype(int)
        
        # Combined event indicator
        has_event_1_col = df_copy['has_event_1'] if 'has_event_1' in df_copy.columns else pd.Series(0, index=df_copy.index)
        has_event_2_col = df_copy['has_event_2'] if 'has_event_2' in df_copy.columns else pd.Series(0, index=df_copy.index)
        df_copy['has_any_event'] = (has_event_1_col | has_event_2_col).astype(int)
        
        # Event type encoding
        if 'event_type_1' in df_copy.columns:
            df_copy['event_type_1_encoded'] = pd.Categorical(
                df_copy['event_type_1']
            ).codes
        
        # SNAP benefits indicator (already in data but ensure it's binary)
        snap_cols = [col for col in df_copy.columns if col.startswith('snap_')]
        for col in snap_cols:
            if col in df_copy.columns:
                df_copy[col] = df_copy[col].astype(int)
        
        event_features = ['has_event_1', 'has_event_2', 'has_any_event']
        if 'event_type_1_encoded' in df_copy.columns:
            event_features.append('event_type_1_encoded')
        
        self.feature_names.extend(event_features)
        logger.info(f"✓ Created {len(event_features)} event features")
        
        return df_copy
    
    def create_hierarchical_features(
        self,
        df: pd.DataFrame,
        target_col: str = 'sales'
    ) -> pd.DataFrame:
        """
        Create features based on hierarchical aggregations.
        
        Args:
            df: Input DataFrame
            target_col: Target column to aggregate
            
        Returns:
            DataFrame with hierarchical features added
        """
        logger.info("Creating hierarchical features...")
        
        df_copy = df.copy()
        
        # Store average sales
        if 'store_id' in df_copy.columns:
            df_copy['store_avg_sales'] = df_copy.groupby(
                ['date', 'store_id']
            )[target_col].transform('mean')
        
        # Category average sales
        if 'cat_id' in df_copy.columns:
            df_copy['cat_avg_sales'] = df_copy.groupby(
                ['date', 'cat_id']
            )[target_col].transform('mean')
        
        # Department average sales
        if 'dept_id' in df_copy.columns:
            df_copy['dept_avg_sales'] = df_copy.groupby(
                ['date', 'dept_id']
            )[target_col].transform('mean')
        
        # State average sales
        if 'state_id' in df_copy.columns:
            df_copy['state_avg_sales'] = df_copy.groupby(
                ['date', 'state_id']
            )[target_col].transform('mean')
        
        # Item's share of category sales
        if 'cat_avg_sales' in df_copy.columns:
            df_copy['item_share_of_cat'] = df_copy[target_col] / (
                df_copy['cat_avg_sales'] + 1e-6
            )
        
        # Item's share of store sales
        if 'store_avg_sales' in df_copy.columns:
            df_copy['item_share_of_store'] = df_copy[target_col] / (
                df_copy['store_avg_sales'] + 1e-6
            )
        
        hierarchical_features = [
            'store_avg_sales', 'cat_avg_sales', 'dept_avg_sales', 
            'state_avg_sales', 'item_share_of_cat', 'item_share_of_store'
        ]
        hierarchical_features = [f for f in hierarchical_features if f in df_copy.columns]
        
        self.feature_names.extend(hierarchical_features)
        logger.info(f"✓ Created {len(hierarchical_features)} hierarchical features")
        
        return df_copy
    
    def create_all_features(
        self,
        df: pd.DataFrame,
        target_col: str = 'sales',
        lags: List[int] = [7, 14, 21, 28],
        rolling_windows: List[int] = [7, 14, 28],
        group_cols: List[str] = ['id']
    ) -> pd.DataFrame:
        """
        Create all features in the correct order.
        
        Args:
            df: Input DataFrame
            target_col: Target column
            lags: Lag periods
            rolling_windows: Rolling window sizes
            group_cols: Grouping columns
            
        Returns:
            DataFrame with all features
        """
        logger.info("Creating all features...")
        logger.info(f"Input shape: {df.shape}")
        
        # Reset feature names
        self.feature_names = []
        
        # Sort by id and date first
        df = df.sort_values(group_cols + ['date']).reset_index(drop=True)
        
        # 1. Calendar features (no dependencies)
        df = self.create_calendar_features(df)
        
        # 2. Event features (no dependencies)
        df = self.create_event_features(df)
        
        # 3. Price features (minimal dependencies)
        if 'sell_price' in df.columns:
            df = self.create_price_features(df, group_cols=group_cols)
        
        # 4. Lag features (depend on target)
        df = self.create_lag_features(
            df, 
            target_col=target_col, 
            lags=lags, 
            group_cols=group_cols
        )
        
        # 5. Rolling features (depend on target)
        df = self.create_rolling_features(
            df,
            target_col=target_col,
            windows=rolling_windows,
            group_cols=group_cols
        )
        
        # 6. Hierarchical features (depend on target)
        df = self.create_hierarchical_features(df, target_col=target_col)
        
        logger.info(f"✓ Feature engineering complete")
        logger.info(f"Output shape: {df.shape}")
        logger.info(f"Total features created: {len(self.feature_names)}")
        
        return df
    
    def get_feature_names(self) -> List[str]:
        """Get list of created feature names."""
        return self.feature_names


def main():
    """Example usage of feature engineering."""
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from src.utils.logger import setup_logger
    
    # Setup logging
    logger = setup_logger(
        "feature_engineering",
        log_file="logs/feature_engineering.log"
    )
    
    logger.info("Starting feature engineering...")
    
    # Load processed data
    data_path = Path("data/processed")
    
    if not (data_path / "sales_processed.parquet").exists():
        logger.error("Processed data not found. Run preprocess.py first.")
        return
    
    # Load data (use sample for testing)
    df = pd.read_parquet(data_path / "train.parquet")
    
    # Sample for faster testing
    sample_ids = df['id'].unique()[:10]
    df_sample = df[df['id'].isin(sample_ids)].copy()
    
    logger.info(f"Sample data shape: {df_sample.shape}")
    
    # Create features
    engineer = FeatureEngineer()
    df_features = engineer.create_all_features(
        df_sample,
        target_col='sales',
        lags=[7, 14, 28],
        rolling_windows=[7, 28],
        group_cols=['id']
    )
    
    # Print feature summary
    logger.info("\nFeature Names:")
    for i, name in enumerate(engineer.get_feature_names(), 1):
        logger.info(f"  {i}. {name}")
    
    # Save sample with features
    output_path = data_path / "sample_with_features.parquet"
    df_features.to_parquet(output_path, index=False)
    logger.info(f"\n✓ Sample with features saved to {output_path}")


if __name__ == "__main__":
    main()
