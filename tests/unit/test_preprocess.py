"""
Unit tests for src/data_generation/preprocess.py

Strategy: inject mock DataFrames directly into preprocessor.sales_long
to avoid needing real CSV files on disk.

Covers:
- handle_missing_values
- create_train_val_test_split
- get_data_summary
- transform_to_long_format (error path)
"""

import numpy as np
import pandas as pd
import pytest
from src.data_generation.preprocess import M5DataPreprocessor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_sales_long(n_products=2, n_days=10, with_nulls=False):
    """
    Build a minimal sales_long-style DataFrame without loading real files.
    """
    dates = pd.date_range('2020-01-01', periods=n_days, freq='D')
    records = []
    for prod_id in [f'ITEM_{i}' for i in range(n_products)]:
        for date in dates:
            records.append({
                'id':       prod_id,
                'item_id':  prod_id,
                'store_id': 'STORE_1',
                'state_id': 'CA',
                'cat_id':   'FOODS',
                'dept_id':  'FOODS_1',
                'date':     date,
                'sales':    np.nan if with_nulls else 1.0,
                'event_name_1': np.nan if with_nulls else 'None',
                'event_name_2': np.nan if with_nulls else 'None',
                'sell_price': 2.50,
            })
    return pd.DataFrame(records)


def make_preprocessor(n_products=2, n_days=20, with_nulls=False):
    """Return a preprocessor with sales_long already injected."""
    p = M5DataPreprocessor()
    p.sales_long = make_sales_long(n_products, n_days, with_nulls)
    return p


# ---------------------------------------------------------------------------
# handle_missing_values
# ---------------------------------------------------------------------------

def test_handle_missing_values_fills_sales_nan():
    p = make_preprocessor(with_nulls=True)
    result = p.handle_missing_values()
    assert result['sales'].isna().sum() == 0


def test_handle_missing_values_sales_nan_becomes_zero():
    p = make_preprocessor(with_nulls=True)
    result = p.handle_missing_values()
    assert (result['sales'] == 0).all()


def test_handle_missing_values_fills_event_cols_with_none_string():
    p = make_preprocessor(with_nulls=True)
    result = p.handle_missing_values()
    assert result['event_name_1'].isna().sum() == 0
    assert result['event_name_2'].isna().sum() == 0
    assert (result['event_name_1'] == 'None').all()


def test_handle_missing_values_does_not_alter_existing_values():
    """Non-null sales values should remain unchanged."""
    p = make_preprocessor(with_nulls=False)
    result = p.handle_missing_values()
    assert (result['sales'] == 1.0).all()


def test_handle_missing_values_raises_without_data():
    p = M5DataPreprocessor()
    with pytest.raises(ValueError):
        p.handle_missing_values()


# ---------------------------------------------------------------------------
# create_train_val_test_split
# ---------------------------------------------------------------------------

def test_split_train_does_not_exceed_end_date():
    p = make_preprocessor(n_days=60)
    train_end = '2020-02-01'
    train, val, test = p.create_train_val_test_split(
        train_end_date=train_end, val_days=10, test_days=10
    )
    assert train['date'].max() <= pd.Timestamp(train_end)


def test_split_val_is_after_train():
    p = make_preprocessor(n_days=60)
    train_end = '2020-02-01'
    train, val, test = p.create_train_val_test_split(
        train_end_date=train_end, val_days=10, test_days=10
    )
    assert val['date'].min() > train['date'].max()


def test_split_test_is_after_val():
    p = make_preprocessor(n_days=60)
    train, val, test = p.create_train_val_test_split(
        train_end_date='2020-02-01', val_days=10, test_days=10
    )
    if len(test) > 0 and len(val) > 0:
        assert test['date'].min() > val['date'].max()


def test_split_no_date_overlap():
    p = make_preprocessor(n_days=60)
    train, val, test = p.create_train_val_test_split(
        train_end_date='2020-02-01', val_days=10, test_days=5
    )
    train_dates = set(train['date'].dt.date)
    val_dates   = set(val['date'].dt.date)
    test_dates  = set(test['date'].dt.date)
    assert train_dates.isdisjoint(val_dates)
    assert train_dates.isdisjoint(test_dates)
    assert val_dates.isdisjoint(test_dates)


def test_split_raises_without_data():
    p = M5DataPreprocessor()
    with pytest.raises(ValueError):
        p.create_train_val_test_split()


def test_split_returns_three_dataframes():
    p = make_preprocessor(n_days=60)
    result = p.create_train_val_test_split(
        train_end_date='2020-02-01', val_days=5, test_days=5
    )
    assert len(result) == 3
    assert all(isinstance(df, pd.DataFrame) for df in result)


# ---------------------------------------------------------------------------
# get_data_summary
# ---------------------------------------------------------------------------

def test_get_data_summary_returns_dict():
    p = make_preprocessor(n_products=2, n_days=10)
    summary = p.get_data_summary()
    assert isinstance(summary, dict)


def test_get_data_summary_total_rows():
    p = make_preprocessor(n_products=2, n_days=10)
    summary = p.get_data_summary()
    assert summary['total_rows'] == 20  # 2 products × 10 days


def test_get_data_summary_unique_products():
    p = make_preprocessor(n_products=3, n_days=5)
    summary = p.get_data_summary()
    assert summary['unique_products'] == 3


def test_get_data_summary_zero_sales_pct():
    """All sales = 1.0 → zero_sales_pct should be 0."""
    p = make_preprocessor(n_products=2, n_days=5, with_nulls=False)
    summary = p.get_data_summary()
    assert summary['zero_sales_pct'] == pytest.approx(0.0)


def test_get_data_summary_expected_keys():
    p = make_preprocessor()
    summary = p.get_data_summary()
    for key in ('total_rows', 'unique_products', 'unique_stores',
                'total_days', 'total_sales', 'zero_sales_pct'):
        assert key in summary, f"Missing key: {key}"


def test_get_data_summary_raises_without_data():
    p = M5DataPreprocessor()
    with pytest.raises(ValueError):
        p.get_data_summary()


# ---------------------------------------------------------------------------
# transform_to_long_format (error path only — full test needs CSV files)
# ---------------------------------------------------------------------------

def test_transform_to_long_format_raises_without_sales():
    """Calling transform before load_data should raise ValueError."""
    p = M5DataPreprocessor()
    with pytest.raises(ValueError, match="not loaded"):
        p.transform_to_long_format()


# ---------------------------------------------------------------------------
# create_hierarchical_aggregations (error path)
# ---------------------------------------------------------------------------

def test_create_hierarchical_aggregations_raises_without_data():
    p = M5DataPreprocessor()
    with pytest.raises(ValueError):
        p.create_hierarchical_aggregations()
