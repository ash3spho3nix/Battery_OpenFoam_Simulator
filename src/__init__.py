"""
Battery Simulator - Python Migration

This package contains the Python implementation of the Battery Simulator application,
migrated from C++/Qt. The application provides a GUI interface for creating and running
battery simulations using OpenFOAM solvers.

Package Structure:
- core/     : Core application logic and project management
- gui/      : GUI components and interfaces  
- openfoam/ : OpenFOAM integration and process management
- utils/    : Utility functions and helpers
- resources/ : Static resources (templates, UI files)

Key Classes:
- MainWindow: Main application window and project management
- ProjectManager: Handles project creation and management
- InterfaceFactory: Creates simulation interfaces
- ProcessController: Manages OpenFOAM process execution
"""

# Import core modules
from .gui.main_window import MainWindow
from .core.project_manager import ProjectManager

# Import GUI components
from .gui.interface_factory import InterfaceFactory
from .gui.ui_loader import UiLoader

# Import OpenFOAM integration
from .openfoam.process_controller import ProcessController
from .openfoam.solver_manager import SolverManager

# Import utilities
from .utils.file_operations import FileOperations
from .utils.parameter_parser import ParameterParser

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
    'SolverManager',
    'FileOperations',
    'ParameterParser'
]