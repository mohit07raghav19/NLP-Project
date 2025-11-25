"""
Configuration Loading Utilities

Load and manage project configuration from YAML and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file and environment variables.
    
    Args:
        config_path: Path to config.yaml (default: config/config.yaml)
        
    Returns:
        Configuration dictionary
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Default config path
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    
    # Load YAML config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables where applicable
    if os.getenv("NVD_API_KEY"):
        config.setdefault('data_collection', {}).setdefault('nvd_api', {})['api_key'] = os.getenv("NVD_API_KEY")
    
    if os.getenv("DATABASE_URL"):
        config.setdefault('database', {})['url'] = os.getenv("DATABASE_URL")
    
    if os.getenv("DEBUG"):
        config.setdefault('api', {})['debug'] = os.getenv("DEBUG").lower() == 'true'
    
    return config


def get_database_url() -> str:
    """Get database URL from environment or config."""
    return os.getenv("DATABASE_URL", "sqlite:///data/cve_database.db")


def get_api_key() -> Optional[str]:
    """Get NVD API key from environment."""
    return os.getenv("NVD_API_KEY")


def get_data_dir() -> Path:
    """Get data directory path."""
    return Path(__file__).parent.parent.parent / "data"


def get_cache_dir() -> Path:
    """Get cache directory path."""
    cache_dir = get_data_dir() / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


# Example usage
if __name__ == "__main__":
    config = load_config()
    print("Configuration loaded successfully!")
    print(f"Database type: {config.get('database', {}).get('type')}")
    print(f"NLP spaCy model: {config.get('nlp', {}).get('spacy', {}).get('model')}")
