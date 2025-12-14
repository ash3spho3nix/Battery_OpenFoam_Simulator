# Battery Simulator Project Rules

## Project Context

This is a Python implementation of a Battery Simulator application, migrated from C++/Qt. The application provides a GUI interface for creating and running battery simulations using OpenFOAM solvers.

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

### 3. PyQt6 Signal/Slot Connections

**Best Practices:**
- Use new-style signals (`signal.connect(slot)`)
- Always disconnect signals in cleanup
- Avoid circular signal connections
- Use `lambda` carefully with proper closures
- Document all signal/slot connections

Example:
```python
# Good
self.button.clicked.connect(self.on_button_clicked)

# Clean up
self.button.clicked.disconnect(self.on_button_clicked)
```

### 4. OpenFOAM Integration

**Requirements:**
- Use `subprocess.Popen` for process management
- Implement non-blocking I/O
- Parse stdout/stderr separately
- Handle process termination gracefully
- Support cross-platform execution

## Code Style

### Python Style
- Follow PEP 8
- Use type hints everywhere
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all public functions/classes

### PyQt6 Style
- Use Qt naming conventions for UI elements
- Prefix slots with `on_` or handle pattern
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

## Error Handling

**Always:**
- Use try-except for all I/O operations
- Log errors with context
- Provide user-friendly error messages
- Implement recovery mechanisms
- Never let exceptions crash the GUI

Example:
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    self.show_error_message("User-friendly message")
    return None
```

## Testing Requirements

### Coverage Targets
- Unit tests: >90% coverage
- Integration tests: All critical workflows
- UI tests: Both loading modes

### Test Organization
```
tests/
├── unit/           # Unit tests by module
├── integration/    # Workflow tests
└── conftest.py     # Shared fixtures
```

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
- Windows
- Path separators (use `pathlib`)
- Process execution differences
- File permissions
- Line endings

## Dependencies

**Required:**
- Python 3.8+
- PyQt6 >= 6.5.2
- OpenFOAM (external)

**Optional:**
- pyqtgraph (plotting)
- matplotlib (alternative plotting)
- pytest (testing)

## Git Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Test additions
- `chore:` Maintenance

Example: `feat: implement auto-detect UI loading mode`

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
2. **Blocking GUI** - Use QThread
3. **Memory leaks** - Disconnect signals, clean up properly
4. **Hard-coded paths** - Use pathlib and configuration
5. **Platform-specific code** - Abstract with utility functions
6. **Missing error handling** - Always use try-except for I/O
7. **Poor UI responsiveness** - Keep operations non-blocking

## Development Workflow

1. **Analysis Phase**: Understand requirements, design architecture
2. **Implementation Phase**: Write code following these rules
3. **Testing Phase**: Write tests, achieve coverage targets
4. **Review Phase**: Code review, refactoring
5. **Documentation Phase**: Update docs, write guides

## Debugging Tips

### Circular Import Issues
```bash
# Visualize import graph
python -c "import src; print(src.__file__)"
# Check for circular dependencies
```

### UI Loading Issues
- Check .ui file paths
- Verify PyQt6 installation
- Test fallback mechanism
- Check console logs

### OpenFOAM Issues
- Verify installation: `which icoFoam`
- Check environment: `echo $WM_PROJECT_DIR`
- Test solver manually
- Check case directory structure

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