# Kilo Code Implementation Guide for Battery Simulator

## Overview

This guide explains how to use Kilo Code with the Battery Simulator project. The project uses custom modes for different development phases and specialized agents for specific tasks.

## Prerequisites

1. **Install Kilo Code Extension**
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X or Cmd+Shift+X)
   - Search for "Kilo Code"
   - Install the extension
   - Reload VS Code

2. **Configure API Provider**
   - Click the Kilo Code icon in the sidebar
   - Click "Settings" gear icon
   - Add your API key (OpenAI, Anthropic, etc.) or use Kilo Credits
   - Test the connection

3. **Project Setup**
   - Ensure all project files are in place
   - Python 3.8+ installed
   - PyQt6 installed: `pip install PyQt6`
   - OpenFOAM installed (optional for full testing)

## Configuration Files

The project includes the following Kilo Code configuration files:

### 1. `.kilocodemodes` (Project Root)
Contains 8 custom modes for different development phases:
- `project-architect` - Project planning and architecture
- `core-app-developer` - Core application development
- `interface-specialist` - Interface implementation
- `openfoam-integration` - OpenFOAM integration
- `template-manager` - Template and file operations
- `ui-loading-specialist` - UI loading mechanisms
- `testing-validation` - Testing and validation
- `documentation-deployment` - Documentation
- `battery-debugger` - Specialized debugging

### 2. `.kilocode/rules/battery-simulator.md`
Project-specific rules that all modes will follow:
- Circular import prevention
- UI loading system rules
- PyQt6 best practices
- OpenFOAM integration guidelines
- Code style requirements

## Using Kilo Code with This Project

### Step 1: Load Project Configuration

1. Open the Battery Simulator project in VS Code
2. Open Kilo Code panel (click icon in sidebar)
3. Kilo Code will automatically detect:
   - `.kilocodemodes` file
   - `.kilocode/rules/` directory
   - Project structure

### Step 2: Select Appropriate Mode

#### For Initial Analysis (Phase 1)
```
Click mode dropdown → Select "🏗️ Project Architect"
```

**What to ask:**
```
Analyze the current Battery Simulator project state and identify:
1. Missing implementations
2. Circular import issues
3. Incomplete functionality
4. Architecture improvements needed

Create a comprehensive implementation plan.
```

#### For Core Development (Phase 2)

**Mode: 💻 Core App Developer**
```
Implement the main application entry point (main.py) with:
1. Proper argument parsing for UI modes
2. Logging configuration
3. QApplication initialization
4. MainWindow creation and display
5. Error handling

Follow the project rules for circular import prevention.
```

**Mode: 🎨 Interface Specialist**
```
Implement CarbonInterface for SPM simulations:
1. Inherit from BaseInterface
2. Set up geometry parameters section
3. Add constants configuration
4. Implement boundary conditions
5. Add parameter validation
6. Support both .ui and hand-coded loading

Test with both UI loading modes.
```

**Mode: ⚙️ OpenFOAM Integration Expert**
```
Implement ProcessController for managing OpenFOAM solver execution:
1. Use subprocess.Popen
2. Implement non-blocking output reading
3. Add start/stop/pause methods
4. Handle process termination
5. Emit signals for GUI updates

Ensure cross-platform compatibility.
```

**Mode: 📁 Template Manager**
```
Implement the project creation system:
1. Copy templates from resources/templates/
2. Update file references with project path
3. Parse and substitute parameters
4. Validate created projects
5. Handle errors gracefully

Test with all three module types (SPM, HalfCell, FullCell).
```

**Mode: 🎭 UI Loading Specialist**
```
Implement UIConfig and UILoader:
1. Support three modes: auto-detect, ui_files, hand_coded
2. Read configuration from environment, CLI args, defaults
3. Load .ui files using PyQt6.uic.loadUi()
4. Implement fallback to hand-coded widgets
5. Log all loading decisions

Test all configuration sources and modes.
```

#### For Testing (Phase 3)

**Mode: 🧪 Testing Engineer**
```
Create comprehensive test suite:
1. Unit tests for all modules
2. Integration tests for workflows
3. Test both UI loading modes
4. Test OpenFOAM integration
5. Cross-platform validation

Aim for >90% coverage.
```

#### For Documentation (Phase 4)

**Mode: 📚 Documentation Specialist**
```
Create comprehensive documentation:
1. Update README with usage instructions
2. Document API with docstrings
3. Create user guides
4. Write troubleshooting section
5. Add installation instructions

Include examples and screenshots.
```

#### For Debugging

**Mode: 🐛 Battery Sim Debugger**
```
Debug the circular import issue between:
- core/application.py
- core/constants.py
- utils/parameter_parser.py

Analyze the import chain and suggest fixes using lazy imports.
```

### Step 3: Working with Multiple Agents

Kilo Code can work on multiple tasks simultaneously:

#### Sequential Workflow
```
1. Switch to Project Architect → Get analysis
2. Switch to Core App Developer → Implement main.py
3. Switch to Interface Specialist → Implement interfaces
4. Switch to Testing Engineer → Write tests
5. Switch to Documentation Specialist → Update docs
```

#### Parallel Tasks (Using Multiple Chat Threads)
You can open multiple Kilo Code instances:
1. Create new editor group (split editor)
2. Each can use different mode
3. Work on different parts simultaneously

### Step 4: Monitoring Progress

Create a checklist to track progress:

#### Phase 1: Analysis ✓
- [ ] Project structure analyzed
- [ ] Missing components identified
- [ ] Architecture plan created
- [ ] Implementation roadmap ready

#### Phase 2: Core Development
- [ ] main.py implemented
- [ ] MainWindow working
- [ ] InterfaceFactory functional
- [ ] BaseInterface complete
- [ ] CarbonInterface working
- [ ] HalfCellInterface implemented
- [ ] FullCellInterface implemented
- [ ] ProcessController functional
- [ ] SolverManager working
- [ ] TemplateManager operational
- [ ] ProjectManager complete
- [ ] UILoader implemented
- [ ] UIConfig functional

#### Phase 3: Testing
- [ ] Unit tests written (>90% coverage)
- [ ] Integration tests pass
- [ ] UI loading tests pass
- [ ] OpenFOAM tests pass
- [ ] Cross-platform tests pass

#### Phase 4: Documentation
- [ ] README updated
- [ ] API documented
- [ ] User guides written
- [ ] Troubleshooting guide ready
- [ ] Installation tested

## Tips for Effective Use

### 1. Be Specific with Requests
```
❌ Bad: "Fix the UI"
✅ Good: "Fix the blank GUI issue that occurs when clicking Next button. 
          The InterfaceFactory should create CarbonInterface but returns None. 
          Check for circular import issues."
```

### 2. Provide Context
```
I'm working on the CarbonInterface class in src/gui/interfaces/carbon_interface.py.
The interface needs to load geometry parameters from blockMeshDict.
Follow the lazy import pattern to avoid circular dependencies with constants.py.
```

### 3. Request Multiple Files
```
Create the following files:
1. src/gui/ui_loader.py - For loading .ui files
2. src/gui/ui_config.py - For configuration management
3. tests/test_ui_loading.py - For testing both

All should follow the project rules in .kilocode/rules/
```

### 4. Iterate and Refine
```
First request: "Implement basic ProcessController"
After review: "Add pause/resume functionality to ProcessController"
After testing: "Fix the race condition in ProcessController output handling"
```

### 5. Use Mode-Specific Expertise
Each mode has specialized knowledge:
- Ask Project Architect for design decisions
- Ask Core App Developer for PyQt6 questions
- Ask Interface Specialist for UI implementation
- Ask OpenFOAM Integration for process control
- Ask Testing Engineer for test strategies
- Ask Debugger for issue resolution

## Common Workflows

### Workflow 1: Implement New Interface
```
1. Mode: Interface Specialist
   Request: "Implement FullCellInterface inheriting from BaseInterface"

2. Mode: Testing Engineer
   Request: "Create unit tests for FullCellInterface"

3. Mode: Debugger
   Request: "Test FullCellInterface with both UI loading modes"

4. Mode: Documentation Specialist
   Request: "Document FullCellInterface API and usage"
```

### Workflow 2: Fix Circular Import
```
1. Mode: Debugger
   Request: "Analyze circular import between core/application.py and utils/parameter_parser.py"

2. Mode: Project Architect
   Request: "Suggest architecture refactoring to eliminate circular imports"

3. Mode: Core App Developer
   Request: "Implement lazy imports as suggested"

4. Mode: Testing Engineer
   Request: "Verify imports work correctly with test_imports.py"
```

### Workflow 3: Add New Feature
```
1. Mode: Project Architect
   Request: "Design architecture for adding PyBaMM solver integration"

2. Mode: OpenFOAM Integration
   Request: "Create SolverInterface base class for multiple solver types"

3. Mode: Interface Specialist
   Request: "Add PyBaMM solver option to interface"

4. Mode: Testing Engineer
   Request: "Create tests for PyBaMM integration"

5. Mode: Documentation Specialist
   Request: "Document PyBaMM solver usage"
```

## Troubleshooting

### Issue: Mode not available
**Solution:** Check that `.kilocodemodes` file is in project root and properly formatted.

### Issue: Rules not being followed
**Solution:** Verify `.kilocode/rules/battery-simulator.md` exists and is readable.

### Issue: Kilo Code giving incorrect advice
**Solution:** 
1. Provide more context about the project
2. Reference specific files and line numbers
3. Show the error messages
4. Specify which mode you're using

### Issue: Multiple conflicting suggestions
**Solution:**
1. Ask Project Architect for design decision
2. Use that decision consistently across modes
3. Document the decision in project rules

## Best Practices

1. **Start with Analysis**: Always begin with Project Architect mode to understand the full scope

2. **One Phase at a Time**: Complete each phase before moving to the next

3. **Test Continuously**: Switch to Testing Engineer mode frequently

4. **Document as You Go**: Don't wait until the end for documentation

5. **Use Debugger Early**: When stuck, switch to Debugger mode immediately

6. **Review Generated Code**: Always review and test code before committing

7. **Update Rules**: Add new rules to `.kilocode/rules/` as you discover them

8. **Track Progress**: Use GitHub issues or a task list to track completion

## Integration with Development Tools

### With Git
```bash
# Let Kilo Code help with commits
Mode: Documentation Specialist
Request: "Review my changes and suggest a commit message"
```

### With pytest
```bash
# Run tests after Kilo Code implementations
pytest tests/ -v --cov=src --cov-report=html
```

### With VS Code Debugger
```bash
# Use Kilo Code to help set breakpoints
Mode: Debugger
Request: "Where should I set breakpoints to debug the UI loading issue?"
```

## Getting Help

### Within Kilo Code
```
Switch to appropriate mode and ask:
- "Explain how [feature] works"
- "What's the best way to implement [functionality]?"
- "Review my implementation of [class]"
- "Suggest improvements for [code]"
```

### Project Resources
- README.md - Project overview
- ARCHITECTURE.md - System design
- .kilocode/rules/ - Project rules
- GitHub Issues - Report problems

## Conclusion

This configuration provides a comprehensive multi-agent system for developing the Battery Simulator project. Each mode is specialized for its phase and follows consistent project rules. Use the modes sequentially through the development phases for best results.

## Quick Reference

| Phase | Mode | Purpose |
|-------|------|---------|
| 1 | Project Architect | Analysis & Planning |
| 2a | Core App Developer | Application Core |
| 2b | Interface Specialist | UI Interfaces |
| 2c | OpenFOAM Integration | Solver Integration |
| 2d | Template Manager | File Operations |
| 2e | UI Loading Specialist | UI System |
| 3 | Testing Engineer | Testing |
| 4 | Documentation Specialist | Documentation |
| * | Battery Debugger | Debugging |

---

**Remember:** The project rules in `.kilocode/rules/battery-simulator.md` apply to all modes. Reference them frequently and update them as the project evolves.