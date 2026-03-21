"""
Metrics module for forecast evaluation.

Implements various forecasting metrics including:
- RMSE, MAE, MAPE
- WRMSSE (M5 competition metric)
- Service level metrics
- Cost-based metrics
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Root Mean Squared Error.
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
        
    Returns:
        RMSE value
    """
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Mean Absolute Error.
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
        
    Returns:
        MAE value
    """
    return np.mean(np.abs(y_true - y_pred))


def mape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-10) -> float:
    """
    Mean Absolute Percentage Error.
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
        epsilon: Small value to avoid division by zero
        
    Returns:
        MAPE value (as percentage)
    """
    return np.mean(np.abs((y_true - y_pred) / (y_true + epsilon))) * 100


def smape(y_true: np.ndarray, y_pred: np.ndarray, epsilon: float = 1e-10) -> float:
    """
    Symmetric Mean Absolute Percentage Error.
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
        epsilon: Small value to avoid division by zero
        
    Returns:
        SMAPE value (as percentage)
    """
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2 + epsilon
    return np.mean(np.abs(y_true - y_pred) / denominator) * 100


def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Mean Squared Error.
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
        
    Returns:
        MSE value
    """
    return np.mean((y_true - y_pred) ** 2)


def wrmsse(
    y_true: pd.DataFrame,
    y_pred: pd.DataFrame,
    sales_train: pd.DataFrame,
    weights: Optional[pd.Series] = None
) -> float:
    """
    Weighted Root Mean Squared Scaled Error (M5 competition metric).
    
    Args:
        y_true: True sales values (rows=items, cols=days)
        y_pred: Predicted sales values (rows=items, cols=days)
        sales_train: Training sales for computing scale
        weights: Optional weights for aggregation levels
        
    Returns:
        WRMSSE value
    """
    # Compute RMSSE for each series
    rmsse_values = []
    
    for idx in y_true.index:
        # Get actual and predicted for this series
        actual = y_true.loc[idx].values
        predicted = y_pred.loc[idx].values
        
        # Get training data for scale calculation
        train = sales_train.loc[idx].values
        
        # Calculate denominator (scale): mean of squared differences
        # Using h-step ahead naive forecast
        h = len(actual)
        if len(train) > h:
            scale_denominator = np.mean(np.diff(train) ** 2)
        else:
            scale_denominator = 1.0  # Fallback
        
        # Avoid division by zero
        if scale_denominator == 0:
            scale_denominator = 1.0
        
        # Calculate MSE
        mse_value = np.mean((actual - predicted) ** 2)
        
        # Calculate RMSSE
        rmsse = np.sqrt(mse_value / scale_denominator)
        rmsse_values.append(rmsse)
    
    rmsse_values = np.array(rmsse_values)
    
    # Apply weights if provided
    if weights is not None:
        wrmsse_value = np.average(rmsse_values, weights=weights)
    else:
        wrmsse_value = np.mean(rmsse_values)
    
    return wrmsse_value


def service_level(
    y_true: np.ndarray,
    inventory: np.ndarray,
    demand_met_threshold: float = 1.0
) -> float:
    """
    Calculate service level (fill rate).
    
    Args:
        y_true: Actual demand
        inventory: Available inventory
        demand_met_threshold: Threshold for considering demand met (default 1.0 = 100%)
        
    Returns:
        Service level as percentage
    """
    demand_met = np.minimum(y_true, inventory)
    fill_rate = demand_met / (y_true + 1e-10)
    service_level_pct = np.mean(fill_rate >= demand_met_threshold) * 100
    
    return service_level_pct


def stockout_rate(y_true: np.ndarray, inventory: np.ndarray) -> float:
    """
    Calculate stockout rate.
    
    Args:
        y_true: Actual demand
        inventory: Available inventory
        
    Returns:
        Stockout rate as percentage
    """
    stockouts = inventory < y_true
    return np.mean(stockouts) * 100


def inventory_cost(
    inventory: np.ndarray,
    holding_cost_per_unit: float = 1.0,
    ordering_cost_per_order: float = 100.0,
    orders: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    Calculate inventory-related costs.
    
    Args:
        inventory: Inventory levels over time
        holding_cost_per_unit: Cost to hold one unit for one period
        ordering_cost_per_order: Fixed cost per order
        orders: Array indicating when orders were placed (1 = order, 0 = no order)
        
    Returns:
        Dictionary with cost breakdown
    """
    # Holding cost
    total_holding_cost = np.sum(inventory) * holding_cost_per_unit
    
    # Ordering cost
    if orders is not None:
        num_orders = np.sum(orders)
        total_ordering_cost = num_orders * ordering_cost_per_order
    else:
        total_ordering_cost = 0.0
    
    total_cost = total_holding_cost + total_ordering_cost
    
    return {
        'holding_cost': total_holding_cost,
        'ordering_cost': total_ordering_cost,
        'total_cost': total_cost,
        'avg_inventory': np.mean(inventory),
        'max_inventory': np.max(inventory)
    }


def total_supply_chain_cost(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    inventory: np.ndarray,
    holding_cost_per_unit: float = 1.0,
    stockout_cost_per_unit: float = 10.0,
    ordering_cost_per_order: float = 100.0,
    orders: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    Calculate total supply chain cost including all components.
    
    Args:
        y_true: Actual demand
        y_pred: Forecasted demand
        inventory: Inventory levels
        holding_cost_per_unit: Holding cost per unit per period
        stockout_cost_per_unit: Lost sales cost per unit
        ordering_cost_per_order: Fixed ordering cost
        orders: Order indicators
        
    Returns:
        Dictionary with detailed cost breakdown
    """
    # Inventory costs
    inv_costs = inventory_cost(
        inventory,
        holding_cost_per_unit,
        ordering_cost_per_order,
        orders
    )
    
    # Stockout costs (lost sales)
    unmet_demand = np.maximum(0, y_true - inventory)
    stockout_cost = np.sum(unmet_demand) * stockout_cost_per_unit
    
    # Total cost
    total_cost = inv_costs['total_cost'] + stockout_cost
    
    return {
        'holding_cost': inv_costs['holding_cost'],
        'ordering_cost': inv_costs['ordering_cost'],
        'stockout_cost': stockout_cost,
        'total_cost': total_cost,
        'avg_inventory': inv_costs['avg_inventory'],
        'max_inventory': inv_costs['max_inventory'],
        'total_stockouts': np.sum(unmet_demand),
        'stockout_rate_pct': stockout_rate(y_true, inventory)
    }


def forecast_bias(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate forecast bias (tendency to over/under forecast).
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
        
    Returns:
        Bias value (negative = under-forecasting, positive = over-forecasting)
    """
    return np.mean(y_pred - y_true)


def calculate_all_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    inventory: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """
    Calculate all standard forecasting metrics.
    
    Args:
        y_true: Actual values
        y_pred: Predicted values
        inventory: Optional inventory levels for service metrics
        
    Returns:
        Dictionary with all metrics
    """
    metrics = {
        'rmse': rmse(y_true, y_pred),
        'mae': mae(y_true, y_pred),
        'mape': mape(y_true, y_pred),
        'smape': smape(y_true, y_pred),
        'mse': mse(y_true, y_pred),
        'bias': forecast_bias(y_true, y_pred)
    }
    
    # Add service metrics if inventory provided
    if inventory is not None:
        metrics['service_level'] = service_level(y_true, inventory)
        metrics['stockout_rate'] = stockout_rate(y_true, inventory)
    
    return metrics


class MetricsCalculator:
    """Class for calculating and tracking metrics across experiments."""
    
    def __init__(self):
        """Initialize metrics calculator."""
        self.metrics_history = []
        
    def calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        experiment_name: str = "default",
        **kwargs
    ) -> Dict[str, float]:
        """
        Calculate metrics and store in history.
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            experiment_name: Name of the experiment
            **kwargs: Additional arguments for specific metrics
            
        Returns:
            Dictionary of metrics
        """
        metrics = calculate_all_metrics(y_true, y_pred, **kwargs)
        metrics['experiment'] = experiment_name
        
        self.metrics_history.append(metrics)
        
        return metrics
    
    def get_metrics_df(self) -> pd.DataFrame:
        """
        Get metrics history as DataFrame.
        
        Returns:
            DataFrame with metrics history
        """
        return pd.DataFrame(self.metrics_history)
    
    def compare_experiments(self) -> pd.DataFrame:
        """
        Compare metrics across experiments.
        
        Returns:
            DataFrame with comparison
        """
        df = self.get_metrics_df()
        
        if 'experiment' in df.columns:
            comparison = df.groupby('experiment').mean()
            return comparison
        else:
            return df
    
    def print_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Pretty print metrics.
        
        Args:
            metrics: Dictionary of metrics
        """
        logger.info("\n" + "="*50)
        logger.info("METRICS SUMMARY")
        logger.info("="*50)
        
        for key, value in metrics.items():
            if key != 'experiment':
                logger.info(f"{key:20s}: {value:10.4f}")
        
        logger.info("="*50)


def main():
    """Example usage of metrics."""
    # Generate sample data
    np.random.seed(42)
    y_true = np.random.poisson(10, size=100)
    y_pred = y_true + np.random.normal(0, 2, size=100)
    
    # Calculate metrics
    calculator = MetricsCalculator()
    metrics = calculator.calculate_metrics(
        y_true, 
        y_pred, 
        experiment_name="baseline"
    )
    
    # Print results
    calculator.print_metrics(metrics)


if __name__ == "__main__":
    main()
