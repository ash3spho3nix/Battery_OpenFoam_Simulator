# PHASE 2 & 3 IMPLEMENTATION GUIDE

## Phase 1 Complete ✅

The following have been implemented:
1. ✅ Exception handling decorator (`src/utils/exception_handler.py`)
2. ✅ MSYS2 executor for OpenFOAM (`src/openfoam/msys2_executor.py`)
3. ✅ Enhanced process controller (`src/openfoam/process_controller.py`)
4. ✅ Main window enhancements template (`src/gui/main_window_enhanced.py`)

---

## PHASE 2: SPM/Carbon Complete Implementation

### Goal
Complete end-to-end SPM simulation workflow with all parameter management.

### Files to Modify

#### 1. `src/gui/interfaces/carbon_interface.py` (PRIMARY)

**Add safe_slot decorator to ALL button handlers:**
```python
from src.utils.exception_handler import safe_slot

# Wrap all methods like this:
@safe_slot
def _on_change_geometry_clicked(self):
    # existing code
```

**Implement parameter update methods:**

**_update_geometry_parameters():**
- Read values from: `self.length_edit.text()`, `self.width_edit.text()`, `self.height_edit.text()`, etc.
- Use `ParameterManager` to update `system/blockMeshDict`
- Update `system/topoSetDict` with new dimensions
- Key pattern:
  ```python
  from src.utils.parameter_parser import ParameterManager
  param_mgr = ParameterManager(self.case_path)
  param_mgr.update_blockmesh(length, width, height, divisions)
  ```

**_run_geometry_commands():**
- Execute in order:
  1. `blockMesh` - creates computational mesh
  2. `topoSet` - creates cell zones
  3. `splitMeshRegions -cellZones -overwrite` - splits into ele/solidPhase
- Use: `self.process_controller.start_process(command, self.case_path)`

**_update_constants_parameters():**
- Read from: `self.param_edits[param].text()` for each parameter
- Update `constant/LiProperties` file
- Update `constant/ele/LiProperties` and `constant/solidPhase/LiProperties`
- Material selection: read `self.material_carbon.isChecked()`

**_run_constants_commands():**
- Execute in SPMFoam directory:
  1. `wclean` - clean previous build
  2. `wmake` - compile solver

**_update_control_parameters():**
- Read from spinboxes: `self.end_time_edit.value()`, etc.
- Update `system/controlDict`:
  - `endTime`
  - `deltaT`
  - `writeInterval`

**_start_simulation():**
- Build command: `SPMFoam` or full solver name
- Execute: `self.process_controller.start_process("SPMFoam", self.case_path)`
- Monitor progress in terminal

#### 2. `src/utils/parameter_parser.py` (SECONDARY)

**Add/enhance methods:**

**update_blockmesh(length, width, height, x_div, y_div, z_div, unit='micrometer'):**
- Open `{case_path}/system/blockMeshDict`
- Find vertices section
- Calculate coordinates based on dimensions and unit conversion
- Update divisions in blocks section
- Write back to file

**update_liproperties(params_dict, material_type='Gr'):**
- Open `{case_path}/constant/LiProperties`
- Find each parameter line
- Replace value while preserving format
- Handle both scientific notation and regular numbers

**update_controldict(end_time, delta_t, write_interval):**
- Open `{case_path}/system/controlDict`
- Find and update each parameter
- Preserve OpenFOAM dictionary format

**Pattern for all methods:**
```python
def update_blockmesh(self, case_path, length, width, height, ...):
    file_path = Path(case_path) / "system" / "blockMeshDict"
    
    # Read file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update using regex or line-by-line
    import re
    content = re.sub(
        r'vertices\s*\((.*?)\);',
        f'vertices ({new_vertices});',
        content,
        flags=re.DOTALL
    )
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
```

#### 3. `src/gui/main_window.py` (TERTIARY)

**Integrate enhanced methods from main_window_enhanced.py:**
- Copy all @safe_slot methods
- Add imports at top
- Replace existing button connection code
- Test project creation workflow

#### 4. Testing Phase 2

Run these tests in order:
1. Create SPM project
2. Modify geometry → Run geometry → Check mesh files created
3. Modify constants → Check LiProperties updated
4. Run simulation → Monitor terminal output
5. Verify output files in case directory

---

## PHASE 3: HalfCell & FullCell Implementation

### Goal
Replicate SPM workflow for HalfCell and FullCell with multi-region support.

### Files to Modify

#### 1. `src/gui/interfaces/halfcell_interface.py`

**Complete _add_boundary_configuration():**
```python
def _add_boundary_configuration(self, layout):
    # Working Electrode (WE) group
    we_group = QGroupBox("Working Electrode")
    we_layout = QVBoxLayout()
    
    # Thickness
    self.we_thickness_edit = QLineEdit("50")
    # Active material fraction
    self.we_amf_edit = QLineEdit("0.5")
    # Porosity
    self.we_porosity_edit = QLineEdit("0.3")
    
    # Add to layout...
    
    # Separator group
    sep_group = QGroupBox("Separator")
    # Similar structure
```

**Implement multi-region parameter updates:**
- Update `constant/WE/LiProperties`
- Update `constant/sep/LiProperties`
- Handle two-region mesh generation

**Key differences from SPM:**
- Two regions instead of one
- Different boundary conditions between WE and separator
- Modified topoSetDict for two zones

#### 2. `src/gui/interfaces/fullcell_interface.py`

**Complete _add_boundary_configuration():**
```python
def _add_boundary_configuration(self, layout):
    # Anode group
    anode_group = QGroupBox("Anode")
    self.anode_thickness_edit = QLineEdit("70")
    self.anode_material_combo = QComboBox()
    self.anode_material_combo.addItems(["Graphite", "Silicon", "LTO"])
    # ... more parameters
    
    # Separator group  
    sep_group = QGroupBox("Separator")
    # ...
    
    # Cathode group
    cathode_group = QGroupBox("Cathode")
    self.cathode_thickness_edit = QLineEdit("50")
    self.cathode_material_combo = QComboBox()
    self.cathode_material_combo.addItems(["NMC", "NCA", "LFP"])
    # ... more parameters
```

**Implement three-region updates:**
- Update `constant/anode/LiProperties`
- Update `constant/seperator/LiProperties` (note spelling in templates)
- Update `constant/cathode/LiProperties`
- Three-zone mesh generation

**Key differences from HalfCell:**
- Three regions: anode, separator, cathode
- More complex coupling
- Different OCV curves for anode vs cathode
- Voltage calculation from both electrodes

### Implementation Pattern for Both

**For each interface, implement in this order:**

1. **UI Completion** (1 day)
   - Add all input widgets
   - Connect to existing base interface structure
   - Test widget creation

2. **Parameter Management** (1 day)
   - Implement update methods
   - Test file writing
   - Verify OpenFOAM format preservation

3. **Command Execution** (1 day)
   - Geometry commands
   - Solver compilation
   - Simulation execution

4. **Testing** (1 day)
   - End-to-end workflow
   - Error handling
   - Output verification

### Helper Functions Needed

#### In `src/utils/parameter_parser.py`:

**update_multiregion_liproperties(regions, params_by_region):**
```python
def update_multiregion_liproperties(self, case_path, regions, params):
    """Update LiProperties for multiple regions.
    
    Args:
        case_path: Path to case directory
        regions: list like ['WE', 'sep'] or ['anode', 'seperator', 'cathode']
        params: dict like {'WE': {params}, 'sep': {params}}
    """
    for region in regions:
        region_path = Path(case_path) / "constant" / region / "LiProperties"
        self._update_single_liproperties(region_path, params[region])
```

**update_multiregion_blockmesh(regions, thicknesses):**
- Calculate coordinates for each region
- Update vertices in blockMeshDict
- Update block definitions for each region

#### In `src/openfoam/solver_manager.py`:

**run_multiregion_mesh(case_path, num_regions):**
```python
def run_multiregion_mesh(self, case_path, num_regions):
    """Run mesh generation for multi-region case."""
    commands = [
        "blockMesh",
        "topoSet",
        "splitMeshRegions -cellZones -overwrite"
    ]
    
    for cmd in commands:
        self.process_controller.start_process(cmd, case_path)
        # Wait for completion
```

---

## CRITICAL IMPLEMENTATION NOTES

### For All Phases:

1. **Always use safe_slot decorator** on button click handlers
2. **Always log operations** with logger.info/debug/error
3. **Always validate user input** before file operations
4. **Always use Path objects** from pathlib for cross-platform compatibility
5. **Always preserve OpenFOAM file format** - especially semicolons and brackets

### Error Handling Pattern:

```python
@safe_slot
def _on_change_geometry_clicked(self):
    try:
        # Validate inputs
        length = float(self.length_edit.text())
        if length <= 0:
            raise ValueError("Length must be positive")
            
        # Update files
        self._update_geometry_parameters()
        
        # Show success
        self.terminal_output.append("✓ Geometry updated successfully")
        
    except ValueError as e:
        QMessageBox.warning(self, "Invalid Input", str(e))
    except Exception as e:
        logger.error(f"Geometry update failed: {e}")
        raise  # Re-raise to be caught by safe_slot
```

### OpenFOAM File Format Rules:

1. **Dictionary format**: `keyword value;`
2. **Lists**: `listName ( value1 value2 );`
3. **Nested**: `group { keyword value; }`
4. **Comments**: `// comment` or `/* block */`
5. **Preserve whitespace** in structured sections

### Path Handling:

```python
# Always use pathlib and convert for MSYS2
from pathlib import Path

case_path = Path(self.project_path) / "Case"
system_dir = case_path / "system"
blockmesh_file = system_dir / "blockMeshDict"

# For MSYS2 executor, paths are auto-converted
self.process_controller.start_process("blockMesh", str(case_path))
```

---

## TESTING STRATEGY

### For Each Interface:

**Unit Testing:**
- Test parameter reading from UI
- Test file writing
- Test command construction

**Integration Testing:**
- Test complete geometry workflow
- Test complete constants workflow
- Test complete simulation workflow

**Error Testing:**
- Invalid inputs
- Missing files
- Failed commands

### Test Checklist:

- [ ] Project creation
- [ ] Geometry modification
- [ ] Mesh generation (blockMesh, topoSet, splitMeshRegions)
- [ ] Constants modification
- [ ] Solver compilation (wclean, wmake)
- [ ] Boundary conditions
- [ ] Functions/schemes
- [ ] Control parameters
- [ ] Simulation execution
- [ ] Terminal output capture
- [ ] Error handling

---

## QUICK REFERENCE: Key File Locations

```
project_root/
  test_spm_001/                    # Created project
    Case/                          # OpenFOAM case directory
      0/                           # Initial conditions
        ele/                       # Electrolyte region files
        solidPhase/                # Solid phase region files
      constant/                    # Physical properties
        ele/
          LiProperties            # Parameters to update
        solidPhase/
          LiProperties            # Parameters to update
        polyMesh/                  # Mesh files
      system/                      # Simulation control
        blockMeshDict              # Mesh definition - UPDATE THIS
        topoSetDict                # Cell zones - UPDATE THIS
        controlDict                # Time control - UPDATE THIS
        fvSchemes                  # Discretization - UPDATE THIS
        fvSolution                 # Solver settings - UPDATE THIS
    SPMFoam/                       # Solver source code
      Make/                        # Compilation files
```

---

## COMPLETION CRITERIA

### Phase 2 Complete When:
- ✅ SPM project creation works
- ✅ All geometry commands execute successfully
- ✅ All constants update correctly
- ✅ Solver compiles without errors
- ✅ Simulation runs and produces output
- ✅ Terminal shows real-time output
- ✅ Can pause/stop simulation
- ✅ Error messages are clear and helpful

### Phase 3 Complete When:
- ✅ All Phase 2 criteria met for SPM
- ✅ HalfCell project creation and execution works
- ✅ FullCell project creation and execution works
- ✅ Multi-region parameter updates work
- ✅ All three interfaces are functional

---

## ESTIMATED TIME

**Phase 2 (SPM Complete):**
- Day 1: Parameter management implementation
- Day 2: Command execution and testing
- Day 3: Bug fixes and refinement
- **Total: 3 days**

**Phase 3 (HalfCell + FullCell):**
- Day 4-5: HalfCell implementation (following SPM pattern)
- Day 6-7: FullCell implementation (following SPM pattern)
- Day 8: Integration testing
- **Total: 5 days**

**Grand Total: 8 working days for Phases 2 & 3**

---

## NEXT STEPS

1. Review Phase 1 implementation
2. Test OpenFOAM-MSYS2 integration manually
3. Begin Phase 2 with carbon_interface.py
4. Follow implementation pattern for each method
5. Test incrementally after each feature
6. Move to Phase 3 only after Phase 2 is solid

Good luck with the implementation!
