# AI Implementation Prompt for Phase 2 & 3

## Context
Battery Simulator Python application with OpenFOAM backend. Phase 1 (exception handling, MSYS2 integration) complete. Need to implement parameter management and complete all three simulation interfaces.

## Phase 1 Completed Files
- `src/utils/exception_handler.py` - @safe_slot decorator for error handling
- `src/openfoam/msys2_executor.py` - Windows OpenFOAM execution via MSYS2
- `src/openfoam/process_controller.py` - Process management with real-time output
- `src/gui/main_window_enhanced.py` - Template for main window methods

## Task: Implement Phase 2 (SPM Complete) + Phase 3 (HalfCell/FullCell)

### Phase 2: Complete SPM/Carbon Interface

**File: `src/gui/interfaces/carbon_interface.py`**

1. Add `from src.utils.exception_handler import safe_slot` at top
2. Decorate ALL button click methods with `@safe_slot`
3. Implement these methods:

```python
def _update_geometry_parameters(self):
    # Read: self.length_edit.text(), width, height, radius, divisions
    # Convert units from self.unit_combo.currentText()
    # Update system/blockMeshDict using parameter_parser
    # Update system/topoSetDict for ele/solidPhase zones

def _run_geometry_commands(self):
    # Execute: blockMesh, topoSet, splitMeshRegions -cellZones -overwrite
    # Use: self.process_controller.start_process(command, self.case_path)

def _update_constants_parameters(self):
    # Read: self.param_edits[param].text() for all parameters
    # Check: self.material_carbon.isChecked() vs silicon
    # Update: constant/LiProperties, constant/ele/LiProperties, constant/solidPhase/LiProperties

def _run_constants_commands(self):
    # Navigate to solver directory (SPMFoam)
    # Execute: wclean then wmake

def _update_boundary_parameters(self):
    # Read: self.initial_cs_edit (or similar widget)
    # Update: 0/ele/Cs and 0/solidPhase/Cs files

def _update_functions_parameters(self):
    # Read discretization scheme combos
    # Update: system/fvSchemes and system/fvSolution

def _update_control_parameters(self):
    # Read: self.end_time_edit.value(), delta_t, write_interval, tolerance
    # Update: system/controlDict

def _start_simulation(self):
    # Build command: "SPMFoam" (or full solver path)
    # Execute in case directory
    # self.process_controller.start_process("SPMFoam", self.case_path)
```

**File: `src/utils/parameter_parser.py`**

Add these methods to `ParameterManager` class:

```python
def update_blockmesh(self, length, width, height, x_div, y_div, z_div, unit='micrometer'):
    # Read system/blockMeshDict
    # Calculate vertices based on dimensions * unit conversion
    # Update vertices section (8 points for hex block)
    # Update blocks section with divisions
    # Write back preserving OpenFOAM format

def update_toposet(self, regions):
    # Read system/topoSetDict
    # Update cellSet definitions for each region
    # regions = ['ele', 'solidPhase'] for SPM

def update_liproperties(self, params_dict, material='Gr'):
    # Read constant/LiProperties
    # Find each param (DS_value, CS_max, etc.)
    # Replace value while keeping format: "DS_value DS_value [0 2 -1 0 0 0 0] 1e-14;"
    # Write back

def update_controldict(self, end_time, delta_t, write_interval, tolerance):
    # Read system/controlDict
    # Update: endTime, deltaT, writeInterval
    # Preserve dictionary format

def update_fvschemes(self, schemes_dict):
    # Read system/fvSchemes
    # Update ddtSchemes, gradSchemes, divSchemes, laplacianSchemes, interpolationSchemes

def update_fvsolution(self, solvers_dict, relaxation_factors):
    # Read system/fvSolution
    # Update solver settings and relaxation factors
```

### Phase 3: HalfCell & FullCell Interfaces

**Files: `src/gui/interfaces/halfcell_interface.py` and `fullcell_interface.py`**

Pattern: Copy carbon_interface.py structure, modify for multi-region:

**HalfCell changes:**
- Two regions: WE (working electrode), sep (separator)
- Add widgets: we_thickness, sep_thickness, porosity, etc.
- Update TWO LiProperties files: constant/WE/LiProperties, constant/sep/LiProperties
- Update mesh for two zones

**FullCell changes:**
- Three regions: anode, seperator (note spelling), cathode
- Add widgets for all three regions
- Different materials: anode (Graphite/Silicon), cathode (NMC/NCA/LFP)
- Update THREE LiProperties files
- Update mesh for three zones

**Pattern for _update_constants_parameters():**
```python
def _update_constants_parameters(self):
    # Get params for each region
    params_we = self._get_we_parameters()
    params_sep = self._get_sep_parameters()
    
    # Update each region's LiProperties
    self.parameter_manager.update_liproperties_multiregion({
        'WE': params_we,
        'sep': params_sep
    })
```

### Integration with Main Window

**File: `src/gui/main_window.py`**

Copy methods from `main_window_enhanced.py`:
- `_on_choose_path_clicked`
- `_on_next_button_clicked`
- `_create_project`
- `_create_project_manual`
- `_open_interface`
- `_on_interface_exit`
- `_detect_project_type`

Ensure buttons are connected:
```python
self.main_path_button.clicked.connect(self._on_choose_path_clicked)
self.main_next_button.clicked.connect(self._on_next_button_clicked)
```

### Critical Rules

1. **Always use @safe_slot decorator** on signal handlers
2. **Always log operations**: logger.info("Updating geometry...")
3. **Validate inputs**: Check for empty strings, negative numbers
4. **Preserve OpenFOAM format**: Don't break semicolons, brackets
5. **Use pathlib.Path**: For cross-platform path handling
6. **Handle missing files gracefully**: Check file existence before reading

### OpenFOAM File Format Pattern

```python
# Reading
with open(file_path, 'r') as f:
    lines = f.readlines()

# Updating (preserve format)
new_lines = []
for line in lines:
    if 'endTime' in line:
        new_lines.append(f'endTime         {end_time};\n')
    else:
        new_lines.append(line)

# Writing
with open(file_path, 'w') as f:
    f.writelines(new_lines)
```

### Testing Each Implementation

After implementing each method:
1. Create project via UI
2. Click corresponding button
3. Check terminal output for errors
4. Verify file was modified correctly
5. Run OpenFOAM command manually to verify

### Success Criteria

- All button clicks work without crashes
- Files are updated correctly
- OpenFOAM commands execute successfully
- Terminal shows real-time output
- Can complete full simulation workflow for all three interfaces

### Output

Provide:
1. Modified/new Python files
2. Brief summary of changes per file
3. Any discovered issues needing manual fix
4. Testing recommendations

Focus on correctness over perfection - working implementation beats elegant incomplete code.
