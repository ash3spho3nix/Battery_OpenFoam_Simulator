"""
GUI module for Battery Simulator.

Contains all GUI-related classes and widgets, including the main window
and simulation interfaces. Also includes UI loading infrastructure.
"""

# Import only the UI loader to avoid circular imports
from .ui_loader import UILoader

__all__ = [
    'UILoader'
]
