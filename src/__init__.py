"""
Battery Simulator - Python Migration

This package contains the Python implementation of the Battery Simulator,
migrated from C++/Qt to maintain compatibility with OpenFOAM solvers
while providing a modern Python codebase.

Author: Migration Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Battery Simulator Migration Team"

# Import core modules
from .core.application import BatterySimulatorApp
from .core.project_manager import ProjectManager
from .core.constants import *

# Import GUI modules
from .gui.main_window import MainWindow

# Import OpenFOAM integration
from .openfoam.solver_manager import OpenFOAMSolverManager
from .openfoam.process_controller import ProcessController

# Import utilities
from .utils.file_operations import TemplateManager
from .utils.parameter_parser import ParameterManager

__all__ = [
    # Core classes
    'BatterySimulatorApp',
    'ProjectManager',
    
    # GUI classes
    'MainWindow',
    
    # OpenFOAM integration
    'OpenFOAMSolverManager',
    'ProcessController',
    
    # Utilities
    'TemplateManager',
    'ParameterManager',
    
    # Constants
    'APP_NAME',
    'APP_VERSION',
    'SUPPORTED_MODULES',
    'DEFAULT_PROJECT_PATH'
]