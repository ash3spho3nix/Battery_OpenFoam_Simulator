"""
Battery Simulator Python Package.

This package provides a GUI interface for creating and running battery simulations
using OpenFOAM solvers, migrated from C++/Qt.

Package Structure:
- core/     : Core application logic and project management
- gui/      : GUI components and interfaces  
- openfoam/ : OpenFOAM integration and process management
- utils/    : Utility functions and helpers
- resources/ : Static resources (templates, UI files)

Key Classes:
- MainWindow: Main application window and project management
- EnhancedProjectManager: Handles project creation and management
- InterfaceFactory: Creates simulation interfaces
- UiLoader: Loads UI files at runtime
- ProcessController: Manages OpenFOAM process execution
- OpenFOAMSolverManager: Manages OpenFOAM solver operations
- TemplateManager: Manages project templates
- ParameterManager: Manages simulation parameters
"""

# Import core modules
from .gui.main_window import MainWindow
from .core.project_manager_enhanced import EnhancedProjectManager as ProjectManager

# Import GUI components
from .gui.interface_factory import InterfaceFactory
from .gui.ui_loader import UiLoader

# Import OpenFOAM integration
from .openfoam.process_controller import ProcessController
from .openfoam.solver_manager import OpenFOAMSolverManager

# Import utilities
from .utils.file_operations import TemplateManager
from .utils.parameter_parser import ParameterManager

# Create aliases for backward compatibility
SolverManager = OpenFOAMSolverManager
FileOperations = TemplateManager
ParameterParser = ParameterManager

# Version information
__version__ = "1.0.0"
__author__ = "Battery Simulator Team"

# Package metadata
__all__ = [
    'MainWindow',
    'ProjectManager', 
    'InterfaceFactory',
    'UiLoader',
    'ProcessController',
    'OpenFOAMSolverManager',
    'SolverManager',  # Alias for backward compatibility
    'TemplateManager',
    'FileOperations',  # Alias for backward compatibility
    'ParameterManager',
    'ParameterParser',  # Alias for backward compatibility
]
