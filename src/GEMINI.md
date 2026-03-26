# BatteryFOAM Simulator - Project Index & Analysis

## 1. Project Overview
BatteryFOAM is a Python-based GUI wrapper for OpenFOAM battery simulations. It manages project creation, case configuration, solver execution, and result visualization.

## 2. Architecture
- **Core**: Configuration (`config.py`, `constants.py`) and Project Management.
- **GUI**: PyQt6-based interface.
  - `MainWindow`: Central hub.
  - `Interfaces`: Module-specific screens (Carbon, HalfCell, FullCell).
  - `UILoader`: Dynamic UI file loading.
- **OpenFOAM**: Backend integration.
  - `ProcessController`: Manages external processes.
  - `SolverManager`: Handles solver execution.
  - `CaseManager`: Manages OpenFOAM case directories.
- **Utils**: Helper utilities.
  - `ErrorRecovery`: Robust error handling strategies.
  - `FileOperations`: Template and file management.

## 3. Component Index

### Core (`src/core/`)
- `config.py`: Configuration manager class.
- `constants.py`: Static constants and definitions.

### GUI (`src/gui/`)
- `interfaces/carbon_interface.py`: Interface for Single Particle Model.
- `ui_loader.py`: Utility to load .ui files.

### OpenFOAM (`src/openfoam/`)
- `process_controller.py`: QProcess wrapper for async execution.
- `solver_manager.py`: Manages solver binaries and commands.
- `case_manager.py`: Handles case directory structure.

### Utils (`src/utils/`)
- `error_recovery.py`: Advanced error recovery system.

### Tests (`tests/`)
- `unit/test_openfoam/test_openfoam_integration.py`: Integration tests.
- `unit/test_gui_components.py`: GUI component tests.
- `test_imports.py`: Import validity tests.

## 4. Current Status & Issues
- **Duplicate Code**: Duplicate test classes found in integration tests.
- **Naming Inconsistencies**: `UiLoader` vs `UILoader` causing import errors.
- **Configuration Split**: Config data split between `config.py` and `constants.py`.
- **Widget Access**: Direct widget access in interfaces reduces flexibility.
