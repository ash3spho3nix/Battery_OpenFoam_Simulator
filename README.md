# Battery Simulator - Python Implementation

This directory contains the Python implementation of the Battery Simulator, migrated from C++/Qt to maintain compatibility with OpenFOAM solvers while providing a modern Python codebase.

Inspired from : https://github.com/KinomotoTomoyo/BatterySimulator.git
Kudos and thanks to https://github.com/KinomotoTomoyo and https://github.com/Jason-Imperial

## Project Structure

```
src_py/
├── __init__.py                 # Package initialization
├── main.py                     # Application entry point
├── requirements.txt             # Python dependencies
├── core/                      # Core application logic
│   ├── __init__.py
│   ├── application.py         # Main application (MainWindow equivalent)
│   ├── project_manager.py     # Project creation/management
│   └── constants.py           # Application constants
├── gui/                       # GUI components
│   ├── __init__.py
│   ├── main_window.py         # Main window wrapper
│   ├── ui_loader.py           # Runtime .ui file loading
│   ├── ui_config.py           # UI configuration management
│   ├── interface_factory.py   # Interface creation factory
│   └── interfaces/            # Simulation interfaces
│       ├── __init__.py
│       ├── base_interface.py  # Base interface class
│       ├── carbon_interface.py    # SPM interface (stub)
│       ├── halfcell_interface.py  # P2D Half Cell interface (stub)
│       ├── fullcell_interface.py  # P2D Full Cell interface (stub)
│       └── result_interface.py    # Results interface (stub)
├── openfoam/                  # OpenFOAM integration
│   ├── __init__.py
│   ├── process_controller.py  # Process management (subprocess)
│   └── solver_manager.py      # Solver execution
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── file_operations.py     # Template and file management
│   └── parameter_parser.py    # Parameter file parsing
└── resources/                 # Static resources
    ├── __init__.py
    ├── ui/                    # Qt Designer UI files
    │   ├── mainwindow.ui      # Main window design
    │   ├── carboninterface.ui # SPM interface design
    │   ├── halfcellinterface.ui # Half-cell interface design
    │   ├── fullcellfoam.ui    # Full-cell interface design
    │   └── resultinterface.ui # Results interface design
    └── templates/             # OpenFOAM templates
        └── README.md
```

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure OpenFOAM is installed and accessible from command line

## Usage

### Running the Application

```bash
python src_py/main.py
```

### UI Loading Modes

The application supports multiple UI loading modes for flexibility and compatibility:

#### 1. Auto-Detect Mode (Default)
Automatically detects available .ui files and loads them if present, falling back to hand-coded widgets if needed.

```bash
python src_py/main.py
# or
python src_py/main.py --ui-mode auto
```

#### 2. Force .ui File Loading
Loads all interfaces from Qt Designer .ui files at runtime.

```bash
python src_py/main.py --ui-mode ui_files
# or
BATTERY_SIM_UI_MODE=ui_files python src_py/main.py
```

#### 3. Force Hand-Coded Widgets
Uses the original hand-coded PyQt6 widgets instead of .ui files.

```bash
python src_py/main.py --ui-mode hand_coded
# or
BATTERY_SIM_UI_MODE=hand_coded python src_py/main.py
```

#### 4. Custom .ui File Path
Specify a custom directory for .ui files.

```bash
python src_py/main.py --ui-path /custom/path/to/ui/files
# or
BATTERY_SIM_UI_PATH=/custom/path/to/ui/files python src_py/main.py
```

#### 5. Disable Fallback
Prevent fallback to hand-coded widgets if .ui loading fails.

```bash
python src_py/main.py --no-fallback
```

### Project Creation

The application supports creating projects for three simulation modules:

1. **SPM (Single Particle Model)** - Basic battery simulation
2. **P2D Half Cell** - Pseudo-2D half-cell configuration
3. **P2D Full Cell** - Pseudo-2D full-cell configuration

### Interface Features

Each simulation interface provides:

- **Geometry Configuration**: Set dimensions, radius, and units
- **Constants Setup**: Material properties and electrochemical parameters
- **Boundary Conditions**: Module-specific boundary settings
- **Solver Functions**: Discretization schemes and numerical methods
- **Control Parameters**: Simulation time, timestep, and convergence
- **Terminal Output**: Real-time process monitoring

## Key Components

### UI Loading Infrastructure

#### UILoader (`gui/ui_loader.py`)
Provides runtime loading of Qt Designer .ui files using PyQt6's `uic.loadUi()` function.

**Key Features:**
- Dynamic .ui file loading at runtime
- Support for all interface types (main window, carbon, half-cell, full-cell, results)
- File existence checking and error handling
- Automatic path resolution

**Usage:**
```python
from gui.ui_loader import UILoader

# Load main window from .ui file
main_window = UILoader.load_main_window()

# Load carbon interface from .ui file
carbon_interface = UILoader.load_carbon_interface()

# Check if .ui file exists
if UILoader.ui_file_exists("mainwindow"):
    # Load the file
    widget = UILoader.load_ui_file("path/to/mainwindow.ui")
```

#### UIConfig (`gui/ui_config.py`)
Manages UI loading configuration and provides multiple configuration sources.

**Loading Modes:**
- `UI_FILES`: Force loading from .ui files
- `HAND_CODED`: Force hand-coded widgets
- `AUTO_DETECT`: Auto-detect based on file availability

**Configuration Sources:**
1. **Environment Variables**: `BATTERY_SIM_UI_MODE`, `BATTERY_SIM_UI_PATH`
2. **Command Line Arguments**: `--ui-mode`, `--ui-path`, `--no-fallback`
3. **Default Settings**: Auto-detect with fallback enabled

**Usage:**
```python
from gui.ui_config import UIConfig, UILoadingMode

# Create default configuration
config = UIConfig()

# Configure from environment
config = UIConfig.from_environment()

# Configure from command line
config = UIConfig.from_command_line(args)

# Set specific mode
config.set_mode(UILoadingMode.UI_FILES)
config.set_fallback_enabled(False)
```

#### InterfaceFactory (`gui/interface_factory.py`)
Factory pattern implementation for creating interfaces with automatic fallback.

**Features:**
- Automatic .ui file detection and loading
- Seamless fallback to hand-coded widgets
- Support for all interface types
- Error handling and logging

**Usage:**
```python
from gui.interface_factory import InterfaceFactory
from gui.ui_config import UIConfig

config = UIConfig()
config.set_mode(UILoadingMode.AUTO_DETECT)

# Create interface with automatic .ui loading and fallback
interface = InterfaceFactory.create_interface("carbon", parent, config)
```

### Core Application (`core/application.py`)

- Main application window logic
- Project creation and opening
- Interface navigation
- Signal/slot management
- UI configuration integration

### Process Control (`openfoam/process_controller.py`)

- Subprocess management with `subprocess.Popen`
- Real-time output streaming
- Process start/stop/pause functionality
- Thread-safe output handling

### File Management (`utils/file_operations.py`)

- Template-based project creation
- File copying and modification
- Parameter substitution
- Backup/restore functionality

### Parameter Management (`utils/parameter_parser.py`)

- Parsing OpenFOAM configuration files
- Geometry parameters (blockMeshDict, topoSetDict)
- Material properties (LiProperties)
- Solver settings (fvSchemes, fvSolution)
- Control parameters (controlDict)

## Migration Notes

### From C++ to Python

1. **GUI Framework**: PyQt6/PySide6 replaces Qt C++
2. **Process Control**: `subprocess.Popen` replaces `QProcess`
3. **File Operations**: Python `pathlib`/`shutil` replaces C++ file I/O
4. **Parameter Parsing**: Regular expressions replace C++ parsing

### Preserved Functionality

- All three simulation modules (SPM, Half Cell, Full Cell)
- Template-based project creation
- Real-time OpenFOAM solver execution
- Parameter management and validation
- File operations and template system
- Process control and monitoring

### UI Loading Strategy

The Python implementation supports both .ui file loading and hand-coded widgets:

**Advantages of .ui File Loading:**
- 100% UI compatibility with original C++ version
- Visual design support with Qt Designer
- Easier UI maintenance and updates
- Better separation of UI design and business logic

**Advantages of Hand-Coded Widgets:**
- No dependency on .ui files
- Better performance (no runtime loading)
- Easier to debug and modify
- Full Python code control

**Fallback Strategy:**
- Try .ui file loading first (if configured)
- Automatically fall back to hand-coded widgets if .ui loading fails
- User can disable fallback for strict .ui file requirement
- Graceful error handling and user feedback

## OpenFOAM Integration

The Python implementation maintains full compatibility with OpenFOAM solvers:

- **Solver Building**: `wclean` and `wmake` commands
- **Simulation Execution**: Direct solver invocation
- **Process Monitoring**: Real-time output streaming
- **Error Handling**: Comprehensive error reporting

### Windows Compatibility

- Supports Windows-installed OpenFOAM
- Path conversion utilities
- Environment variable management
- Cross-platform process execution

## Development

### Adding New Simulation Modules

1. Create interface class inheriting from `BaseInterface`
2. Add module to `SUPPORTED_MODULES` in `constants.py`
3. Create template directory in `resources/templates/`
4. Add .ui file to `resources/ui/`
5. Update interface factory as needed

### Testing UI Loading

Use the test script to verify UI loading functionality:

```bash
python src_py/test_ui_loading.py
```

This tests:
- .ui file existence and loading
- UI configuration from different sources
- Interface factory functionality
- Fallback mechanisms

## Dependencies

### Required

- PyQt6 >= 6.5.2 (or PySide6)
- pyqtgraph >= 0.13.4 (for plotting)

### Optional

- matplotlib >= 3.7.2 (alternative plotting)
- pytest >= 7.4.3 (testing)
- black >= 23.7.0 (code formatting)
- mypy >= 1.5.1 (type checking)

## Future Enhancements

### Phase 4+ Implementation

The following components are planned for future implementation:

- **Complete GUI Interfaces**: Full implementation of all simulation interfaces
- **Results Visualization**: Advanced plotting and data analysis
- **Testing Framework**: Comprehensive test suite
- **Documentation**: API documentation and user guides
- **Deployment**: Packaging and distribution

## Troubleshooting

### Common Issues

1. **OpenFOAM Not Found**: Ensure OpenFOAM is in PATH
2. **Python Dependencies**: Install all requirements
3. **Permissions**: Ensure write access to project directories
4. **Template Files**: Copy templates from C++ version
5. **.ui File Loading**: Check file paths and PyQt6 installation

### Debug Mode

Enable debug output by setting environment variable:
```bash
export DEBUG=1
python src_py/main.py
```

### UI Loading Issues

If .ui files fail to load:

1. **Check PyQt6 Installation**: Ensure PyQt6 is properly installed
2. **Verify .ui Files**: Check that .ui files exist in `resources/ui/`
3. **File Permissions**: Ensure .ui files are readable
4. **Qt Version**: Check compatibility between .ui files and PyQt6 version
5. **Fallback**: Use `--ui-mode hand_coded` to use hand-coded widgets

## Contributing

1. Follow Python PEP 8 style guidelines
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure compatibility with existing C++ version
5. Test both .ui file and hand-coded widget modes

## License

This implementation maintains the same GPLv3 license as the original C++ version.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the original C++ implementation
3. Consult OpenFOAM documentation
4. Report bugs with detailed error messages
5. Include UI loading mode and configuration details
