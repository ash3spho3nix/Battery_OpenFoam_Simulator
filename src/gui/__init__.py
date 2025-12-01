"""
GUI module for Battery Simulator.

Contains all GUI-related classes and widgets, including the main window
and simulation interfaces. Also includes UI loading infrastructure.
"""

from .main_window import MainWindow
from .ui_loader import UILoader
from .ui_config import UIConfig, UILoadingMode
from .interface_factory import InterfaceFactory
from .interfaces.base_interface import BaseInterface
from .interfaces.carbon_interface import CarbonInterface
from .interfaces.halfcell_interface import HalfCellInterface
from .interfaces.fullcell_interface import FullCellInterface
from .interfaces.result_interface import ResultInterface

__all__ = [
    'MainWindow',
    'UILoader',
    'UIConfig',
    'UILoadingMode',
    'InterfaceFactory',
    'BaseInterface',
    'CarbonInterface',
    'HalfCellInterface',
    'FullCellInterface',
    'ResultInterface'
]