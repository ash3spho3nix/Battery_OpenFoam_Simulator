"""
UI Loader for Battery Simulator.

This module provides functionality to load Qt Designer .ui files at runtime
using PyQt6's uic.loadUi() function. This allows for dynamic UI loading
and maintains compatibility with the original C++ .ui files.
"""

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
import os
from pathlib import Path
from typing import Optional


class UILoader:
    """
    Handles loading of .ui files at runtime.
    
    This class provides methods to load .ui files dynamically, making it
    possible to use the original Qt Designer files without converting them
    to Python code.
    """
    
    @staticmethod
    def load_ui_file(ui_file_path: str, parent: Optional[QWidget] = None) -> QWidget:
        """
        Load a .ui file and return the widget.
        
        Args:
            ui_file_path: Path to the .ui file
            parent: Parent widget (optional)
            
        Returns:
            QWidget: The loaded widget
            
        Raises:
            FileNotFoundError: If the .ui file doesn't exist
            Exception: If loading fails for any reason
        """
        if not os.path.exists(ui_file_path):
            raise FileNotFoundError(f"UI file not found: {ui_file_path}")
        
        try:
            # Load the .ui file using PyQt6's uic
            widget = uic.loadUi(ui_file_path, parent)
            return widget
        except Exception as e:
            raise Exception(f"Failed to load UI file {ui_file_path}: {str(e)}")
    
    @staticmethod
    def get_ui_path(ui_name: str, base_path: Optional[str] = None) -> str:
        """
        Get the full path to a .ui file.
        
        Args:
            ui_name: Name of the UI file (without .ui extension)
            base_path: Base path to search for UI files (optional)
            
        Returns:
            str: Full path to the .ui file
        """
        if base_path is None:
            # Default to resources/ui directory
            base_path = Path(__file__).parent.parent.parent / "resources" / "ui"
        else:
            base_path = Path(base_path)
            
        ui_file_path = base_path / f"{ui_name}.ui"
        return str(ui_file_path)
    
    @staticmethod
    def ui_file_exists(ui_name: str, base_path: Optional[str] = None) -> bool:
        """
        Check if a .ui file exists.
        
        Args:
            ui_name: Name of the UI file (without .ui extension)
            base_path: Base path to search for UI files (optional)
            
        Returns:
            bool: True if the file exists
        """
        ui_path = UILoader.get_ui_path(ui_name, base_path)
        return os.path.exists(ui_path)
    
    @staticmethod
    def get_available_ui_files(base_path: Optional[str] = None) -> list:
        """
        Get a list of available .ui files.
        
        Args:
            base_path: Base path to search for UI files (optional)
            
        Returns:
            list: List of available .ui file names (without extension)
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent / "resources" / "ui"
        else:
            base_path = Path(base_path)
            
        if not base_path.exists():
            return []
            
        ui_files = []
        for file_path in base_path.glob("*.ui"):
            ui_files.append(file_path.stem)
            
        return sorted(ui_files)
    
    @staticmethod
    def load_main_window(parent: Optional[QWidget] = None) -> QWidget:
        """
        Load the main window from .ui file.
        
        Args:
            parent: Parent widget (optional)
            
        Returns:
            QWidget: The loaded main window widget
        """
        ui_path = UILoader.get_ui_path("mainwindow")
        return UILoader.load_ui_file(ui_path, parent)
    
    @staticmethod
    def load_carbon_interface(parent: Optional[QWidget] = None) -> QWidget:
        """
        Load the carbon interface from .ui file.
        
        Args:
            parent: Parent widget (optional)
            
        Returns:
            QWidget: The loaded carbon interface widget
        """
        ui_path = UILoader.get_ui_path("carboninterface")
        return UILoader.load_ui_file(ui_path, parent)
    
    @staticmethod
    def load_halfcell_interface(parent: Optional[QWidget] = None) -> QWidget:
        """
        Load the half-cell interface from .ui file.
        
        Args:
            parent: Parent widget (optional)
            
        Returns:
            QWidget: The loaded half-cell interface widget
        """
        ui_path = UILoader.get_ui_path("halfcellinterface")
        return UILoader.load_ui_file(ui_path, parent)
    
    @staticmethod
    def load_fullcell_interface(parent: Optional[QWidget] = None) -> QWidget:
        """
        Load the full-cell interface from .ui file.
        
        Args:
            parent: Parent widget (optional)
            
        Returns:
            QWidget: The loaded full-cell interface widget
        """
        ui_path = UILoader.get_ui_path("fullcellfoam")
        return UILoader.load_ui_file(ui_path, parent)
    
    @staticmethod
    def load_result_interface(parent: Optional[QWidget] = None) -> QWidget:
        """
        Load the result interface from .ui file.
        
        Args:
            parent: Parent widget (optional)
            
        Returns:
            QWidget: The loaded result interface widget
        """
        ui_path = UILoader.get_ui_path("resultinterface")
        return UILoader.load_ui_file(ui_path, parent)
