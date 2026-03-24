"""
Unit tests for src/utils/config.py

Uses pytest's tmp_path fixture to create temporary YAML files,
so no real project config file is required.

Covers:
- Config loading from YAML
- Dot-notation key access (get)
- Default value for missing keys
- FileNotFoundError for missing config file
- Section properties (data, forecasting, simulation, rl, causal)
- Dictionary-style access (__getitem__)
- Config.update
"""

import pytest
import yaml
from src.utils.config import Config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_config(tmp_path, content: dict) -> str:
    """Write a dict as YAML and return the file path as string."""
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(yaml.dump(content))
    return str(cfg_file)


SAMPLE_CONFIG = {
    'data': {
        'raw_path': 'data/raw/m5',
        'processed_path': 'data/processed',
        'sample_size': 100,
    },
    'forecasting': {
        'models': ['arima', 'prophet'],
        'horizon': 28,
    },
    'simulation': {
        'days': 90,
        'holding_cost': 0.5,
    },
    'reinforcement_learning': {
        'algorithm': 'q_learning',
        'episodes': 500,
    },
    'causal': {
        'method': 'dowhy',
    },
}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def test_config_loads_from_valid_yaml(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config is not None


def test_config_raises_for_missing_file(tmp_path):
    missing = str(tmp_path / "does_not_exist.yaml")
    with pytest.raises(FileNotFoundError):
        Config(missing)


# ---------------------------------------------------------------------------
# get() — simple keys
# ---------------------------------------------------------------------------

def test_config_get_top_level_section(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    result = config.get('data')
    assert isinstance(result, dict)
    assert result['raw_path'] == 'data/raw/m5'


def test_config_get_nested_key(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config.get('data.raw_path') == 'data/raw/m5'


def test_config_get_deeply_nested(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config.get('forecasting.horizon') == 28


def test_config_get_integer_value(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config.get('data.sample_size') == 100


def test_config_get_list_value(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    models = config.get('forecasting.models')
    assert isinstance(models, list)
    assert 'arima' in models


# ---------------------------------------------------------------------------
# get() — missing keys and defaults
# ---------------------------------------------------------------------------

def test_config_get_missing_key_returns_none_by_default(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config.get('nonexistent_key') is None


def test_config_get_missing_nested_key_returns_none(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config.get('data.nonexistent_field') is None


def test_config_get_missing_key_returns_custom_default(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config.get('missing', default=42) == 42


def test_config_get_missing_nested_key_returns_custom_default(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config.get('data.missing_field', default='fallback') == 'fallback'


# ---------------------------------------------------------------------------
# __getitem__ (dictionary-style access)
# ---------------------------------------------------------------------------

def test_config_dict_access_top_level(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    result = config['data']
    assert isinstance(result, dict)


def test_config_dict_access_missing_returns_none(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config['totally_missing'] is None


# ---------------------------------------------------------------------------
# Section properties
# ---------------------------------------------------------------------------

def test_config_data_property(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config.data['raw_path'] == 'data/raw/m5'


def test_config_forecasting_property(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config.forecasting['horizon'] == 28


def test_config_simulation_property(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config.simulation['days'] == 90


def test_config_rl_property(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config.rl['algorithm'] == 'q_learning'


def test_config_causal_property(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    assert config.causal['method'] == 'dowhy'


def test_config_missing_section_property_returns_empty_dict(tmp_path):
    """If a section key is absent, the property should return {}."""
    minimal = {'data': {'raw_path': 'x'}}
    path = write_config(tmp_path, minimal)
    config = Config(path)
    assert config.forecasting == {}
    assert config.simulation == {}
    assert config.rl == {}
    assert config.causal == {}


# ---------------------------------------------------------------------------
# update()
# ---------------------------------------------------------------------------

def test_config_update_adds_new_key(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    config.update({'new_section': {'flag': True}})
    assert config.get('new_section') == {'flag': True}


def test_config_update_overwrites_existing_key(tmp_path):
    path = write_config(tmp_path, SAMPLE_CONFIG)
    config = Config(path)
    config.update({'data': {'raw_path': 'new/path'}})
    assert config.get('data.raw_path') == 'new/path'
