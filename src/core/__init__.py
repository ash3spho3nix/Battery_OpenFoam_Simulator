"""
Core module for Battery Simulator.

Contains the main application logic, project management, and constants.
"""

from .project_manager import ProjectManager
from .constants import *

__all__ = [
    'ProjectManager',
    'APP_NAME',
    'APP_VERSION',
    'SUPPORTED_MODULES',
    'DEFAULT_PROJECT_PATH',
    'MODULE_DESCRIPTIONS',
    'UI_FILES_PATH',
    'TEMPLATES_PATH'
]
