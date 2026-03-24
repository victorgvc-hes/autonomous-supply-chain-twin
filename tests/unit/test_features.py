"""
Unit tests for src/data_generation/features.py

Covers:
- create_lag_features
- create_rolling_features
- create_calendar_features
- create_event_features
- create_hierarchical_features
- feature_names tracking
"""

import numpy as np
import pandas as pd
import pytest
from src.data_generation.features import FeatureEngineer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_df():
    """Minimal single-group time series DataFrame."""
    return pd.DataFrame({
        'id': ['A'] * 6,
        'date': pd.date_range('2020-01-01', periods=6, freq='D'),
        'sales': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
    })


@pytest.fixture
def two_group_df():
    """Two groups (A and B) with known sales values."""
    dates = pd.date_range('2020-01-01', periods=4, freq='D')
    return pd.DataFrame({
        'id': ['A'] * 4 + ['B'] * 4,
        'date': list(dates) * 2,
        'sales': [10.0, 20.0, 30.0, 40.0,
                  100.0, 200.0, 300.0, 400.0],
    })


@pytest.fixture
def calendar_df():
    """DataFrame with specific dates to test calendar logic."""
    return pd.DataFrame({
        'id': ['X'] * 8,
        'date': pd.to_datetime([
            '2020-01-01',   # Wednesday, month start
            '2020-01-04',   # Saturday (weekend)
            '2020-01-05',   # Sunday (weekend)
            '2020-01-06',   # Monday (weekday)
            '2020-01-31',   # Friday, month end
            '2020-02-01',   # Saturday, month start
            '2020-03-15',   # Sunday
            '2020-12-31',   # Thursday, month end
        ]),
        'sales': [0.0] * 8,
    })


@pytest.fixture
def event_df():
    """DataFrame with event columns."""
    return pd.DataFrame({
        'id': ['A'] * 4,
        'date': pd.date_range('2020-01-01', periods=4),
        'sales': [1.0, 2.0, 3.0, 4.0],
        'event_name_1': ['None', 'Christmas', 'None', 'Easter'],
        'event_name_2': ['None', 'None', 'None', 'None'],
        'event_type_1': ['None', 'Cultural', 'None', 'Religious'],
    })


@pytest.fixture
def hierarchical_df():
    """DataFrame with store, category, dept, state columns."""
    dates = pd.date_range('2020-01-01', periods=3)
    return pd.DataFrame({
        'id':       ['A', 'A', 'A', 'B', 'B', 'B'],
        'date':     list(dates) * 2,
        'sales':    [2.0, 4.0, 6.0, 8.0, 10.0, 12.0],
        'store_id': ['S1', 'S1', 'S1', 'S1', 'S1', 'S1'],
        'cat_id':   ['C1', 'C1', 'C1', 'C1', 'C1', 'C1'],
        'dept_id':  ['D1', 'D1', 'D1', 'D1', 'D1', 'D1'],
        'state_id': ['CA', 'CA', 'CA', 'CA', 'CA', 'CA'],
    })


# ---------------------------------------------------------------------------
# create_lag_features
# ---------------------------------------------------------------------------

def test_lag_features_column_names(simple_df):
    eng = FeatureEngineer()
    result = eng.create_lag_features(simple_df, lags=[1, 3])
    assert 'sales_lag_1' in result.columns
    assert 'sales_lag_3' in result.columns


def test_lag_features_correct_count(simple_df):
    eng = FeatureEngineer()
    original_cols = len(simple_df.columns)
    result = eng.create_lag_features(simple_df, lags=[7, 14, 21, 28])
    assert len(result.columns) == original_cols + 4


def test_lag_features_values_correct(simple_df):
    """lag_1 of [1,2,3,4,5,6] should be [NaN,1,2,3,4,5]."""
    eng = FeatureEngineer()
    result = eng.create_lag_features(simple_df, lags=[1])
    lag_values = result['sales_lag_1'].values
    assert np.isnan(lag_values[0])
    assert lag_values[1] == pytest.approx(1.0)
    assert lag_values[2] == pytest.approx(2.0)
    assert lag_values[5] == pytest.approx(5.0)


def test_lag_features_no_cross_group_bleed(two_group_df):
    """Lag should not bleed across groups."""
    eng = FeatureEngineer()
    result = eng.create_lag_features(two_group_df, lags=[1])
    result = result.sort_values(['id', 'date']).reset_index(drop=True)

    # First row of group A: lag should be NaN, not last value of group B
    group_a_first = result[result['id'] == 'A'].iloc[0]
    assert np.isnan(group_a_first['sales_lag_1'])

    # First row of group B: lag should also be NaN
    group_b_first = result[result['id'] == 'B'].iloc[0]
    assert np.isnan(group_b_first['sales_lag_1'])


def test_lag_features_does_not_mutate_input(simple_df):
    eng = FeatureEngineer()
    original_cols = list(simple_df.columns)
    eng.create_lag_features(simple_df, lags=[1])
    assert list(simple_df.columns) == original_cols


def test_lag_features_tracked_in_feature_names(simple_df):
    eng = FeatureEngineer()
    eng.create_lag_features(simple_df, lags=[7, 14])
    assert 'sales_lag_7' in eng.feature_names
    assert 'sales_lag_14' in eng.feature_names


# ---------------------------------------------------------------------------
# create_rolling_features
# ---------------------------------------------------------------------------

def test_rolling_features_column_names(simple_df):
    eng = FeatureEngineer()
    result = eng.create_rolling_features(simple_df, windows=[7], stats=['mean'])
    assert 'sales_rolling_mean_7' in result.columns


def test_rolling_features_correct_count(simple_df):
    """3 windows × 4 stats = 12 new columns."""
    eng = FeatureEngineer()
    original_cols = len(simple_df.columns)
    result = eng.create_rolling_features(
        simple_df, windows=[7, 14, 28], stats=['mean', 'std', 'min', 'max']
    )
    assert len(result.columns) == original_cols + 12


def test_rolling_mean_first_row_is_nan(simple_df):
    """First row: shift(1) gives NaN → rolling mean should also be NaN."""
    eng = FeatureEngineer()
    result = eng.create_rolling_features(simple_df, windows=[3], stats=['mean'])
    assert np.isnan(result['sales_rolling_mean_3'].iloc[0])


def test_rolling_mean_uses_shifted_values(simple_df):
    """
    sales = [1,2,3,4,5,6]. After shift(1): [NaN,1,2,3,4,5].
    rolling(window=2, min_periods=1).mean():
      row0: NaN
      row1: mean([1]) = 1.0
      row2: mean([1,2]) = 1.5
      row3: mean([2,3]) = 2.5
    """
    eng = FeatureEngineer()
    result = eng.create_rolling_features(simple_df, windows=[2], stats=['mean'])
    vals = result['sales_rolling_mean_2'].values
    assert np.isnan(vals[0])
    assert vals[1] == pytest.approx(1.0)
    assert vals[2] == pytest.approx(1.5)
    assert vals[3] == pytest.approx(2.5)


def test_rolling_features_tracked_in_feature_names(simple_df):
    eng = FeatureEngineer()
    eng.create_rolling_features(simple_df, windows=[7], stats=['mean', 'std'])
    assert 'sales_rolling_mean_7' in eng.feature_names
    assert 'sales_rolling_std_7' in eng.feature_names


# ---------------------------------------------------------------------------
# create_calendar_features
# ---------------------------------------------------------------------------

def test_calendar_features_year_month_day(calendar_df):
    eng = FeatureEngineer()
    result = eng.create_calendar_features(calendar_df)
    first = result.iloc[0]
    assert first['year'] == 2020
    assert first['month'] == 1
    assert first['day'] == 1


def test_calendar_features_weekend_saturday(calendar_df):
    eng = FeatureEngineer()
    result = eng.create_calendar_features(calendar_df)
    # 2020-01-04 is Saturday → is_weekend = 1
    sat_row = result[result['date'] == pd.Timestamp('2020-01-04')].iloc[0]
    assert sat_row['is_weekend'] == 1


def test_calendar_features_weekend_sunday(calendar_df):
    eng = FeatureEngineer()
    result = eng.create_calendar_features(calendar_df)
    # 2020-01-05 is Sunday → is_weekend = 1
    sun_row = result[result['date'] == pd.Timestamp('2020-01-05')].iloc[0]
    assert sun_row['is_weekend'] == 1


def test_calendar_features_weekday_not_weekend(calendar_df):
    eng = FeatureEngineer()
    result = eng.create_calendar_features(calendar_df)
    # 2020-01-06 is Monday → is_weekend = 0
    mon_row = result[result['date'] == pd.Timestamp('2020-01-06')].iloc[0]
    assert mon_row['is_weekend'] == 0


def test_calendar_features_month_start(calendar_df):
    eng = FeatureEngineer()
    result = eng.create_calendar_features(calendar_df)
    jan1 = result[result['date'] == pd.Timestamp('2020-01-01')].iloc[0]
    assert jan1['is_month_start'] == 1


def test_calendar_features_month_end(calendar_df):
    eng = FeatureEngineer()
    result = eng.create_calendar_features(calendar_df)
    jan31 = result[result['date'] == pd.Timestamp('2020-01-31')].iloc[0]
    assert jan31['is_month_end'] == 1


def test_calendar_features_cyclical_range(calendar_df):
    """sin/cos values must be in [-1, 1]."""
    eng = FeatureEngineer()
    result = eng.create_calendar_features(calendar_df)
    for col in ('day_of_week_sin', 'day_of_week_cos', 'month_sin', 'month_cos'):
        assert result[col].between(-1.0, 1.0).all(), f"{col} out of [-1, 1]"


def test_calendar_features_cyclical_sin_cos_identity(calendar_df):
    """sin² + cos² must equal 1 for each row."""
    eng = FeatureEngineer()
    result = eng.create_calendar_features(calendar_df)
    sq_sum = result['day_of_week_sin'] ** 2 + result['day_of_week_cos'] ** 2
    assert sq_sum.round(10).eq(1.0).all()


def test_calendar_features_expected_columns(simple_df):
    eng = FeatureEngineer()
    result = eng.create_calendar_features(simple_df)
    for col in ('year', 'month', 'day', 'day_of_week', 'is_weekend',
                'is_month_start', 'is_month_end',
                'day_of_week_sin', 'day_of_week_cos',
                'month_sin', 'month_cos'):
        assert col in result.columns, f"Missing column: {col}"


# ---------------------------------------------------------------------------
# create_event_features
# ---------------------------------------------------------------------------

def test_event_features_has_event_1_positive(event_df):
    eng = FeatureEngineer()
    result = eng.create_event_features(event_df)
    # row 1: event_name_1 = 'Christmas' → has_event_1 = 1
    assert result.iloc[1]['has_event_1'] == 1


def test_event_features_has_event_1_negative(event_df):
    eng = FeatureEngineer()
    result = eng.create_event_features(event_df)
    # row 0: event_name_1 = 'None' → has_event_1 = 0
    assert result.iloc[0]['has_event_1'] == 0


def test_event_features_has_any_event(event_df):
    eng = FeatureEngineer()
    result = eng.create_event_features(event_df)
    # rows 1 and 3 have event_name_1 != 'None'
    assert result.iloc[1]['has_any_event'] == 1
    assert result.iloc[3]['has_any_event'] == 1
    # row 0 has no event
    assert result.iloc[0]['has_any_event'] == 0


def test_event_features_no_event_cols_no_error(simple_df):
    """Should not crash when event columns are absent."""
    eng = FeatureEngineer()
    result = eng.create_event_features(simple_df)
    assert result is not None


def test_event_features_has_any_event_always_present(event_df):
    eng = FeatureEngineer()
    result = eng.create_event_features(event_df)
    assert 'has_any_event' in result.columns


# ---------------------------------------------------------------------------
# create_hierarchical_features
# ---------------------------------------------------------------------------

def test_hierarchical_features_store_avg_sales(hierarchical_df):
    """
    Both A and B are in S1. On 2020-01-01: A=2, B=8 → mean=5.
    """
    eng = FeatureEngineer()
    result = eng.create_hierarchical_features(hierarchical_df)
    day1 = result[result['date'] == pd.Timestamp('2020-01-01')]
    assert day1['store_avg_sales'].iloc[0] == pytest.approx(5.0)


def test_hierarchical_features_cat_avg_sales(hierarchical_df):
    """Both items in C1. On day1: mean(2, 8) = 5."""
    eng = FeatureEngineer()
    result = eng.create_hierarchical_features(hierarchical_df)
    day1 = result[result['date'] == pd.Timestamp('2020-01-01')]
    assert day1['cat_avg_sales'].iloc[0] == pytest.approx(5.0)


def test_hierarchical_features_item_share_of_store(hierarchical_df):
    """
    Item A: sales=2, store_avg=5 → share ≈ 2/5 = 0.4.
    """
    eng = FeatureEngineer()
    result = eng.create_hierarchical_features(hierarchical_df)
    row_a = result[(result['id'] == 'A') &
                   (result['date'] == pd.Timestamp('2020-01-01'))].iloc[0]
    assert row_a['item_share_of_store'] == pytest.approx(2.0 / (5.0 + 1e-6), rel=1e-4)


def test_hierarchical_features_expected_columns(hierarchical_df):
    eng = FeatureEngineer()
    result = eng.create_hierarchical_features(hierarchical_df)
    for col in ('store_avg_sales', 'cat_avg_sales',
                'dept_avg_sales', 'state_avg_sales',
                'item_share_of_cat', 'item_share_of_store'):
        assert col in result.columns, f"Missing column: {col}"


def test_hierarchical_features_missing_cols_no_error(simple_df):
    """DataFrame without store/cat/dept/state columns should not crash."""
    eng = FeatureEngineer()
    result = eng.create_hierarchical_features(simple_df)
    assert result is not None


# ---------------------------------------------------------------------------
# feature_names tracking
# ---------------------------------------------------------------------------

def test_feature_names_reset_on_create_all(simple_df):
    """create_all_features resets feature_names before building."""
    eng = FeatureEngineer()
    eng.feature_names = ['stale_feature']
    eng.create_all_features(simple_df, lags=[7], rolling_windows=[7])
    assert 'stale_feature' not in eng.feature_names


def test_get_feature_names_returns_list(simple_df):
    eng = FeatureEngineer()
    eng.create_lag_features(simple_df, lags=[7])
    names = eng.get_feature_names()
    assert isinstance(names, list)
    assert len(names) > 0
