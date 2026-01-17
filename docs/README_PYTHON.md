# Battery Simulator Python Application

This document provides comprehensive instructions for running and debugging the Battery Simulator Python application after the fixes for import errors and hardcoded values.

## Quick Start

### 1. Test the Application (Recommended First Step)

Before running the main application, run the comprehensive test script to verify all fixes:

```bash
python test_application.py
```

This will test:
- Import statements and Python packaging
- UI loading modes (UI_FILES, HAND_CODED, AUTO_DETECT)
- OpenFOAM integration and solver availability
- Constants and hardcoded UI values
- Application initialization with different configurations

### 2. Run the Main Application

```bash
python src_py/main.py
```

### 3. Run with Specific UI Mode

```bash
# Force .ui file loading
python src_py/main.py --ui-mode ui_files

# Force hand-coded widgets
python src_py/main.py --ui-mode hand_coded

# Auto-detect (default)
python src_py/main.py --ui-mode auto

# Custom .ui file path
python src_py/main.py --ui-path /custom/ui/path

# Disable fallback to hand-coded widgets
python src_py/main.py --no-fallback
```

## Fixed Issues

### 1. Python Packaging Issues

**Problem**: "Import error: relative import with no known parent package"

**Solution**: 
- Updated all import statements to use absolute imports
- Added proper Python path configuration in main modules
- Ensured consistent package structure

**Files Modified**:
- `src_py/main.py` - Fixed import statements and added path configuration
- `src_py/gui/main_window.py` - Updated imports to use absolute paths
- `src_py/gui/ui_config.py` - Fixed import statements
- `src_py/gui/interface_factory.py` - Updated imports and added absolute imports
- `src_py/gui/ui_loader.py` - Fixed import statements

### 2. Hardcoded Values from .ui Files

**Problem**: Hardcoded widget names and values in Python code didn't match .ui files

**Solution**: Extracted and hardcoded values from .ui files into constants.py

**Values Extracted**:
- Widget names from all .ui files (mainwindow.ui, carboninterface.ui, etc.)
- Tab titles and UI text
- Default values for UI controls
- Material and simulation options

**Files Modified**:
- `src_py/core/constants.py` - Added UI_WIDGET_NAMES, UI_TAB_TITLES, UI_DEFAULT_VALUES

## OpenFOAM Integration Debugging

### Comprehensive Debugging Tools

A complete debugging suite has been created in `src_py/utils/debug_utils.py` with the following capabilities:

#### 1. Environment Validation
```python
from src_py.utils.debug_utils import validate_openfoam_installation, check_solver_availability

# Check OpenFOAM installation
is_valid = validate_openfoam_installation()
print(f"OpenFOAM installation valid: {is_valid}")

# Check solver availability
solvers = check_solver_availability()
print(f"Solver status: {solvers}")
```

#### 2. Template File Validation
```python
from src_py.utils.debug_utils import OpenFOAMDebugger

debugger = OpenFOAMDebugger()
template_results = debugger.validate_template_files("/path/to/templates")
```

#### 3. Case Structure Validation
```python
case_results = debugger.validate_case_structure("/path/to/case")
```

#### 4. Solver Execution Monitoring
```python
solver_cmd = ["SPMFoam", "-case", "/path/to/case"]
execution_results = debugger.monitor_solver_execution(solver_cmd, "/path/to/case")
```

#### 5. Generate Debug Report
```python
report_path = debugger.generate_debug_report("/path/to/report.txt")
print(f"Debug report saved to: {report_path}")
```

### Automated Debugging Script

Run comprehensive OpenFOAM integration debugging:

```python
from src_py.utils.debug_utils import debug_openfoam_integration

# Debug entire OpenFOAM integration
debugger = debug_openfoam_integration(
    project_path="/path/to/project",
    case_path="/path/to/case"
)

# Generate comprehensive report
debugger.generate_debug_report()
```

## Application Architecture

### UI Loading Modes

The application supports three UI loading modes with automatic fallback:

1. **UI_FILES**: Load from Qt Designer .ui files at runtime
2. **HAND_CODED**: Use hand-coded PyQt6 widgets
3. **AUTO_DETECT**: Automatically choose based on .ui file availability

### Configuration Options

Configuration can be set via:
- Command line arguments
- Environment variables
- Programmatic configuration

**Environment Variables**:
```bash
export BATTERY_SIM_UI_MODE=ui_files      # or hand_coded, auto
export BATTERY_SIM_UI_PATH=/custom/path  # Custom .ui file path
```

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Import Errors
**Symptom**: "relative import with no known parent package"
**Solution**: Ensure you're running from the project root directory and using the test script first

#### 2. UI Loading Failures
**Symptom**: Application fails to load .ui files
**Solution**: 
- Check .ui files exist in `src_py/resources/ui/`
- Use `--ui-mode hand_coded` to force hand-coded widgets
- Check file permissions on .ui files

#### 3. OpenFOAM Integration Issues
**Symptom**: Solver execution fails or OpenFOAM commands not found
**Solution**:
- Run the OpenFOAM validation test: `python test_application.py --test openfoam`
- Check OpenFOAM environment variables are set
- Verify solver compilation in `$FOAM_APPBIN`

#### 4. Missing Dependencies
**Symptom**: PyQt6 modules not found
**Solution**: Install required packages:
```bash
pip install PyQt6
```

### Debugging Workflow

1. **Run comprehensive tests**:
   ```bash
   python test_application.py
   ```

2. **Check OpenFOAM integration**:
   ```bash
   python test_application.py --test openfoam
   ```

3. **Generate debug report**:
   ```python
   from src_py.utils.debug_utils import debug_openfoam_integration
   debugger = debug_openfoam_integration()
   debugger.generate_debug_report("debug_report.txt")
   ```

4. **Check logs**: Debug information is logged to `debug.log` and stdout

### Performance Monitoring

The debugging tools provide comprehensive performance monitoring:
- Solver execution time tracking
- Memory usage monitoring
- Output analysis and validation
- Convergence checking

## File Structure

```
BatterySimulator/
├── src_py/                     # Python source code
│   ├── main.py                 # Main application entry point (FIXED)
│   ├── core/                   # Core application logic
│   │   └── constants.py        # Application constants (ENHANCED)
│   ├── gui/                    # GUI components
│   │   ├── main_window.py      # Main window (FIXED)
│   │   ├── ui_config.py        # UI configuration (FIXED)
│   │   ├── ui_loader.py        # UI file loader (FIXED)
│   │   ├── interface_factory.py # Interface factory (FIXED)
│   │   └── interfaces/         # Simulation interfaces
│   └── utils/                  # Utility modules
│       └── debug_utils.py      # Debugging tools (NEW)
├── test_application.py         # Comprehensive test script (NEW)
└── README_PYTHON.md           # This file (NEW)
```

## Development Notes

### Adding New UI Files

1. Place .ui files in `src_py/resources/ui/`
2. Update `UI_WIDGET_NAMES` in `constants.py` with widget names
3. Update `UI_TAB_TITLES` with tab titles if needed
4. Update `UI_DEFAULT_VALUES` with default values if needed
5. Test with `python test_application.py`

### Adding New Solvers

1. Update `SOLVER_NAMES` in `constants.py`
2. Add solver compilation check in `debug_utils.py`
3. Update interface factory if needed
4. Test OpenFOAM integration

### Best Practices

1. **Always run tests first**: `python test_application.py`
2. **Use debugging tools**: Leverage the comprehensive debugging suite
3. **Check logs**: Monitor `debug.log` for detailed information
4. **Validate OpenFOAM**: Use the validation tools before running simulations
5. **Test different modes**: Verify application works in all UI loading modes

## Support

For issues or questions:
1. Run the comprehensive test script first
2. Check the debug logs
3. Generate a debug report using the debugging tools
4. Review the troubleshooting guide above

The debugging tools provide comprehensive information to diagnose and resolve issues quickly.
