"""
OpenFOAM integration module for Battery Simulator.

Contains classes for managing OpenFOAM solver execution and process control.
"""

from .process_controller import ProcessController
from .solver_manager import OpenFOAMSolverManager

__all__ = [
    'ProcessController',
    'OpenFOAMSolverManager'
]