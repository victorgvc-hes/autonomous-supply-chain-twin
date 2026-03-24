"""
Unit tests for src/utils/metrics.py

Covers:
- rmse, mae, mape, smape, mse, forecast_bias
- service_level, stockout_rate
- inventory_cost, total_supply_chain_cost
- calculate_all_metrics
- MetricsCalculator class
"""

import numpy as np
import pytest
from src.utils.metrics import (
    rmse, mae, mape, smape, mse, forecast_bias,
    service_level, stockout_rate, inventory_cost,
    total_supply_chain_cost, calculate_all_metrics,
    MetricsCalculator,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def perfect():
    """Identical true and predicted arrays."""
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    return y, y.copy()


@pytest.fixture
def known_errors():
    """y_true=[0,0,0,0], y_pred=[1,1,1,1] → all errors = 1."""
    y_true = np.zeros(4)
    y_pred = np.ones(4)
    return y_true, y_pred


# ---------------------------------------------------------------------------
# rmse
# ---------------------------------------------------------------------------

def test_rmse_perfect_prediction(perfect):
    y_true, y_pred = perfect
    assert rmse(y_true, y_pred) == 0.0


def test_rmse_known_value(known_errors):
    y_true, y_pred = known_errors
    # All errors = 1 → RMSE = sqrt(mean([1,1,1,1])) = 1.0
    assert rmse(y_true, y_pred) == pytest.approx(1.0)


def test_rmse_always_nonnegative():
    y_true = np.array([3.0, 1.0, 4.0])
    y_pred = np.array([1.0, 5.0, 9.0])
    assert rmse(y_true, y_pred) >= 0.0


def test_rmse_symmetric():
    """RMSE(a,b) == RMSE(b,a)."""
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([2.0, 4.0, 6.0])
    assert rmse(a, b) == pytest.approx(rmse(b, a))


# ---------------------------------------------------------------------------
# mae
# ---------------------------------------------------------------------------

def test_mae_perfect_prediction(perfect):
    y_true, y_pred = perfect
    assert mae(y_true, y_pred) == 0.0


def test_mae_known_value():
    y_true = np.array([0.0, 0.0, 0.0])
    y_pred = np.array([1.0, 2.0, 3.0])
    # MAE = mean([1, 2, 3]) = 2.0
    assert mae(y_true, y_pred) == pytest.approx(2.0)


def test_mae_always_nonnegative():
    y_true = np.array([5.0, 3.0])
    y_pred = np.array([2.0, 7.0])
    assert mae(y_true, y_pred) >= 0.0


# ---------------------------------------------------------------------------
# mse
# ---------------------------------------------------------------------------

def test_mse_perfect_prediction(perfect):
    y_true, y_pred = perfect
    assert mse(y_true, y_pred) == 0.0


def test_mse_equals_rmse_squared():
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([2.0, 4.0, 6.0])
    assert mse(y_true, y_pred) == pytest.approx(rmse(y_true, y_pred) ** 2)


# ---------------------------------------------------------------------------
# mape
# ---------------------------------------------------------------------------

def test_mape_perfect_prediction(perfect):
    y_true, y_pred = perfect
    assert mape(y_true, y_pred) == pytest.approx(0.0, abs=1e-6)


def test_mape_known_value():
    # y_true=2, y_pred=1: |2-1|/(2+eps)*100 ≈ 50%
    y_true = np.array([2.0])
    y_pred = np.array([1.0])
    assert mape(y_true, y_pred) == pytest.approx(50.0, rel=1e-3)


def test_mape_always_nonnegative(perfect):
    y_true, y_pred = perfect
    assert mape(y_true, y_pred) >= 0.0


# ---------------------------------------------------------------------------
# smape
# ---------------------------------------------------------------------------

def test_smape_perfect_prediction(perfect):
    y_true, y_pred = perfect
    assert smape(y_true, y_pred) == pytest.approx(0.0, abs=1e-6)


def test_smape_always_nonnegative():
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([3.0, 1.0, 2.0])
    assert smape(y_true, y_pred) >= 0.0


def test_smape_bounded_above():
    """SMAPE is bounded at 200%."""
    y_true = np.array([1.0, 0.0])
    y_pred = np.array([0.0, 1.0])
    assert smape(y_true, y_pred) <= 200.0


# ---------------------------------------------------------------------------
# forecast_bias
# ---------------------------------------------------------------------------

def test_forecast_bias_zero(perfect):
    y_true, y_pred = perfect
    assert forecast_bias(y_true, y_pred) == pytest.approx(0.0)


def test_forecast_bias_over_forecast():
    """When pred > true, bias should be positive."""
    y_true = np.array([1.0, 1.0, 1.0])
    y_pred = np.array([2.0, 2.0, 2.0])
    assert forecast_bias(y_true, y_pred) == pytest.approx(1.0)


def test_forecast_bias_under_forecast():
    """When pred < true, bias should be negative."""
    y_true = np.array([3.0, 3.0])
    y_pred = np.array([1.0, 1.0])
    assert forecast_bias(y_true, y_pred) == pytest.approx(-2.0)


# ---------------------------------------------------------------------------
# service_level
# ---------------------------------------------------------------------------

def test_service_level_all_demand_met():
    demand = np.array([1.0, 2.0, 3.0])
    inv = np.array([5.0, 5.0, 5.0])  # always enough
    assert service_level(demand, inv, demand_met_threshold=0.999) == pytest.approx(100.0)


def test_service_level_no_inventory():
    demand = np.array([1.0, 2.0, 3.0])
    inv = np.zeros(3)
    # fill_rate = 0 / demand ≈ 0, all days below threshold → 0%
    assert service_level(demand, inv) == pytest.approx(0.0)


def test_service_level_partial():
    """Half of days have enough inventory."""
    demand = np.array([2.0, 2.0, 2.0, 2.0])
    inv    = np.array([5.0, 5.0, 0.0, 0.0])  # first 2 met, last 2 not
    result = service_level(demand, inv, demand_met_threshold=0.999)
    assert result == pytest.approx(50.0)


def test_service_level_zero_demand():
    """With zero demand and zero inventory, fill_rate=0 → service level is 0%."""
    demand = np.zeros(4)
    inv = np.zeros(4)
    assert service_level(demand, inv) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# stockout_rate
# ---------------------------------------------------------------------------

def test_stockout_rate_no_stockouts():
    demand = np.array([1.0, 2.0, 3.0])
    inv    = np.array([5.0, 5.0, 5.0])
    assert stockout_rate(demand, inv) == pytest.approx(0.0)


def test_stockout_rate_all_stockouts():
    demand = np.array([1.0, 2.0, 3.0])
    inv    = np.zeros(3)
    assert stockout_rate(demand, inv) == pytest.approx(100.0)


def test_stockout_rate_half():
    demand = np.array([1.0, 1.0, 1.0, 1.0])
    inv    = np.array([5.0, 5.0, 0.0, 0.0])
    assert stockout_rate(demand, inv) == pytest.approx(50.0)


def test_stockout_rate_boundary():
    """Inventory exactly equal to demand → no stockout."""
    demand = np.array([3.0, 3.0])
    inv    = np.array([3.0, 3.0])
    assert stockout_rate(demand, inv) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# inventory_cost
# ---------------------------------------------------------------------------

def test_inventory_cost_holding_only():
    inv = np.array([10.0, 10.0, 10.0])  # 30 unit-days
    result = inventory_cost(inv, holding_cost_per_unit=1.0)
    assert result['holding_cost'] == pytest.approx(30.0)
    assert result['ordering_cost'] == pytest.approx(0.0)
    assert result['total_cost'] == pytest.approx(30.0)


def test_inventory_cost_with_orders():
    inv    = np.array([5.0, 5.0])
    orders = np.array([1.0, 0.0])  # one order placed
    result = inventory_cost(inv, holding_cost_per_unit=1.0,
                            ordering_cost_per_order=50.0, orders=orders)
    assert result['ordering_cost'] == pytest.approx(50.0)
    assert result['total_cost'] == pytest.approx(10.0 + 50.0)


def test_inventory_cost_returns_expected_keys():
    inv = np.array([1.0, 2.0, 3.0])
    result = inventory_cost(inv)
    for key in ('holding_cost', 'ordering_cost', 'total_cost',
                'avg_inventory', 'max_inventory'):
        assert key in result


def test_inventory_cost_avg_and_max():
    inv = np.array([2.0, 4.0, 6.0])
    result = inventory_cost(inv, holding_cost_per_unit=1.0)
    assert result['avg_inventory'] == pytest.approx(4.0)
    assert result['max_inventory'] == pytest.approx(6.0)


# ---------------------------------------------------------------------------
# total_supply_chain_cost
# ---------------------------------------------------------------------------

def test_total_supply_chain_cost_no_stockouts():
    demand = np.array([1.0, 1.0])
    pred   = np.array([1.0, 1.0])
    inv    = np.array([5.0, 5.0])
    result = total_supply_chain_cost(demand, pred, inv,
                                     holding_cost_per_unit=1.0,
                                     stockout_cost_per_unit=10.0)
    assert result['stockout_cost'] == pytest.approx(0.0)
    assert result['total_stockouts'] == pytest.approx(0.0)


def test_total_supply_chain_cost_with_stockouts():
    demand = np.array([3.0, 3.0])
    pred   = np.array([3.0, 3.0])
    inv    = np.array([1.0, 1.0])  # 2 units unmet each day
    result = total_supply_chain_cost(demand, pred, inv,
                                     holding_cost_per_unit=0.5,
                                     stockout_cost_per_unit=5.0)
    # unmet = [2, 2] → stockout_cost = 4 * 5 = 20
    assert result['stockout_cost'] == pytest.approx(20.0)
    assert result['total_stockouts'] == pytest.approx(4.0)


def test_total_supply_chain_cost_keys():
    demand = np.ones(3)
    inv    = np.ones(3) * 2
    result = total_supply_chain_cost(demand, demand, inv)
    for key in ('holding_cost', 'ordering_cost', 'stockout_cost',
                'total_cost', 'avg_inventory', 'max_inventory',
                'total_stockouts', 'stockout_rate_pct'):
        assert key in result


# ---------------------------------------------------------------------------
# calculate_all_metrics
# ---------------------------------------------------------------------------

def test_calculate_all_metrics_returns_expected_keys(perfect):
    y_true, y_pred = perfect
    result = calculate_all_metrics(y_true, y_pred)
    for key in ('rmse', 'mae', 'mape', 'smape', 'mse', 'bias'):
        assert key in result


def test_calculate_all_metrics_with_inventory():
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.0, 2.0, 3.0])
    inv    = np.array([5.0, 5.0, 5.0])
    result = calculate_all_metrics(y_true, y_pred, inventory=inv)
    assert 'service_level' in result
    assert 'stockout_rate' in result


def test_calculate_all_metrics_without_inventory_no_service_keys(perfect):
    y_true, y_pred = perfect
    result = calculate_all_metrics(y_true, y_pred)
    assert 'service_level' not in result
    assert 'stockout_rate' not in result


def test_calculate_all_metrics_perfect_gives_zeros(perfect):
    y_true, y_pred = perfect
    result = calculate_all_metrics(y_true, y_pred)
    assert result['rmse'] == pytest.approx(0.0)
    assert result['mae']  == pytest.approx(0.0)
    assert result['bias'] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# MetricsCalculator
# ---------------------------------------------------------------------------

def test_metrics_calculator_stores_history():
    calc = MetricsCalculator()
    y = np.array([1.0, 2.0, 3.0])
    calc.calculate_metrics(y, y, experiment_name="exp1")
    calc.calculate_metrics(y, y, experiment_name="exp2")
    assert len(calc.metrics_history) == 2


def test_metrics_calculator_get_metrics_df():
    calc = MetricsCalculator()
    y = np.array([1.0, 2.0])
    calc.calculate_metrics(y, y, experiment_name="test")
    df = calc.get_metrics_df()
    assert len(df) == 1
    assert 'rmse' in df.columns
    assert 'experiment' in df.columns


def test_metrics_calculator_compare_experiments():
    calc = MetricsCalculator()
    y = np.array([1.0, 2.0, 3.0])
    calc.calculate_metrics(y, y, experiment_name="baseline")
    calc.calculate_metrics(y, y + 1, experiment_name="model_a")
    comparison = calc.compare_experiments()
    assert 'baseline' in comparison.index
    assert 'model_a' in comparison.index


def test_metrics_calculator_experiment_name_recorded():
    calc = MetricsCalculator()
    y = np.array([1.0])
    result = calc.calculate_metrics(y, y, experiment_name="my_exp")
    assert result['experiment'] == "my_exp"
