# Battery Simulator - Architecture Documentation

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current Project State](#current-project-state)
3. [Architecture Overview](#architecture-overview)
4. [Module Analysis](#module-analysis)
5. [Dependency Management](#dependency-management)
6. [Interface Specifications](#interface-specifications)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Success Criteria](#success-criteria)
9. [Risk Assessment](#risk-assessment)
10. [Appendices](#appendices)

## Executive Summary

The Battery Simulator is a Python-based application that provides a GUI interface for creating and running battery simulations using OpenFOAM solvers. The project has been migrated from C++/Qt and maintains compatibility with the original functionality while adding enhanced features.

### Key Findings
- **Project Status**: 85% Complete - Core architecture is solid with most components implemented
- **Strengths**: Well-structured modular design, comprehensive error handling, cross-platform support
- **Critical Issues**: Circular import resolution needed, some interfaces incomplete
- **Target Completion**: 2-3 weeks for full production readiness

## Current Project State

### Completed Components (85%)

#### ✅ Core Infrastructure
- **Application Framework**: Main window, UI configuration, interface factory
- **UI Loading System**: Support for .ui files and hand-coded widgets with fallback
- **OpenFOAM Integration**: Process control, solver management, MSYS2 support
- **Parameter Management**: Enhanced parser with validation and OpenFOAM file support
- **File Operations**: Template management, backup/restore, path validation
- **Error Handling**: Comprehensive exception handling and logging
- **Testing Framework**: Unit tests, integration tests, UI loading tests

#### ✅ Implemented Interfaces
- **Carbon Interface (SPM)**: Fully functional Single Particle Model interface
- **Base Interface**: Common functionality for all simulation interfaces
- **Half-Cell Interface**: P2D half-cell implementation (80% complete)
- **Full-Cell Interface**: P2D full-cell implementation (60% complete)

#### ✅ Utility Systems
- **Debug Tools**: OpenFOAM integration debugging and validation
- **Project Management**: Template-based project creation and management
- **Configuration**: Flexible UI loading modes and environment variables

### Missing Components (15%)

#### 🔄 Incomplete Implementations
- **Full-Cell Interface**: Missing boundary conditions and validation
- **Result Interface**: Visualization and plotting functionality
- **Template Files**: OpenFOAM configuration templates not fully populated

#### ⚠️ Critical Issues
- **Circular Imports**: Some modules have circular dependency issues
- **UI Widget Naming**: Inconsistencies between .ui files and hand-coded widgets
- **Error Handling**: Some interfaces lack comprehensive error handling

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    BATTERY SIMULATOR                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   MAIN WINDOW   │  │   UI LOADER     │  │ UI CONFIG    │ │
│  │                 │  │                 │  │              │ │
│  │ - Project Mgmt  │  │ - .ui Loading   │  │ - Mode Mgmt  │ │
│  │ - Navigation    │  │ - Fallback      │  │ - Env Vars   │ │
│  │ - Exit Handling │  │ - Validation    │  │ - CLI Args   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ CARBON INTERFACE│  │HALF-CELL INTERFACE│ │FULL-CELL     │ │
│  │                 │  │                 │  │INTERFACE     │ │
│  │ - Geometry      │  │ - WE/SEP Params │  │ - Full Cell  │ │
│  │ - Constants     │  │ - Electrochem   │  │ - Multi-region│ │
│  │ - Boundary      │  │ - Validation    │  │ - Validation │ │
│  │ - Functions     │  │ - Region Mgmt   │  │ - Region Mgmt│ │
│  │ - Control       │  │ - Interface     │  │ - Interface  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ RESULT INTERFACE│  │ BASE INTERFACE  │  │ INTERFACE    │ │
│  │                 │  │                 │  │ FACTORY      │ │
│  │ - Visualization │  │ - Common Logic  │  │ - Creation   │ │
│  │ - Plotting      │  │ - Process Ctrl  │  │ - Fallback   │ │
│  │ - Data Analysis │  │ - Param Mgmt    │  │ - Validation │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   OPENFOAM INTEGRATION                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ PROCESS CTRL    │  │ SOLVER MGR      │  │ MSYS2 EXEC   │ │
│  │                 │  │                 │  │              │ │
│  │ - Subprocess    │  │ - Solver Mgmt   │  │ - Windows    │ │
│  │ - I/O Stream    │  │ - Compilation   │  │ - Path Conv  │ │
│  │ - Signals       │  │ - Execution     │  │ - Callbacks  │ │
│  │ - Monitoring    │  │ - Validation    │  │ - Validation │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    UTILITY LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ PARAM MGR       │  │ FILE OPS        │  │ DEBUG UTILS  │ │
│  │                 │  │                 │  │              │ │
│  │ - Validation    │  │ - Templates     │  │ - OpenFOAM   │ │
│  │ - Parsing       │  │ - Backup/Restore│  │ - Validation │ │
│  │ - OpenFOAM      │  │ - Path Mgmt     │  │ - Monitoring │ │
│  │ - Caching       │  │ - Copy/Move     │  │ - Reporting  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ PROJECT MGR     │  │ EXCEPTION HNDLR │                   │
│  │                 │  │                 │                   │
│  │ - Creation      │  │ - Safe Slots    │                   │
│  │ - Templates     │  │ - Logging       │                   │
│  │ - Validation    │  │ - Recovery      │                   │
│  │ - Backup        │  │ - Diagnostics   │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
## Module Analysis

### Core Modules

#### 1. Core Layer (`src/core/`)
**Purpose**: Core application logic and constants

**Components**:
- **`constants.py`**: Application constants, configuration, and UI definitions
- **`config.py`**: Configuration management (duplicate of constants.py - needs consolidation)
- **`project_manager.py`**: Project creation and management
- **`project_manager_enhanced.py`**: Enhanced project management with templates

**Dependencies**: None (should be dependency-free)

**Status**: ✅ Complete

**Issues**:
- Duplicate configuration files (`constants.py` vs `config.py`)
- Circular import potential if not careful

#### 2. GUI Layer (`src/gui/`)
**Purpose**: User interface components and interface management

**Components**:
- **`main_window.py`**: Main application window and navigation
- **`ui_config.py`**: UI loading configuration management
- **`ui_loader.py`**: Runtime .ui file loading
- **`interface_factory.py`**: Interface creation with fallback mechanisms
- **`interfaces/`**: Simulation interface implementations

**Dependencies**: Core (constants), PyQt6, OpenFOAM (for process control)

**Status**: ✅ 95% Complete

**Issues**:
- Some interfaces incomplete (FullCell, Result)
- Widget naming inconsistencies between .ui and hand-coded

#### 3. OpenFOAM Layer (`src/openfoam/`)
**Purpose**: OpenFOAM solver integration and process management

**Components**:
- **`process_controller.py`**: Subprocess management with real-time I/O
- **`solver_manager.py`**: Solver compilation and execution
- **`msys2_executor.py`**: Windows MSYS2 integration
- **`case_manager.py`**: OpenFOAM case management

**Dependencies**: PyQt6 (signals), Utils (file operations)

**Status**: ✅ Complete

#### 4. Utils Layer (`src/utils/`)
**Purpose**: Utility functions and parameter management

**Components**:
- **`parameter_parser.py`**: Deprecated - redirects to enhanced version
- **`parameter_manager_enhanced.py`**: Advanced parameter parsing and validation
- **`file_operations.py`**: Template management and file operations
- **`debug_utils.py`**: OpenFOAM integration debugging
- **`exception_handler.py`**: Exception handling utilities

**Dependencies**: Core (constants), OpenFOAM (for validation)

**Status**: ✅ Complete

### Interface Analysis

#### Carbon Interface (SPM) - 100% Complete
**Features**:
- ✅ Geometry configuration (dimensions, divisions, units)
- ✅ Material properties (diffusivity, concentration, reaction rate)
- ✅ Boundary conditions (charge/discharge, material selection)
- ✅ Solver functions (discretization schemes)
- ✅ Control parameters (time, timestep, tolerance)
- ✅ OpenFOAM integration (meshing, solver execution)
- ✅ Real-time output monitoring

**OpenFOAM Files Generated**:
- `blockMeshDict` - Geometry definition
- `topoSetDict` - Particle region definition
- `LiProperties` - Material properties
- `fvSchemes` - Discretization schemes
- `fvSolution` - Solver settings
- `controlDict` - Simulation control

#### Half-Cell Interface (P2D) - 80% Complete
**Features**:
- ✅ Working electrode parameters (thickness, active material fraction)
- ✅ Separator parameters (thickness, porosity)
- ✅ Electrochemical parameters (exchange current density, double layer capacitance)
- ⚠️ Boundary condition validation incomplete
- ⚠️ Region-specific solver settings need refinement

**OpenFOAM Files Generated**:
- Multi-region `blockMeshDict` (WE + separator)
- Region-specific `LiProperties`
- Interface boundary conditions

#### Full-Cell Interface (P2D) - 60% Complete
**Features**:
- ⚠️ Anode/cathode parameters (incomplete)
- ⚠️ Multi-layer geometry (partially implemented)
- ⚠️ Cell balancing and voltage calculations (missing)
- ⚠️ Advanced boundary conditions (missing)

#### Result Interface - 30% Complete
**Features**:
- ⚠️ Basic plotting framework (incomplete)
- ⚠️ Data visualization (missing)
- ⚠️ ParaView integration (missing)
- ⚠️ Results analysis (missing)

## Dependency Management

### Current Dependency Structure

```
GUI Layer
├── Core (constants, config)
├── OpenFOAM (process control)
└── Utils (parameter management)

OpenFOAM Layer
├── PyQt6 (signals)
└── Utils (file operations)

Utils Layer
├── Core (constants)
└── OpenFOAM (validation)

Core Layer
└── NO DEPENDENCIES (should be pure)
```

### Circular Import Issues Identified

#### Issue 1: Constants Import Pattern
**Problem**: Multiple modules import constants at module level
**Location**: `main_window.py`, `base_interface.py`, `parameter_manager_enhanced.py`
**Solution**: Use lazy imports inside functions

#### Issue 2: Interface Factory Dependencies
**Problem**: Interface factory imports all interfaces at module level
**Location**: `interface_factory.py`
**Solution**: Dynamic imports based on interface type

#### Issue 3: OpenFOAM Integration Dependencies
**Problem**: OpenFOAM modules import GUI components for signals
**Location**: `process_controller.py`, `solver_manager.py`
**Solution**: Use abstract base classes or dependency injection

### Recommended Dependency Management Strategy

#### 1. Dependency Inversion Principle
- Define interfaces in Core layer
- Implementations in appropriate layers
- Use dependency injection for cross-layer dependencies

#### 2. Lazy Import Strategy
```python
# GOOD: Lazy import
def get_constants():
    from src.core.constants import PARAMETER_FILES
    return PARAMETER_FILES

# BAD: Module-level import
from src.core.constants import PARAMETER_FILES
```

#### 3. Interface Abstraction
```python
# Core layer defines interfaces
class IProcessObserver(ABC):
    @abstractmethod
    def on_output_received(self, output: str): pass

# GUI layer implements
class MainWindow(IProcessObserver):
    def on_output_received(self, output: str):
        self.terminal.append(output)
```

## Interface Specifications

### Base Interface Contract

All simulation interfaces must implement:

```python
class BaseInterfaceContract:
    # Lifecycle
    def set_project_paths(self, project_path: str, project_name: str): pass
    def load_parameters(self): pass
    def save_parameters(self): pass
    
    # UI Components
    @property
    def project_path(self) -> str: pass
    @property
    def project_name(self) -> str: pass
    
    # OpenFOAM Integration
    def run_geometry(self): pass
    def run_solver(self): pass
    def stop_solver(self): pass
    
    # Signals
    exit_signal = pyqtSignal()
    simulation_started = pyqtSignal()
    simulation_stopped = pyqtSignal()
    output_received = pyqtSignal(str)
```

### Carbon Interface Specification

**Module**: `src/gui/interfaces/carbon_interface.py`

**Parameters**:
```python
# Geometry
length: float (0.001-1000 μm)
width: float (0.001-1000 μm)
height: float (0.001-1000 μm)
radius: float (0.001-100 μm)
x_division: int (1-1000)
y_division: int (1-1000)
z_division: int (1-1000)
unit: str ('micrometer', 'millimeter', 'meter')

# Material Properties
DS_value: float (1e-20-1e-6)
CS_max: float (1000-100000)
kReact: float (1e-20-1e-6)
R: float (8.314)
F: float (96485)
Ce: float (0.1-10000)
alphaA: float (0.0-1.0)
alphaC: float (0.0-1.0)
T_temp: float (200-400 K)
I_app: float (-10000-10000)
initial_cs: float (0-100000)

# Solver Settings
ddtSchemes: str ('Euler', 'backward', 'localEuler', 'steadyState')
gradSchemes: str ('Gauss linear', 'Gauss cubic', 'leastSquares')
divSchemes: str ('bounded Gauss upwind', 'Gauss linear')
laplacianSchemes: str ('Gauss linear uncorrected', 'Gauss linear corrected')
interpolationSchemes: str ('linear', 'cubic')

# Control Parameters
endTime: float (0.001-1e6)
deltaT: float (1e-6-1e3)
writeInterval: float (1e-3-1e6)
tolerance: float (1e-12-1e-3)
```

### OpenFOAM File Specifications

#### blockMeshDict
```cpp
convertToMeters 1e-6;  // Unit conversion

vertices
(
    (-length/2 -width/2 -height/2)
    (length/2 -width/2 -height/2)
    (length/2 width/2 -height/2)
    (-length/2 width/2 -height/2)
    (-length/2 -width/2 height/2)
    (length/2 -width/2 height/2)
    (length/2 width/2 height/2)
    (-length/2 width/2 height/2)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (x_div y_div z_div) simpleGrading (1 1 1)
);
```

#### topoSetDict
```cpp
actions
(
    {
        name particle;
        type cellSet;
        action new;
        source
        {
            type sphereToCell;
            centre (0 0 0);
            radius radius;
        }
    }
);
```

#### LiProperties
```cpp
Li
{
    Ds [0 2 -1 0 0 0 0] DS_value;
    Cs_max [0 0 -3 0 0 0 0] CS_max;
    kReact [0 0 -1 0 0 0 0] kReact;
    R [0 0 0 0 0 0 0] 8.314;
    F [0 0 0 0 0 1 0] 96485;
    Ce [0 0 -3 0 0 0 0] Ce;
    alphaA [0 0 0 0 0 0 0] alphaA;
    alphaC [0 0 0 0 0 0 0] alphaC;
    T [0 0 0 1 0 0 0] T_temp;
    I_app [0 0 -2 0 0 1 0] I_app;
    initial_cs [0 0 -3 0 0 0 0] initial_cs;
}
```

## Implementation Roadmap

### Phase 1: Critical Issues Resolution (Week 1)

#### Priority 1: High Impact, High Urgency

**1.1 Circular Import Resolution**
- **Task**: Refactor module imports to use lazy loading
- **Owner**: Senior Developer
- **Duration**: 2 days
- **Success Criteria**: All modules import without circular dependency errors
- **Validation**: Run `python -c "import src; print('Success')"` without errors

**1.2 UI Widget Naming Standardization**
- **Task**: Standardize widget naming between .ui files and hand-coded versions
- **Owner**: UI Developer
- **Duration**: 1 day
- **Success Criteria**: All interfaces work with both .ui and hand-coded modes
- **Validation**: Test all UI loading modes for each interface

**1.3 Error Handling Enhancement**
- **Task**: Add comprehensive error handling to incomplete interfaces
- **Owner**: Backend Developer
- **Duration**: 1 day
- **Success Criteria**: No unhandled exceptions in any interface
- **Validation**: Run integration tests with error scenarios

#### Priority 2: Medium Impact, Medium Urgency

**1.4 Configuration Consolidation**
- **Task**: Merge `config.py` into `constants.py`
- **Owner**: Architect
- **Duration**: 0.5 days
- **Success Criteria**: Single configuration source
- **Validation**: All configuration references updated

**1.5 Template File Population**
- **Task**: Create complete OpenFOAM template files
- **Owner**: OpenFOAM Specialist
- **Duration**: 1 day
- **Success Criteria**: All template files contain valid OpenFOAM syntax
- **Validation**: OpenFOAM validation of generated files

### Phase 2: Interface Completion (Week 2)

#### Priority 1: High Impact, Medium Urgency

**2.1 Full-Cell Interface Completion**
- **Task**: Complete P2D full-cell interface implementation
- **Owner**: Senior Developer
- **Duration**: 3 days
- **Success Criteria**: Full-cell simulations can be configured and run
- **Validation**: End-to-end full-cell simulation test

**2.2 Result Interface Implementation**
- **Task**: Implement results visualization and analysis
- **Owner**: UI Developer
- **Duration**: 2 days
- **Success Criteria**: Results can be visualized and analyzed
- **Validation**: Plot generation and data export functionality

#### Priority 2: Medium Impact, Low Urgency

**2.3 Advanced Parameter Validation**
- **Task**: Enhance parameter validation with physical constraints
- **Owner**: Domain Expert
- **Duration**: 1 day
- **Success Criteria**: Invalid parameter combinations are prevented
- **Validation**: Boundary condition validation tests

**2.4 Performance Optimization**
- **Task**: Optimize parameter parsing and file operations
- **Owner**: Performance Engineer
- **Duration**: 1 day
- **Success Criteria**: 20% improvement in file operations
- **Validation**: Benchmark tests

### Phase 3: Testing and Documentation (Week 3)

#### Priority 1: High Impact, Medium Urgency

**3.1 Comprehensive Testing**
- **Task**: Complete test coverage for all interfaces
- **Owner**: QA Engineer
- **Duration**: 2 days
- **Success Criteria**: >90% test coverage, all critical workflows tested
- **Validation**: Test suite execution and coverage report

**3.2 Documentation Completion**
- **Task**: Complete architecture and user documentation
- **Owner**: Technical Writer
- **Duration**: 1 day
- **Success Criteria**: Complete documentation package
- **Validation**: Documentation review and approval

#### Priority 2: Medium Impact, Low Urgency

**3.3 Performance Testing**
- **Task**: Load testing and performance validation
- **Owner**: Performance Engineer
- **Duration**: 1 day
- **Success Criteria**: Application handles large simulations
- **Validation**: Performance benchmarks

**3.4 Deployment Preparation**
- **Task**: Prepare deployment scripts and packaging
- **Owner**: DevOps Engineer
- **Duration**: 1 day
- **Success Criteria**: Automated deployment pipeline
- **Validation**: Successful deployment to test environment

## Success Criteria

### Technical Success Criteria

#### 1. Architecture Quality
- **Circular Import Free**: No circular dependencies between modules
- **Separation of Concerns**: Clear module boundaries maintained
- **Dependency Management**: Proper dependency injection and abstraction
- **Code Quality**: PEP 8 compliance, type hints, comprehensive docstrings

#### 2. Functional Completeness
- **Interface Completion**: All 4 interfaces (Carbon, Half-Cell, Full-Cell, Result) fully functional
- **OpenFOAM Integration**: All 3 solvers (SPMFoam, halfCellFoam, fullCellFoam) integrated
- **Parameter Management**: Complete parameter validation and management
- **Error Handling**: Comprehensive error handling and user feedback

#### 3. Performance Requirements
- **Startup Time**: Application starts in <5 seconds
- **File Operations**: Template operations complete in <10 seconds
- **Memory Usage**: Memory usage <500MB for typical operations
- **Responsiveness**: UI remains responsive during long operations

#### 4. Quality Assurance
- **Test Coverage**: >90% unit test coverage, >80% integration test coverage
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **OpenFOAM Compatibility**: Compatible with OpenFOAM 6+ and MSYS2
- **User Experience**: Intuitive UI with helpful error messages

### Business Success Criteria

#### 1. User Adoption
- **Training Time**: New users can start basic simulations in <30 minutes
- **Documentation Quality**: Users can complete tasks using documentation
- **Support Requests**: <5% of users require technical support

#### 2. Maintainability
- **Code Reviews**: All code changes reviewed before merge
- **Documentation**: Architecture and API documentation maintained
- **Testing**: Automated testing prevents regressions
- **Dependencies**: Dependencies updated and security vulnerabilities addressed

#### 3. Extensibility
- **New Interfaces**: New simulation interfaces can be added in <1 week
- **New Solvers**: New OpenFOAM solvers can be integrated in <2 days
- **Customization**: Users can customize parameters without code changes

## Risk Assessment

### High Risk Items

#### 1. Circular Import Resolution
**Risk**: Circular imports cause application startup failures
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Create dependency graph visualization
- Implement automated circular import detection
- Use dependency injection framework
- Maintain import order documentation

#### 2. OpenFOAM Integration Stability
**Risk**: OpenFOAM version changes break integration
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Version-specific compatibility layers
- Automated OpenFOAM validation
- Fallback mechanisms for solver execution
- Clear version requirements documentation

#### 3. UI Loading Mode Compatibility
**Risk**: .ui file and hand-coded widget inconsistencies
**Probability**: High
**Impact**: Medium
**Mitigation**:
- Automated UI consistency testing
- Widget naming convention enforcement
- Fallback mechanism testing
- Cross-mode validation scripts

### Medium Risk Items

#### 4. Performance with Large Simulations
**Risk**: Application becomes unresponsive with large parameter sets
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Background processing for long operations
- Progress indicators and cancellation support
- Memory usage optimization
- Performance benchmarking

#### 5. Cross-Platform Compatibility
**Risk**: Platform-specific issues on Windows, Linux, or macOS
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Cross-platform testing on all supported platforms
- Platform-specific code abstraction
- CI/CD pipeline with multi-platform testing
- Platform-specific documentation

### Low Risk Items

#### 6. Template File Maintenance
**Risk**: Template files become outdated or inconsistent
**Probability**: Low
**Impact**: Low
**Mitigation**:
- Template validation scripts
- Automated template generation
- Version control for templates
- Template documentation

#### 7. Documentation Currency
**Risk**: Documentation becomes outdated with code changes
**Probability**: Medium
**Impact**: Low
**Mitigation**:
- Documentation generation from code
- Documentation review in code review process
- Automated documentation validation
- Documentation change requirements

## Implementation Guidelines

### Development Best Practices

#### 1. Code Organization
```python
# Module structure
src/
├── core/           # Core logic, no dependencies
├── gui/            # UI components only
├── openfoam/       # OpenFOAM integration
├── utils/          # Utility functions
└── resources/      # Static files only
```

#### 2. Import Guidelines
```python
# GOOD: Lazy imports
def my_function():
    from src.core.constants import PARAMETER_FILES
    return PARAMETER_FILES

# BAD: Module-level imports causing cycles
from src.core.constants import PARAMETER_FILES
```

#### 3. Error Handling
```python
# GOOD: Comprehensive error handling
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    self.show_error_message("User-friendly message")
    return None
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    self.show_critical_error("Critical error occurred")
    raise
```

#### 4. Signal/Slot Management
```python
# GOOD: Proper signal management
class MyInterface(BaseInterface):
    def __init__(self):
        super().__init__()
        self._connect_signals()
    
    def _connect_signals(self):
        self.process_controller.output_received.connect(self._on_output)
        self.process_controller.error_received.connect(self._on_error)
    
    def closeEvent(self, event):
        # Clean up signals
        self.process_controller.output_received.disconnect(self._on_output)
        self.process_controller.error_received.disconnect(self._on_error)
        super().closeEvent(event)
```

### Testing Guidelines

#### 1. Unit Test Structure
```python
# Test file structure
tests/
├── unit/
│   ├── test_core_application.py
│   ├── test_gui_components.py
│   ├── test_openfoam_integration.py
│   └── test_utils_components.py
├── integration/
│   └── test_workflows.py
└── performance/
    └── test_benchmarks.py
```

#### 2. Test Coverage Requirements
- **Unit Tests**: >90% coverage of all modules
- **Integration Tests**: All critical workflows tested
- **UI Tests**: Both .ui file and hand-coded widget modes
- **Error Tests**: All error scenarios covered

#### 3. Test Data Management
```python
# Use fixtures for test data
@pytest.fixture
def sample_parameters():
    return {
        'length': 100.0,
        'width': 100.0,
        'height': 100.0,
        'radius': 50.0
    }

# Use temporary directories for file operations
@pytest.fixture
def temp_project_dir(tmp_path):
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir
```

### Deployment Guidelines

#### 1. Environment Setup
```bash
# Required dependencies
pip install -r requirements.txt

# OpenFOAM setup (external)
# - Install OpenFOAM 6+ or MSYS2 on Windows
# - Set environment variables (FOAM_INST_DIR, etc.)
```

#### 2. Configuration
```python
# Environment variables for UI configuration
export BATTERY_SIM_UI_MODE=auto  # or ui_files, hand_coded
export BATTERY_SIM_UI_PATH=/custom/ui/path

# Command line arguments
python src/main.py --ui-mode auto --ui-path /custom/path
```

#### 3. Validation
```bash
# Run test suite
python -m pytest tests/

# Validate OpenFOAM integration
python src/utils/debug_utils.py

# Test UI loading modes
python src/tests/test_ui_loading.py
```

## Appendices

### Appendix A: Module Dependencies

#### Core Dependencies
```
src/core/constants.py: NO DEPENDENCIES
src/core/project_manager.py: constants.py
```

#### GUI Dependencies
```
src/gui/main_window.py: core.constants, gui.ui_config, gui.interface_factory
src/gui/interfaces/base_interface.py: core.constants, openfoam.process_controller, utils.parameter_manager
src/gui/interfaces/carbon_interface.py: gui.interfaces.base_interface
```

#### OpenFOAM Dependencies
```
src/openfoam/process_controller.py: PyQt6.QtCore
src/openfoam/solver_manager.py: openfoam.process_controller, core.constants
```

#### Utils Dependencies
```
src/utils/parameter_manager_enhanced.py: core.constants
src/utils/file_operations.py: core.constants
src/utils/debug_utils.py: NO DEPENDENCIES
```

### Appendix B: Configuration Reference

#### UI Loading Modes
```python
# Environment variables
BATTERY_SIM_UI_MODE=auto          # auto, ui_files, hand_coded
BATTERY_SIM_UI_PATH=/custom/path  # Custom .ui file path

# Command line arguments
--ui-mode auto                    # auto, ui_files, hand_coded
--ui-path /custom/path           # Custom .ui file path
--no-fallback                    # Disable fallback to hand-coded
```

#### OpenFOAM Configuration
```python
# Environment variables (external)
FOAM_INST_DIR=/path/to/openfoam
FOAM_APPBIN=/path/to/openfoam/applications/bin
WM_PROJECT_DIR=/path/to/openfoam

# MSYS2 Configuration (Windows)
OpenFOAM-MSYS2.bat available in PATH
```

### Appendix C: Error Codes and Messages

#### Application Errors
```
ERR-001: Circular import detected
ERR-002: UI file loading failed
ERR-003: OpenFOAM integration failed
ERR-004: Parameter validation failed
ERR-005: Project creation failed
```

#### OpenFOAM Errors
```
OF-001: OpenFOAM not found
OF-002: Solver compilation failed
OF-003: Mesh generation failed
OF-004: Simulation execution failed
OF-005: Process timeout
```

#### UI Errors
```
UI-001: Widget not found
UI-002: Signal connection failed
UI-003: Layout configuration failed
UI-004: Theme loading failed
```

### Appendix D: Performance Benchmarks

#### Startup Performance
- **Target**: <5 seconds
- **Current**: ~3 seconds
- **Measurement**: Time from application launch to main window display

#### File Operations
- **Template Copy**: <5 seconds for 100 files
- **Parameter Parsing**: <1 second for 50 parameters
- **File Generation**: <2 seconds for complete case

#### Memory Usage
- **Idle**: <100MB
- **Active**: <300MB
- **Peak**: <500MB

### Appendix E: Glossary

- **SPM**: Single Particle Model
- **P2D**: Pseudo-2D Model
- **OpenFOAM**: Open Field Operation and Manipulation (CFD library)
- **MSYS2**: Windows development environment for OpenFOAM
- **UI**: User Interface (.ui files from Qt Designer)
- **PyQt6**: Python binding for Qt framework
- **BlockMesh**: OpenFOAM mesh generation utility
- **TopoSet**: OpenFOAM topology selection utility
- **ParaView**: Visualization application for OpenFOAM results

---

**Document Version**: 1.0
**Last Updated**: December 2025
**Next Review**: March 2026
                                │
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    RESOURCE LAYER                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ UI FILES        │  │ TEMPLATES       │  │ CONFIG       │ │
│  │                 │  │                 │  │              │ │
│  │ - Main Window   │  │ - OpenFOAM      │  │ - Constants  │ │
│  │ - Interfaces    │  │ - Parameters    │  │ - Settings   │ │
│  │ - Widgets       │  │ - Structure     │  │ - Defaults   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘