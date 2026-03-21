"""
Configuration loader utility for ASCDT project.
"""

import yaml
from pathlib import Path
from typing import Any, Dict
import os


class Config:
    """Configuration manager for the project."""
    
    def __init__(self, config_path: str = "configs/config.yaml"):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports nested keys with dot notation).
        
        Args:
            key: Configuration key (e.g., 'data.raw_path')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access."""
        return self.get(key)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of updates
        """
        self._config.update(updates)
        
    def save(self, path: str = None) -> None:
        """
        Save configuration to file.
        
        Args:
            path: Path to save (defaults to original path)
        """
        save_path = Path(path) if path else self.config_path
        
        with open(save_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)
            
    @property
    def data(self) -> Dict[str, Any]:
        """Get data configuration."""
        return self._config.get('data', {})
    
    @property
    def forecasting(self) -> Dict[str, Any]:
        """Get forecasting configuration."""
        return self._config.get('forecasting', {})
    
    @property
    def simulation(self) -> Dict[str, Any]:
        """Get simulation configuration."""
        return self._config.get('simulation', {})
    
    @property
    def rl(self) -> Dict[str, Any]:
        """Get RL configuration."""
        return self._config.get('reinforcement_learning', {})
    
    @property
    def causal(self) -> Dict[str, Any]:
        """Get causal configuration."""
        return self._config.get('causal', {})
    

# Global config instance
_config = None

def get_config(config_path: str = "configs/config.yaml") -> Config:
    """
    Get global configuration instance.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
