"""
Package initialization for Battery Simulator application.

This module initializes the application package and provides access to core components.
"""

# Import core components
from src.core.config import ConfigManager

# Initialize configuration
config = ConfigManager()

# Export key components
__all__ = ["config"]
