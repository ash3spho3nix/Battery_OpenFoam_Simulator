#!/usr/bin/env python3
"""
UI Loader Module

This module provides functionality to load UI files from the resources directory.
It supports both .ui files and hand-coded widgets.
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
    """Handles loading of UI files and hand-coded widgets."""
    
    # Cache for loaded UI metadata
    _ui_metadata_cache: Dict[str, Dict[str, Any]] = {}
    _widget_count_cache: Dict[str, int] = {}
    _last_modified_cache: Dict[str, float] = {}
    
    @classmethod
    def load_ui(cls, ui_name: str, parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """
        Load a UI file and return the widget.
        
        Args:
            ui_name: Name of the UI file (without .ui extension)
            parent: Parent widget
            
        Returns:
            Loaded widget or None if loading failed
        """
        print(f"Loading UI: {ui_name}")
        
        # Remove .ui extension if present to avoid double extension
        if ui_name.endswith('.ui'):
            ui_name = ui_name[:-3]
            
        # Construct the path to the .ui file
        ui_file_path = Path(__file__).parent.parent / "resources" / "ui" / "files" / f"{ui_name}.ui"
        
        print(f"Looking for UI file at: {ui_file_path}")
        
        if not ui_file_path.exists():
            print(f"UI file not found: {ui_file_path}")
            return None
            
        try:
            # Load the UI file
            widget = loadUi(str(ui_file_path), parent)
            print(f"Successfully loaded UI: {ui_name}")
            return widget
        except Exception as e:
            print(f"Failed to load UI {ui_name}: {e}")
            return None

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
