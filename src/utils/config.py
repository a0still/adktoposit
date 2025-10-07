"""Configuration management for the application."""
import os
from typing import Dict, Any
import yaml

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file and environment variables.
    
    Args:
        config_path: Path to the configuration YAML file
        
    Returns:
        Dictionary containing configuration values
    """
    config = {
        'project_id': os.getenv('GOOGLE_CLOUD_PROJECT', 'wmt-us-gg-shrnk-prod'),
        'location': os.getenv('VERTEX_LOCATION', 'us-central1'),
        'debug': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        'port': int(os.getenv('PORT', '8080')),
    }
    
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
            config.update(yaml_config)
    
    return config

def get_vertex_config() -> Dict[str, Any]:
    """
    Get Vertex AI specific configuration.
    
    Returns:
        Dictionary containing Vertex AI configuration
    """
    return {
        'project_id': os.getenv('GOOGLE_CLOUD_PROJECT', 'wmt-us-gg-shrnk-prod'),
        'location': os.getenv('VERTEX_LOCATION', 'us-central1'),
        'model_name': os.getenv('VERTEX_MODEL', 'gemini-2.0-flash-001'),
        'temperature': float(os.getenv('VERTEX_TEMPERATURE', '0.7')),
        'top_p': float(os.getenv('VERTEX_TOP_P', '0.8')),
        'top_k': int(os.getenv('VERTEX_TOP_K', '40')),
    }