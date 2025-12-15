#!/usr/bin/env python3
"""
UI Loader Module - Direct UI File Loading.

This module provides functionality to load UI files directly from the resources directory.
It supports only .ui files with robust error handling and user-friendly error messages.
"""

import os
import sys
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any, Callable, Tuple
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QMetaObject
from PyQt6.QtGui import QGuiApplication
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QMessageBox

class UiLoader:
    """Handles loading of UI files directly without fallback."""
    
    # Cache for loaded UI metadata
    _ui_metadata_cache: Dict[str, Dict[str, Any]] = {}
    _widget_count_cache: Dict[str, int] = {}
    _last_modified_cache: Dict[str, float] = {}
    
    @classmethod
    def load_ui(cls, ui_name: str, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """
        Load a UI file directly and return the widget.
        
        Args:
            ui_name: Name of the UI file (without .ui extension)
            parent: Parent widget
            
        Returns:
            Loaded widget or None if loading failed
            
        Raises:
            FileNotFoundError: If UI file doesn't exist
            Exception: If UI file is corrupted or invalid
        """
        print(f"Loading UI: {ui_name}")
        
        # Remove .ui extension if present to avoid double extension
        if ui_name.endswith('.ui'):
            ui_name = ui_name[:-3]
            
        # Construct the path to the .ui file
        ui_file_path = Path(__file__).parent.parent / "resources" / "ui" / "files" / f"{ui_name}.ui"
        
        print(f"Looking for UI file at: {ui_file_path}")
        
        if not ui_file_path.exists():
            error_msg = f"UI file not found: {ui_file_path}"
            print(error_msg)
            raise FileNotFoundError(error_msg)
            
        try:
            # Load the UI file
            widget = loadUi(str(ui_file_path), parent)
            print(f"Successfully loaded UI: {ui_name}")
            return widget
        except Exception as e:
            error_msg = f"Failed to load UI {ui_name}: {e}"
            print(error_msg)
            raise Exception(error_msg)
    
    @classmethod
    def get_ui_path(cls, ui_name: str, base_path: Optional[str] = None) -> str:
        """
        Get the full path to a UI file.
        
        Args:
            ui_name: Name of the UI file (without .ui extension)
            base_path: Optional custom base path
            
        Returns:
            Full path to the UI file
        """
        if base_path:
            return str(Path(base_path) / f"{ui_name}.ui")
        else:
            return str(Path(__file__).parent.parent / "resources" / "ui" / "files" / f"{ui_name}.ui")
    
    @classmethod
    def ui_file_exists(cls, ui_name: str, base_path: Optional[str] = None) -> bool:
        """
        Check if a UI file exists.
        
        Args:
            ui_name: Name of the UI file (without .ui extension)
            base_path: Optional custom base path
            
        Returns:
            True if the file exists, False otherwise
        """
        ui_path = cls.get_ui_path(ui_name, base_path)
        return os.path.exists(ui_path)
    
    @classmethod
    def validate_ui_integrity(cls, ui_path: str) -> bool:
        """
        Validate that a UI file is well-formed XML.
        
        Args:
            ui_path: Path to the UI file
            
        Returns:
            True if the file is valid XML, False otherwise
        """
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(ui_path)
            root = tree.getroot()
            return root.tag == 'ui'
        except Exception:
            return False

def main():
    """Test the UI loader."""
    app = QApplication(sys.argv)
    
    # Test loading a UI
    widget = UiLoader.load_ui("mainwindow")
    if widget:
        widget.show()
        sys.exit(app.exec())
    else:
        print("Failed to load UI")
        sys.exit(1)

if __name__ == "__main__":
    main()
