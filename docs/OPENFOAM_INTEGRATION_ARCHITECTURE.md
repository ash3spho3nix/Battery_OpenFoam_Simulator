# OpenFOAM Integration Architecture Documentation

## Overview

This document describes the comprehensive OpenFOAM integration architecture for the Battery Simulator Python application. The integration provides robust process control, solver management, and case directory management with cross-platform support.

## Architecture Components

### 1. ProcessController

**Location**: `src/openfoam/process_controller.py`

The `ProcessController` class provides low-level process management for OpenFOAM operations.

#### Key Features

- **Cross-Platform Process Control**: Handles Windows vs Unix differences automatically
- **Real-time Output Streaming**: Non-blocking I/O with separate stdout/stderr handling
- **Process Lifecycle Management**: Start, stop, pause, resume operations
- **Progress Monitoring**: Built-in progress tracking for long-running operations
- **Thread Safety**: Proper thread synchronization for GUI integration

#### Architecture Design

```
ProcessController
├── subprocess.Popen Management
├── Thread-based I/O Monitoring
│   ├── stdout_reader_thread
│   ├── stderr_reader_thread
│   └── process_monitor_thread
├── Cross-Platform Signal Handling
│   ├── Windows: CTRL_BREAK_EVENT, CTRL_C_EVENT
│   └── Unix: SIGTERM, SIGSTOP, SIGCONT
├── Output Buffering & Parsing
└── Progress Tracking
```

#### Signals and Events

```python
# Process events
process_started = pyqtSignal()
process_finished = pyqtSignal(int)  # exit_code
process_stopped = pyqtSignal()

# Output events
output_received = pyqtSignal(str)
error_received = pyqtSignal(str)

# Progress events
progress_updated = pyqtSignal(float)  # 0.0 to 1.0
```

#### Usage Example

```python
from openfoam.process_controller import ProcessController

controller = ProcessController()

# Connect signals
controller.output_received.connect(self.handle_output)
controller.process_finished.connect(self.handle_completion)

# Start process with OpenFOAM mode
controller.start_process("blockMesh", working_dir="/path/to/case", openfoam_mode=True)

# Monitor progress
if controller.is_running():
    progress = controller.get_progress()
    
# Clean termination
controller.terminate_process()
```

### 2. OpenFOAMSolverManager

**Location**: `src/openfoam/solver_manager.py`

The `OpenFOAMSolverManager` class provides high-level solver management with OpenFOAM-specific features.

#### Key Features

- **OpenFOAM Environment Detection**: Automatic discovery of OpenFOAM installations
- **Solver Building**: wclean and wmake operations with progress monitoring
- **Simulation Execution**: Full simulation lifecycle management
- **Output Parsing**: OpenFOAM-specific output parsing for time and progress
- **Parallel Execution**: Support for MPI-based parallel simulations

#### Architecture Design

```
OpenFOAMSolverManager
├── OpenFOAM Environment Detection
│   ├── Environment Variables (WM_PROJECT_DIR)
│   ├── Filesystem Discovery
│   └── PATH-based Detection
├── Solver Management
│   ├── Build Operations (wclean, wmake)
│   ├── Executable Validation
│   └── Build Progress Tracking
├── Simulation Management
│   ├── Serial Execution
│   ├── Parallel Execution (MPI)
│   └── Parameter Parsing (controlDict)
├── Output Processing
│   ├── Time-based Progress
│   ├── Error Detection
│   └── Real-time Monitoring
└── Process Integration
    └── ProcessController Integration
```

#### OpenFOAM Environment Detection

The solver manager automatically detects OpenFOAM installations through multiple methods:

1. **Environment Variables**: Checks `WM_PROJECT_DIR`
2. **Filesystem Paths**: Searches common installation directories
3. **PATH Discovery**: Finds OpenFOAM executables in system PATH

```python
def _find_openfoam_installation(self) -> Optional[Dict[str, Any]]:
    """Find OpenFOAM installation on the system."""
    # Priority order:
    # 1. Environment variables
    # 2. Common filesystem paths
    # 3. PATH-based discovery
```

#### Solver Building Process

```python
def build_solver(self, force_rebuild: bool = False) -> bool:
    """Build OpenFOAM solver with progress monitoring."""
    # 1. Change to solver directory
    # 2. Execute wclean
    # 3. Execute wmake
    # 4. Verify build success
    # 5. Emit build_completed signal
```

#### Simulation Execution

```python
def run_simulation(self, case_path: str, parallel: bool = False, n_processors: int = 1) -> bool:
    """Run OpenFOAM simulation with monitoring."""
    # 1. Parse controlDict for parameters
    # 2. Build simulation command
    # 3. Start process with OpenFOAM mode
    # 4. Monitor progress and time
```

#### Usage Example

```python
from openfoam.solver_manager import OpenFOAMSolverManager

# Initialize solver manager
solver_manager = OpenFOAMSolverManager(
    project_path="/path/to/project",
    solver_name="SPMFoam_OF6"
)

# Build solver
if solver_manager.build_solver():
    print("Solver built successfully")
    
# Run simulation
case_path = "/path/to/case"
if solver_manager.run_simulation(case_path, parallel=True, n_processors=4):
    print("Simulation started")
    
# Monitor progress
@pyqtSlot(float)
def on_progress(progress):
    print(f"Simulation progress: {progress * 100:.1f}%")

solver_manager.simulation_progress.connect(on_progress)
```

### 3. OpenFOAMCaseManager

**Location**: `src/openfoam/case_manager.py`

The `OpenFOAMCaseManager` class handles OpenFOAM case directory setup and parameter management.

#### Key Features

- **Case Structure Management**: Create and validate OpenFOAM case directories
- **Parameter File Management**: Update OpenFOAM configuration files
- **Initial Conditions**: Set up field initial conditions
- **Backup/Restore**: Case backup and restoration capabilities
- **File Format Handling**: Proper OpenFOAM file format support

#### Case Directory Structure

```
case_directory/
├── 0/                          # Initial conditions
│   ├── C                       # Concentration field
│   ├── Cs                      # Surface concentration field
│   └── p                       # Pressure field
├── constant/                   # Constant properties
│   └── LiProperties           # Lithium material properties
└── system/                     # System configuration
    ├── blockMeshDict          # Mesh definition
    ├── topoSetDict            # Topological sets
    ├── controlDict            # Simulation control
    ├── fvSchemes              # Discretization schemes
    └── fvSolution             # Solver settings
```

#### Parameter Management

The case manager provides methods to update various OpenFOAM parameter files:

```python
# Geometry parameters
params = {
    'length': 100.0,
    'width': 50.0,
    'height': 25.0,
    'x_division': 40,
    'y_division': 20,
    'z_division': 10,
    'unit': 'micrometer',
    'radius': 10.0
}
case_manager.update_geometry_parameters(params)

# Material parameters
material_params = {
    'Ds_value': 1e-14,
    'CS_max': 30000,
    'kReact': 1e-11,
    'R': 8.314,
    'F': 96485,
    'Ce': 1000,
    'alphaA': 0.5,
    'alphaC': 0.5,
    'T_temp': 298.15,
    'I_app': 0.0
}
case_manager.update_material_parameters(material_params)

# Control parameters
control_params = {
    'endTime': 10.0,
    'deltaT': 0.1,
    'writeInterval': 1.0
}
case_manager.update_control_parameters(control_params)
```

#### Usage Example

```python
from openfoam.case_manager import OpenFOAMCaseManager

# Initialize case manager
case_manager = OpenFOAMCaseManager("/path/to/case")

# Create case structure
case_manager.create_case_structure()

# Set up parameters
geometry_params = {...}
case_manager.update_geometry_parameters(geometry_params)

material_params = {...}
case_manager.update_material_parameters(material_params)

# Set initial conditions
initial_conditions = {
    'C': 1.0,
    'Cs': 0.5,
    'p': 0.0
}
case_manager.setup_initial_conditions(initial_conditions)

# Validate case
if case_manager.validate_case_structure():
    print("Case structure is valid")
```

## Integration Architecture

### Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    Battery Simulator GUI                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    BaseInterface                            │
│  (src/gui/interfaces/base_interface.py)                     │
│                                                             │
│  - Integrates all OpenFOAM components                       │
│  - Provides unified interface to GUI                        │
│  - Manages project paths and configuration                  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│             │ │             │ │             │
│   Solver    │ │    Case     │ │   Process   │
│  Manager    │ │   Manager   │ │  Controller │
│             │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘
```

### Signal Flow Architecture

```
User Action → BaseInterface → OpenFOAM Components → Process Execution
     ↓              ↓               ↓                    ↓
  Button      Parameter      Solver/Case        subprocess.Popen
  Click       Validation     Operations           Management
     ↓              ↓               ↓                    ↓
  Signal      Update Files    Build/Setup        Real-time Output
  Emission    & Validation    Simulation         & Progress
     ↓              ↓               ↓                    ↓
  GUI Update ←  Status Info  ←  Results        ←   Process Events
```

## Cross-Platform Support

### Platform Detection

```python
import platform
platform_name = platform.system()  # 'Windows', 'Linux', 'Darwin'

if platform_name == "Windows":
    # Windows-specific handling
    shell = True  # Use shell for command interpretation
    signals = [signal.CTRL_BREAK_EVENT, signal.CTRL_C_EVENT]
else:
    # Unix-specific handling
    shell = False  # Avoid shell for better signal handling
    signals = [signal.SIGTERM, signal.SIGSTOP, signal.SIGCONT]
```

### Process Control Differences

#### Windows
- Uses `shell=True` for proper command interpretation
- Limited signal support (CTRL_C_EVENT, CTRL_BREAK_EVENT)
- Process termination via `terminate()` and `kill()`
- No pause/resume support (SIGSTOP/SIGCONT not available)

#### Unix (Linux/macOS)
- Uses `shell=False` for better signal handling
- Full signal support (SIGTERM, SIGSTOP, SIGCONT)
- Process group support for better control
- Pause/resume functionality available

### Path Handling

```python
from pathlib import Path

# Cross-platform path handling
case_path = Path("/path/to/case")
blockmesh_path = case_path / "system" / "blockMeshDict"

# Convert to string for subprocess
command = f"cd {case_path} && blockMesh"
```

## Error Handling Strategy

### Hierarchical Error Handling

1. **Process Level**: ProcessController handles subprocess errors
2. **Component Level**: Each manager handles domain-specific errors
3. **Application Level**: BaseInterface provides user-friendly error messages

### Error Types and Handling

#### Process Errors
```python
try:
    self.process_controller.start_process(command)
except Exception as e:
    self.error_occurred.emit(f"Process execution failed: {e}")
```

#### OpenFOAM Build Errors
```python
if exit_code != 0:
    error_msg = self._parse_build_errors()
    self.error_occurred.emit(f"Solver build failed: {error_msg}")
```

#### Parameter Validation Errors
```python
if not self._validate_parameters(params):
    raise ValueError("Invalid parameter values")
```

#### Case Structure Errors
```python
missing_files = self._check_required_files()
if missing_files:
    self.error_occurred.emit(f"Case structure invalid: {missing_files}")
```

## Performance Considerations

### Threading Strategy

- **I/O Threads**: Separate threads for stdout/stderr reading
- **Monitor Thread**: Dedicated thread for process monitoring
- **GUI Thread**: Main thread remains responsive
- **Thread Safety**: Proper locking for shared resources

### Memory Management

- **Buffer Limits**: Output buffers have size limits
- **Resource Cleanup**: Proper cleanup in `cleanup()` methods
- **Signal Disconnection**: Disconnect signals to prevent memory leaks

### Progress Optimization

- **Throttled Updates**: Progress updates limited to prevent flooding
- **Time-based Estimation**: Progress based on simulation time
- **Asynchronous Processing**: Non-blocking operations

## Testing Strategy

### Unit Tests

```python
class TestProcessController:
    """Test ProcessController functionality."""
    
    def test_start_process(self):
        """Test process startup."""
        # Mock subprocess.Popen
        # Verify signal emissions
        # Check process state
        
    def test_output_handling(self):
        """Test output stream handling."""
        # Mock process output
        # Verify signal emissions
        # Check buffer management
```

### Integration Tests

```python
class TestOpenFOAMIntegration:
    """Test full OpenFOAM workflow."""
    
    def test_full_workflow(self):
        """Test complete workflow."""
        # 1. Create case with CaseManager
        # 2. Build solver with SolverManager
        # 3. Run simulation
        # 4. Verify results
```

### Mocking Strategy

- **subprocess.Popen**: Mocked for controlled testing
- **File Operations**: Use temporary directories
- **OpenFOAM Commands**: Mock external commands
- **Signal Testing**: Verify signal emissions

## Best Practices

### 1. Error Handling

```python
# Always use try-except for I/O operations
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    self.error_occurred.emit(str(e))
    return False
```

### 2. Resource Management

```python
# Always clean up resources
def cleanup(self):
    self.process_controller.cleanup()
    # Disconnect signals
    # Close files
    # Clear buffers
```

### 3. Signal Usage

```python
# Use signals for loose coupling
self.simulation_started.connect(self.on_simulation_started)
self.simulation_progress.connect(self.update_progress_bar)

# Always disconnect in cleanup
def cleanup(self):
    self.simulation_started.disconnect(self.on_simulation_started)
    self.simulation_progress.disconnect(self.update_progress_bar)
```

### 4. Cross-Platform Code

```python
# Check platform when needed
if sys.platform == "win32":
    # Windows-specific code
    pass
else:
    # Unix-specific code
    pass
```

### 5. Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Operation started")
logger.warning("Potential issue detected")
logger.error("Operation failed", exc_info=True)
```

## Troubleshooting Guide

### Common Issues

#### 1. Process Not Starting
- **Cause**: Command syntax error or missing OpenFOAM environment
- **Solution**: Check command syntax and OpenFOAM installation

#### 2. No Output Received
- **Cause**: Buffering issues or thread problems
- **Solution**: Check thread status and buffer settings

#### 3. Build Failures
- **Cause**: Missing dependencies or incorrect paths
- **Solution**: Verify OpenFOAM installation and solver paths

#### 4. Cross-Platform Issues
- **Cause**: Platform-specific code not handled
- **Solution**: Add platform checks and appropriate handling

### Debugging Tips

1. **Enable Verbose Logging**: Set logging level to DEBUG
2. **Check Process Status**: Use `is_running()` and `get_exit_code()`
3. **Monitor Output Buffers**: Check `get_output_buffer()` and `get_error_buffer()`
4. **Verify File Paths**: Ensure all paths are correct and accessible
5. **Test Components Individually**: Test each component separately

## Future Enhancements

### Planned Features

1. **Enhanced Progress Parsing**: More sophisticated OpenFOAM output parsing
2. **Parallel Execution Optimization**: Better MPI integration
3. **Resource Monitoring**: CPU/memory usage monitoring
4. **Advanced Error Recovery**: Automatic retry mechanisms
5. **Performance Profiling**: Built-in performance analysis

### Extension Points

- **New Solver Types**: Easy addition of new solver types
- **Custom Output Parsers**: Pluggable output parsing system
- **Alternative Process Managers**: Support for alternative process control
- **Cloud Integration**: Remote execution support

## Conclusion

The OpenFOAM integration architecture provides a robust, cross-platform solution for managing OpenFOAM simulations in the Battery Simulator application. The modular design allows for easy maintenance and extension, while the comprehensive error handling and testing ensure reliability.

The architecture successfully addresses the key challenges of:
- Cross-platform process control
- Real-time output monitoring
- OpenFOAM-specific requirements
- GUI integration and responsiveness
- Error handling and recovery

This integration forms the backbone of the OpenFOAM simulation capabilities in the Battery Simulator, enabling users to perform complex battery simulations with a user-friendly interface.