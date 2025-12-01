# UI Loading Implementation Plan

## Overview

This document provides a detailed implementation plan for adding .ui file loading capability to the Battery Simulator Python migration. The implementation will support both .ui file loading and the current hand-coded approach, giving users the choice at startup.

## Implementation Strategy

### Option 1: Runtime .ui File Loading (Recommended)

Load .ui files dynamically at runtime using `uic.loadUi()`. This approach:
- ✅ Maintains 100% compatibility with original C++ .ui files
- ✅ Allows UI modifications without code changes
- ✅ Supports both .ui and hand-coded approaches
- ✅ Easy to implement and maintain

### Option 2: Pre-compiled .ui Files

Convert .ui files to Python code using `pyuic6`. This approach:
- ✅ Better performance (no runtime loading)
- ✅ IDE support for .ui classes
- ❌ Requires regeneration when .ui files change
- ❌ More complex maintenance

## Implementation Plan

### Phase 1: Create UI Loading Infrastructure

#### 1.1 Create UI Loader Module
```python
# src_py/gui/ui_loader.py
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
import os
from pathlib import Path

class UILoader:
    """Handles loading of .ui files at runtime."""
    
    @staticmethod
    def load_ui_file(ui_file_path: str, parent: QWidget = None):
        """Load a .ui file and return the widget."""
        if not os.path.exists(ui_file_path):
            raise FileNotFoundError(f"UI file not found: {ui_file_path}")
        
        return uic.loadUi(ui_file_path, parent)
    
    @staticmethod
    def get_ui_path(ui_name: str) -> str:
        """Get the full path to a .ui file."""
        ui_dir = Path(__file__).parent.parent.parent / "resources" / "ui"
        return str(ui_dir / f"{ui_name}.ui")
```

#### 1.2 Create UI Configuration
```python
# src_py/gui/ui_config.py
from enum import Enum

class UILoadingMode(Enum):
    """UI loading modes."""
    UI_FILES = "ui_files"           # Load from .ui files
    HAND_CODED = "hand_coded"       # Use hand-coded widgets
    AUTO_DETECT = "auto_detect"     # Auto-detect based on availability

class UIConfig:
    """Configuration for UI loading."""
    
    def __init__(self):
        self.mode = UILoadingMode.AUTO_DETECT
        self.prefer_ui_files = True
        self.fallback_to_hand_coded = True
    
    @classmethod
    def from_environment(cls):
        """Create config from environment variables."""
        config = cls()
        
        # Check environment variable
        import os
        ui_mode = os.environ.get("BATTERY_SIM_UI_MODE", "").lower()
        
        if ui_mode == "ui_files":
            config.mode = UILoadingMode.UI_FILES
        elif ui_mode == "hand_coded":
            config.mode = UILoadingMode.HAND_CODED
        elif ui_mode == "auto":
            config.mode = UILoadingMode.AUTO_DETECT
            
        return config
```

### Phase 2: Modify Application Entry Point

#### 2.1 Update main.py
```python
# src_py/main.py
import sys
import os
from pathlib import Path

# Add the src_py directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QIcon

from .gui.main_window import MainWindow
from .gui.ui_config import UIConfig
from .core.constants import APP_NAME, APP_VERSION


def main():
    """
    Main application entry point.
    
    Creates QApplication, MainWindow, and starts the event loop.
    """
    # Set application metadata
    QCoreApplication.setApplicationName(APP_NAME)
    QCoreApplication.setApplicationVersion(APP_VERSION)
    QCoreApplication.setOrganizationName("BatterySimulator")
    QCoreApplication.setOrganizationDomain("batterysimulator.example.com")
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Set application style (similar to C++)
    app.setStyle("Fusion")
    
    # Create main window with UI configuration
    ui_config = UIConfig.from_environment()
    window = MainWindow(ui_config=ui_config)
    window.show()
    
    # Start event loop
    return app.exec()


if __name__ == "__main__":
    # Handle Windows-specific path issues
    if sys.platform == "win32":
        # Ensure proper handling of Windows paths
        os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + os.getcwd()
    
    # Run the application
    exit_code = main()
    sys.exit(exit_code)
```

### Phase 3: Update MainWindow to Support UI Loading

#### 3.1 Modify MainWindow
```python
# src_py/gui/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from .ui_loader import UILoader
from .ui_config import UIConfig, UILoadingMode
from core.application import BatterySimulatorApp


class MainWindow(QMainWindow):
    """
    Main window for Battery Simulator GUI.
    
    This class provides a simplified main window interface that can load
    either from .ui files or use the hand-coded approach.
    """
    
    def __init__(self, parent=None, ui_config=None):
        """
        Initialize the main window.
        
        Args:
            parent: Parent widget
            ui_config: UI configuration for loading mode
        """
        super().__init__(parent)
        
        self.ui_config = ui_config or UIConfig()
        
        # Try to load from .ui file first if configured
        if self._should_load_ui_file():
            try:
                self._load_from_ui_file()
            except Exception as e:
                print(f"Failed to load .ui file: {e}")
                if self.ui_config.fallback_to_hand_coded:
                    self._create_hand_coded_ui()
                else:
                    raise
        else:
            self._create_hand_coded_ui()
            
    def _should_load_ui_file(self) -> bool:
        """Determine if we should try loading from .ui file."""
        if self.ui_config.mode == UILoadingMode.UI_FILES:
            return True
        elif self.ui_config.mode == UILoadingMode.HAND_CODED:
            return False
        elif self.ui_config.mode == UILoadingMode.AUTO_DETECT:
            # Check if .ui files exist
            ui_loader = UILoader()
            try:
                ui_path = ui_loader.get_ui_path("mainwindow")
                return os.path.exists(ui_path)
            except:
                return False
        return False
        
    def _load_from_ui_file(self):
        """Load the main window from .ui file."""
        ui_loader = UILoader()
        ui_path = ui_loader.get_ui_path("mainwindow")
        
        # Load the .ui file
        self.ui_widget = ui_loader.load_ui_file(ui_path, self)
        
        # Set the loaded widget as central widget
        self.setCentralWidget(self.ui_widget)
        
        # Connect signals if needed
        self._connect_ui_signals()
        
    def _create_hand_coded_ui(self):
        """Create the hand-coded UI (current implementation)."""
        # Create the main application
        self.app = BatterySimulatorApp()
        
        # Set this window as the central widget
        self.setCentralWidget(self.app)
        
        # Copy window properties
        self.setWindowTitle(self.app.windowTitle())
        self.setMinimumSize(self.app.minimumSize())
        self.setMaximumSize(self.app.maximumSize())
        
    def _connect_ui_signals(self):
        """Connect signals for .ui-based interface."""
        # Connect signals from .ui file to handlers
        if hasattr(self.ui_widget, 'main_path_button'):
            self.ui_widget.main_path_button.clicked.connect(self._on_main_path_button_clicked)
        if hasattr(self.ui_widget, 'main_next_button'):
            self.ui_widget.main_next_button.clicked.connect(self._on_main_next_button_clicked)
        # ... connect other signals
        
    def _on_main_path_button_clicked(self):
        """Handle main path button click."""
        # Implementation for .ui-based interface
        pass
        
    def _on_main_next_button_clicked(self):
        """Handle main next button click."""
        # Implementation for .ui-based interface
        pass
        
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Ensures proper cleanup of the application.
        """
        # Close any open interfaces
        if hasattr(self, 'app') and self.app:
            if hasattr(self.app, 'carbon_interface') and self.app.carbon_interface:
                self.app.carbon_interface.close()
            if hasattr(self.app, 'halfcell_interface') and self.app.halfcell_interface:
                self.app.halfcell_interface.close()
            if hasattr(self.app, 'fullcell_interface') and self.app.fullcell_interface:
                self.app.fullcell_interface.close()
                
        # Accept the close event
        event.accept()
```

### Phase 4: Create Interface Factory

#### 4.1 Interface Factory
```python
# src_py/gui/interface_factory.py
from .ui_loader import UILoader
from .ui_config import UIConfig, UILoadingMode
from .interfaces.base_interface import BaseInterface
from pathlib import Path
import os

class InterfaceFactory:
    """Factory for creating simulation interfaces."""
    
    @staticmethod
    def create_interface(interface_type: str, parent=None, ui_config=None):
        """
        Create an interface based on type and configuration.
        
        Args:
            interface_type: Type of interface (carbon, halfcell, fullcell, result)
            parent: Parent widget
            ui_config: UI configuration
        """
        ui_config = ui_config or UIConfig()
        
        if ui_config.mode == UILoadingMode.UI_FILES or \
           (ui_config.mode == UILoadingMode.AUTO_DETECT and InterfaceFactory._ui_file_exists(interface_type)):
            
            try:
                return InterfaceFactory._create_ui_based_interface(interface_type, parent)
            except Exception as e:
                print(f"Failed to create UI-based interface: {e}")
                if ui_config.fallback_to_hand_coded:
                    return InterfaceFactory._create_hand_coded_interface(interface_type, parent)
                else:
                    raise
        else:
            return InterfaceFactory._create_hand_coded_interface(interface_type, parent)
    
    @staticmethod
    def _ui_file_exists(interface_type: str) -> bool:
        """Check if .ui file exists for the interface type."""
        ui_loader = UILoader()
        try:
            ui_path = ui_loader.get_ui_path(interface_type)
            return os.path.exists(ui_path)
        except:
            return False
    
    @staticmethod
    def _create_ui_based_interface(interface_type: str, parent):
        """Create interface from .ui file."""
        ui_loader = UILoader()
        ui_path = ui_loader.get_ui_path(interface_type)
        
        # Load the .ui file
        interface = ui_loader.load_ui_file(ui_path, parent)
        
        # Set interface type for signal handling
        interface.interface_type = interface_type
        
        return interface
    
    @staticmethod
    def _create_hand_coded_interface(interface_type: str, parent):
        """Create hand-coded interface."""
        if interface_type == "carbon":
            from .interfaces.carbon_interface import CarbonInterface
            return CarbonInterface(parent)
        elif interface_type == "halfcell":
            from .interfaces.halfcell_interface import HalfCellInterface
            return HalfCellInterface(parent)
        elif interface_type == "fullcell":
            from .interfaces.fullcell_interface import FullCellInterface
            return FullCellInterface(parent)
        elif interface_type == "result":
            from .interfaces.result_interface import ResultInterface
            return ResultInterface(parent)
        else:
            raise ValueError(f"Unknown interface type: {interface_type}")
```

### Phase 5: Update Application to Use Factory

#### 5.1 Update BatterySimulatorApp
```python
# src_py/core/application.py
from .interface_factory import InterfaceFactory

class BatterySimulatorApp(QMainWindow):
    # ... existing code ...
    
    def on_main_next_button_clicked(self):
        """
        Handle new project creation.
        
        Validates input and creates new project with selected module.
        """
        # ... existing validation code ...
        
        try:
            # Create project
            self.project_manager.create_project(
                self.project_path, self.project_name, module
            )
            
            # Hide main window and show appropriate interface
            self.hide()
            
            # Use interface factory to create the appropriate interface
            interface_type = self._get_interface_type(module)
            self.current_interface = InterfaceFactory.create_interface(
                interface_type, self, self.ui_config
            )
            self.current_interface.show()
            
            # Connect exit signal
            if hasattr(self.current_interface, 'exit_signal'):
                self.current_interface.exit_signal.connect(self.show)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create project: {str(e)}")
    
    def _get_interface_type(self, module: str) -> str:
        """Get the interface type for a module."""
        interface_map = {
            "SPM": "carbon",
            "halfCell": "halfcell", 
            "fullCell": "fullcell"
        }
        return interface_map.get(module, "carbon")
```

## Usage Examples

### Environment Variable Configuration

```bash
# Force .ui file loading
export BATTERY_SIM_UI_MODE=ui_files
python src_py/main.py

# Force hand-coded loading
export BATTERY_SIM_UI_MODE=hand_coded
python src_py/main.py

# Auto-detect (default)
export BATTERY_SIM_UI_MODE=auto
python src_py/main.py
```

### Command Line Arguments

```python
# Add to main.py
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ui-mode', choices=['ui_files', 'hand_coded', 'auto'], 
                       default='auto')
    args = parser.parse_args()
    
    # Set environment variable
    os.environ['BATTERY_SIM_UI_MODE'] = args.ui_mode
    
    # ... rest of main function
```

## File Structure After Implementation

```
src_py/
├── main.py                          # Updated with UI config
├── gui/
│   ├── __init__.py
│   ├── main_window.py               # Updated with .ui loading
│   ├── ui_loader.py                 # NEW: .ui file loading
│   ├── ui_config.py                 # NEW: UI configuration
│   ├── interface_factory.py         # NEW: Interface factory
│   ├── main_window.py               # Updated
│   └── interfaces/
│       ├── base_interface.py        # Existing
│       └── *.py                     # Existing interfaces
├── resources/
│   └── ui/                          # Directory for .ui files
│       ├── mainwindow.ui            # Copy from SourceCode/
│       ├── carboninterface.ui       # Copy from SourceCode/
│       ├── halfcellinterface.ui     # Copy from SourceCode/
│       ├── fullcellfoam.ui          # Copy from SourceCode/
│       └── resultinterface.ui       # Copy from SourceCode/
└── core/
    └── application.py               # Updated with factory
```

## Implementation Steps

### Step 1: Create Directory Structure
```bash
mkdir src_py/resources/ui
```

### Step 2: Copy .ui Files
```bash
cp SourceCode/mainwindow.ui src_py/resources/ui/
cp SourceCode/carboninterface.ui src_py/resources/ui/
cp SourceCode/halfcellinterface.ui src_py/resources/ui/
cp SourceCode/fullcellfoam.ui src_py/resources/ui/
cp SourceCode/resultinterface.ui src_py/resources/ui/
```

### Step 3: Create New Modules
1. Create `ui_loader.py`
2. Create `ui_config.py`
3. Create `interface_factory.py`

### Step 4: Update Existing Modules
1. Update `main.py` to support UI configuration
2. Update `main_window.py` to support .ui loading
3. Update `application.py` to use interface factory

### Step 5: Test Different Modes
1. Test with `BATTERY_SIM_UI_MODE=ui_files`
2. Test with `BATTERY_SIM_UI_MODE=hand_coded`
3. Test with `BATTERY_SIM_UI_MODE=auto`

## Benefits

1. **Backward Compatibility**: Existing hand-coded interfaces still work
2. **Forward Compatibility**: Easy migration to .ui files
3. **Flexibility**: Users can choose loading mode
4. **Maintainability**: UI changes don't require code changes
5. **Development**: UI designers can use Qt Designer

## Next Steps

1. **Phase 4 Implementation**: Complete the .ui file loading infrastructure
2. **Testing**: Test both loading modes thoroughly
3. **Documentation**: Update README with usage instructions
4. **Migration**: Gradually migrate interfaces to use .ui files

This implementation provides a robust foundation for supporting both .ui file loading and hand-coded approaches, giving users maximum flexibility while maintaining compatibility with the original C++ design.