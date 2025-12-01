"""
Resources module for Battery Simulator.

Contains UI files, templates, and other resource files.
"""

from pathlib import Path

# Resource paths
RESOURCES_PATH = Path(__file__).parent
UI_FILES_PATH = RESOURCES_PATH / "ui"
TEMPLATES_PATH = RESOURCES_PATH / "templates"

__all__ = [
    'RESOURCES_PATH',
    'UI_FILES_PATH', 
    'TEMPLATES_PATH'
]