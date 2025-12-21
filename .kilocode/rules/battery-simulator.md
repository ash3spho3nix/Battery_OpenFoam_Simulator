# Battery Simulator Project Rules

## Project Context

This is a Python implementation of a Battery Simulator application, migrated from C++/Qt. The application provides a GUI interface for creating and running battery simulations using OpenFOAM solvers.

## CRITICAL: Known Interface & Connection Issues (Priority Fixes)

### Issue #1: Signal-Slot Connection Missing (CRITICAL)
**Problem**: Interfaces don't emit `exit_signal` to return to MainWindow
**Fix Requirements**:
- All interfaces MUST emit `exit_signal` when exit button is clicked
- MainWindow MUST connect to `exit_signal` before showing interface
- Test: Click interface exit button → MainWindow should appear

**Implementation Pattern**:
```python
# In interface (BaseInterface or child):
class BaseInterface(QWidget):
    exit_signal = pyqtSignal()
    
    def _on_exit_button_clicked(self):
        self.exit_signal.emit()
        self.close()

# In MainWindow._open_interface():
self.current_interface.exit_signal.connect(self._on_interface_exit)
```

### Issue #2: Project Path Not Passed to Interfaces (CRITICAL)
**Problem**: Interfaces created without project context
**Fix Requirements**:
- MainWindow MUST call `interface.set_project_paths()` after creation
- Pass: project_path, project_name before showing interface
- Interfaces MUST NOT show() until paths are set

**Implementation Pattern**:
```python
# In MainWindow._open_interface():
interface = InterfaceFactory.create_interface(...)
interface.set_project_paths(project_path, project_name)
interface.exit_signal.connect(self._on_interface_exit)
interface.show()
self.hide()
```

### Issue #3: Interface Initialization Incomplete (CRITICAL)
**Problem**: `set_project_paths()` never called, paths remain None
**Fix Requirements**:
- ALWAYS call `set_project_paths()` after interface creation
- Initialize `solver_manager` and `parameter_manager` in `set_project_paths()`
- Validate paths exist before proceeding
- Show error if paths invalid

### Issue #4: Widget Naming Mismatch (HIGH PRIORITY)
**Problem**: .ui files use `length_lineEdit`, Python expects `length_edit`
**Fix Requirements**:
- Choose ONE naming convention (recommend: .ui file names)
- Update ALL Python code to match .ui widget names
- Use `_get_widget_value()` helper that tries both conventions
- Document the naming standard

**Standard Naming Convention**:
```python
# .ui file widgets (use these):
self.length_lineEdit
self.width_lineEdit
self.unit_select_box
self.carbon_radioButton

# Helper for backward compatibility:
def _get_widget_value(self, base_name):
    """Try multiple naming conventions"""
    variants = [f"{base_name}_lineEdit", f"{base_name}_edit", 
                f"{base_name}_spinBox", f"{base_name}_doubleSpinBox"]
    for variant in variants:
        if hasattr(self, variant):
            widget = getattr(self, variant)
            if hasattr(widget, 'text'):
                return float(widget.text())
            elif hasattr(widget, 'value'):
                return float(widget.value())
    raise AttributeError(f"No widget found for {base_name}")
```

### Issue #5: ProcessController Not Connected (HIGH PRIORITY)
**Problem**: ProcessController exists but not wired to simulation execution
**Fix Requirements**:
- Connect `run_button` → `_start_simulation()` → `process_controller.start_process()`
- Connect process signals to UI updates
- Implement pause/resume through process_controller
- Handle process termination properly

### Issue #6: Parameter Manager Initialization (HIGH PRIORITY)
**Problem**: `parameter_manager = None` and never initialized
**Fix Requirements**:
- Initialize in `set_project_paths()` with project path
- Validate parameter_manager before use
- Show error if initialization fails

**Implementation**:
```python
def set_project_paths(self, project_path: str, project_name: str):
    self.project_path = project_path
    self.project_name = project_name
    self.case_path = os.path.join(project_path, "Case")
    self.solver_path = project_path
    
    # Initialize managers
    try:
        self.parameter_manager = ParameterManager(self.case_path)
        self.solver_manager = OpenFOAMSolverManager(self.solver_path, self._get_solver_name())
    except Exception as e:
        logger.error(f"Failed to initialize managers: {e}")
        QMessageBox.critical(self, "Error", f"Failed to initialize: {e}")
        return False
    return True
```

### Issue #7: InterfaceFactory Loses Context (MEDIUM)
**Problem**: Interface created without parent relationship to MainWindow
**Fix Requirements**:
- Pass parent widget to interface constructor
- Maintain parent-child relationship
- Access parent's project_path/project_name if needed

### Issue #8: UI Mode Validation Too Strict (MEDIUM)
**Problem**: Code enforces UI_FILES only but widgets have naming mismatches
**Fix Requirements**:
- Either: Fix all widget names to match .ui files
- Or: Remove strict mode validation and support both
- Recommend: Fix widget names, keep validation

### Issue #9: ProjectManager Never Initialized (MEDIUM)
**Problem**: `self.project_manager = None` in MainWindow
**Fix Requirements**:
- Import and initialize ProjectManager in MainWindow.__init__()
- Use it in `_on_next_button_clicked()`
- Handle project creation failures

**Implementation**:
```python
# In MainWindow.__init__():
from src.core.project_manager import ProjectManager
self.project_manager = ProjectManager()

# In _create_project():
success = self.project_manager.create_project(
    project_name=project_name,
    template_name=module_type,
    project_path=str(project_full_path.parent)
)
if not success:
    raise Exception("Project creation failed")
```

### Issue #10: Error Propagation Incomplete (LOW)
**Problem**: Errors handled locally but not propagated to parent
**Fix Requirements**:
- Define error signals in interfaces
- Connect error signals to MainWindow handlers
- Show error dialogs and log appropriately
- Return error status from critical operations

## Critical Architecture Principles

### 1. Circular Import Prevention

**ALWAYS avoid circular imports:**
- Use lazy imports (import inside functions) when needed
- Import from `src.core.constants` only inside functions
- Use `TYPE_CHECKING` for type hints
- Never import at module level if it creates a cycle

Example:
```python
# Good - Lazy import
def get_parameter_file(file_type: str) -> str:
    from src.core.constants import PARAMETER_FILES
    return PARAMETER_FILES[file_type]

# Bad - Module-level import causing circular dependency
from src.core.constants import PARAMETER_FILES
```

### 2. UI Loading System

The application supports three UI loading modes:

1. **AUTO_DETECT (default)**: Try .ui files, fallback to hand-coded
2. **UI_FILES**: Force .ui file loading
3. **HAND_CODED**: Force hand-coded widgets

**Rules:**
- ALWAYS implement both .ui and hand-coded widget support
- ALWAYS handle .ui loading failures gracefully
- ALWAYS log UI loading decisions
- Test both loading paths
- **CRITICAL**: Ensure widget naming consistency between .ui and Python

### 3. Interface Lifecycle Management (CRITICAL)

**Mandatory Sequence**:
```python
# 1. Create interface
interface = InterfaceFactory.create_interface(type, parent, ui_config)

# 2. Set project paths (REQUIRED before show())
success = interface.set_project_paths(project_path, project_name)
if not success:
    # Handle error
    return

# 3. Connect signals (REQUIRED before show())
interface.exit_signal.connect(self._on_interface_exit)
interface.error_signal.connect(self._on_interface_error)

# 4. Show interface
interface.show()
self.hide()
```

### 4. PyQt6 Signal/Slot Connections

**Best Practices:**
- Use new-style signals (`signal.connect(slot)`)
- Always disconnect signals in cleanup
- Avoid circular signal connections
- Use `lambda` carefully with proper closures
- Document all signal/slot connections
- **CRITICAL**: Connect signals BEFORE calling show()

Example:
```python
# Good
self.button.clicked.connect(self.on_button_clicked)

# Clean up
def closeEvent(self, event):
    self.button.clicked.disconnect(self.on_button_clicked)
    super().closeEvent(event)
```

### 5. OpenFOAM Integration

**Requirements:**
- Use `subprocess.Popen` for process management
- Implement non-blocking I/O
- Parse stdout/stderr separately
- Handle process termination gracefully
- Support cross-platform execution (Windows with MSYS2/Cygwin)

**Windows-Specific**:
- Use MSYS2 or Cygwin bash for OpenFOAM commands
- Convert Windows paths to Unix format
- Source OpenFOAM environment in each command
- Handle path separators correctly

### 6. Widget Access Pattern (CRITICAL)

**Always use the flexible getter pattern**:
```python
def _get_widget(self, base_name: str, widget_type: str = 'lineEdit'):
    """
    Get widget trying multiple naming conventions.
    
    Args:
        base_name: Base name like 'length', 'width'
        widget_type: Widget type like 'lineEdit', 'spinBox'
    """
    # Try .ui convention first
    ui_name = f"{base_name}_{widget_type}"
    if hasattr(self, ui_name):
        return getattr(self, ui_name)
    
    # Try hand-coded convention
    code_name = f"{base_name}_edit" if widget_type == 'lineEdit' else f"{base_name}_spin"
    if hasattr(self, code_name):
        return getattr(self, code_name)
    
    raise AttributeError(f"Widget not found: {base_name}")

def _get_widget_value(self, base_name: str, default=None):
    """Get value from widget with fallback."""
    try:
        widget = self._get_widget(base_name)
        if hasattr(widget, 'text'):
            return widget.text()
        elif hasattr(widget, 'value'):
            return widget.value()
    except AttributeError:
        logger.warning(f"Widget {base_name} not found, using default")
        return default
```

## Code Style

### Python Style
- Follow PEP 8
- Use type hints everywhere
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all public functions/classes

### PyQt6 Style
- Use Qt naming conventions for UI elements (follow .ui files)
- Prefix slots with `on_` or `_on_` for private slots
- Use Qt Designer for complex UIs
- Keep business logic separate from UI

## File Organization

```
src/
├── core/           # Core application logic (avoid circular imports!)
├── gui/            # GUI components and interfaces
├── openfoam/       # OpenFOAM integration
├── utils/          # Utility functions (no constants imports at module level)
└── resources/      # Static resources (templates, UI files)
```

## Error Handling (Updated)

**Always:**
- Use try-except for all I/O operations
- Log errors with context
- Provide user-friendly error messages
- **Propagate errors to parent components**
- **Return status from critical operations**
- Implement recovery mechanisms
- Never let exceptions crash the GUI

Example:
```python
def set_project_paths(self, project_path: str, project_name: str) -> bool:
    """Set project paths. Returns False on failure."""
    try:
        self.project_path = project_path
        # ... initialization ...
        self.parameter_manager = ParameterManager(self.case_path)
        return True
    except Exception as e:
        logger.error(f"Failed to set project paths: {e}", exc_info=True)
        self.error_signal.emit(f"Initialization failed: {e}")
        return False
```

## Testing Requirements

### Critical Tests (Must Pass)
1. **Interface Navigation**: MainWindow → Interface → MainWindow
2. **Project Path Passing**: Validate paths set correctly
3. **Widget Access**: All widgets accessible by name
4. **Signal Connections**: All signals connected properly
5. **Manager Initialization**: parameter_manager, solver_manager not None

### Coverage Targets
- Unit tests: >90% coverage
- Integration tests: All critical workflows
- UI tests: Both loading modes

### Test Organization
```
tests/
├── unit/           # Unit tests by module
├── integration/    # Workflow tests
│   ├── test_interface_navigation.py  # NEW: Test navigation
│   ├── test_project_creation.py      # NEW: Test project setup
│   └── test_simulation_workflow.py   # NEW: End-to-end
└── conftest.py     # Shared fixtures
```

## Validation Checklist (Before Commit)

- [ ] All interfaces can navigate back to MainWindow
- [ ] Project paths passed to interfaces correctly
- [ ] All widget names consistent (prefer .ui names)
- [ ] parameter_manager initialized before use
- [ ] solver_manager initialized before use
- [ ] project_manager initialized in MainWindow
- [ ] All signals connected before show()
- [ ] Error handling returns status codes
- [ ] Tests pass for navigation workflow
- [ ] No circular imports detected

## OpenFOAM Configuration Files

When modifying OpenFOAM files, preserve:
- File format and structure
- Comments and documentation
- Indentation style
- Dictionary nesting

**Common files:**
- `blockMeshDict` - Geometry definition
- `topoSetDict` - Region definitions
- `LiProperties` - Material properties
- `fvSchemes` - Discretization schemes
- `fvSolution` - Solver settings
- `controlDict` - Simulation control

## Cross-Platform Compatibility

**Always consider:**
- Windows (MSYS2/Cygwin for OpenFOAM)
- Linux (native OpenFOAM)
- macOS (OpenFOAM via Docker/native)
- Path separators (use `pathlib`)
- Process execution differences
- File permissions
- Line endings

## Dependencies

**Required:**
- Python 3.8+
- PyQt6 >= 6.5.2
- OpenFOAM (external, platform-specific)
- MSYS2 or Cygwin (Windows only)

**Optional:**
- pyqtgraph (plotting)
- matplotlib (alternative plotting)
- pytest (testing)

## Git Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix (reference issue number)
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Test additions
- `chore:` Maintenance

Example: `fix: connect exit_signal in all interfaces (#1)`

## Performance Considerations

**Guidelines:**
- Use QThread for long operations
- Don't block the GUI thread
- Implement progress indicators
- Cache expensive computations
- Profile before optimizing

## Security

**Considerations:**
- Validate all file paths
- Sanitize user inputs
- Don't execute arbitrary code
- Use secure subprocess execution
- Log security-relevant events

## Documentation

**Requirements:**
- Docstrings for all public APIs
- README for each module
- Architecture documentation
- User guides
- Troubleshooting guides

## Common Pitfalls to Avoid

1. **Circular imports** - Use lazy imports
2. **Missing signal connections** - Connect before show()
3. **Uninitialized managers** - Initialize in set_project_paths()
4. **Widget name mismatches** - Follow .ui file naming
5. **Blocking GUI** - Use QThread
6. **Memory leaks** - Disconnect signals, clean up properly
7. **Hard-coded paths** - Use pathlib and configuration
8. **Platform-specific code** - Abstract with utility functions
9. **Missing error handling** - Always use try-except for I/O
10. **Poor UI responsiveness** - Keep operations non-blocking
11. **Showing interface before initialization** - Set paths first!

## Development Workflow

1. **Analysis Phase**: Understand requirements, design architecture
2. **Implementation Phase**: Write code following these rules
3. **Testing Phase**: Write tests, achieve coverage targets
4. **Validation Phase**: Run validation checklist
5. **Review Phase**: Code review, refactoring
6. **Documentation Phase**: Update docs, write guides

## Debugging Tips

### Circular Import Issues
```bash
# Visualize import graph
python -c "import src; print(src.__file__)"
# Check for circular dependencies
```

### Interface Navigation Issues
- Check if `exit_signal` is defined in interface
- Verify signal connection in MainWindow
- Test signal emission in interface
- Check if interface closes properly

### Widget Access Issues
- Use `_get_widget()` helper method
- Check .ui file for actual widget names
- Use diagnostic method to list all widgets
- Test both naming conventions

### UI Loading Issues
- Check .ui file paths
- Verify PyQt6 installation
- Test fallback mechanism
- Check console logs

### OpenFOAM Issues
- Verify installation: `which icoFoam` (Linux) or check MSYS2 (Windows)
- Check environment: `echo $WM_PROJECT_DIR`
- Test solver manually
- Check case directory structure
- Validate paths are set before operations

## Support Resources

- Project README: Comprehensive overview
- ARCHITECTURE.md: System design
- GitHub Issues: Report bugs
- Documentation: User guides

## Versioning

Follow Semantic Versioning (SemVer):
- MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

## License

This project uses GPLv3 license. All contributions must be compatible.

## Contact

For questions or issues, refer to project documentation or create a GitHub issue.
