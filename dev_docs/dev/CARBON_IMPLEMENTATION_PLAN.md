# Carbon/SPM Interface Implementation Plan

## Overview

This document provides a detailed implementation plan for completing the Carbon/SPM (Single Particle Model) interface to achieve a fully working end-to-end simulation on Windows.

## Current Status

Based on the architecture analysis, the Carbon interface is currently **100% complete** in terms of core functionality, but needs integration and testing for end-to-end simulation execution.

### ✅ Already Implemented
- **Carbon Interface**: Fully functional Single Particle Model interface
- **Geometry Configuration**: Dimensions, divisions, units
- **Material Properties**: Diffusivity, concentration, reaction rate
- **Boundary Conditions**: Charge/discharge, material selection
- **Solver Functions**: Discretization schemes
- **Control Parameters**: Time, timestep, tolerance
- **OpenFOAM Integration**: Process control, solver management
- **Real-time Output**: Terminal monitoring

### 🎯 Target: End-to-End SPM Simulation on Windows

## Implementation Plan

### Phase 1: Signal Connection Completion (Day 1)

#### Task 1.1: Complete Carbon Interface Signal Connections
**Duration**: 4 hours
**Priority**: HIGH

**Objectives**:
- Ensure all UI widgets are properly connected to slots
- Verify signal-slot connections for all tabs
- Test parameter validation and updates

**Detailed Steps**:

1. **Geometry Tab Signals** (1 hour):
   ```python
   # Connect geometry parameter changes
   self.length_edit.textChanged.connect(self._on_geometry_changed)
   self.width_edit.textChanged.connect(self._on_geometry_changed)
   self.height_edit.textChanged.connect(self._on_geometry_changed)
   self.radius_edit.textChanged.connect(self._on_geometry_changed)
   self.unit_combo.currentTextChanged.connect(self._on_unit_changed)
   
   # Connect geometry buttons
   self.change_geometry_button.clicked.connect(self._on_change_geometry_clicked)
   self.run_geometry_button.clicked.connect(self._on_run_geometry_clicked)
   self.view_geometry_button.clicked.connect(self._on_view_geometry_clicked)
   ```

2. **Constants Tab Signals** (1 hour):
   ```python
   # Connect material property changes
   for param_name, widget in self.param_edits.items():
       if hasattr(widget, 'textChanged'):
           widget.textChanged.connect(self._on_constants_changed)
   
   # Connect material selection
   self.material_carbon.toggled.connect(self._on_material_changed)
   self.material_silicon.toggled.connect(self._on_material_changed)
   
   # Connect constants buttons
   self.change_constants_button.clicked.connect(self._on_change_constants_clicked)
   self.run_constants_button.clicked.connect(self._on_run_constants_clicked)
   self.help_constants_button.clicked.connect(self._on_help_constants_clicked)
   ```

3. **Boundary Tab Signals** (1 hour):
   ```python
   # Connect boundary condition changes
   self.initial_cs_edit.textChanged.connect(self._on_boundary_changed)
   self.charge_radio.toggled.connect(self._on_boundary_changed)
   self.discharge_radio.toggled.connect(self._on_boundary_changed)
   
   # Connect boundary buttons
   self.change_boundary_button.clicked.connect(self._on_change_boundary_clicked)
   self.run_boundary_button.clicked.connect(self._on_run_boundary_clicked)
   ```

4. **Functions Tab Signals** (0.5 hour):
   ```python
   # Connect discretization scheme changes
   for scheme_type in ['ddtSchemes', 'gradSchemes', 'divSchemes', 
                      'laplacianSchemes', 'interpolationSchemes']:
       combo = getattr(self, f"{scheme_type.lower()}_combo")
       combo.currentTextChanged.connect(self._on_functions_changed)
   
   # Connect functions buttons
   self.change_functions_button.clicked.connect(self._on_change_functions_clicked)
   self.run_functions_button.clicked.connect(self._on_run_functions_clicked)
   ```

5. **Control Tab Signals** (0.5 hour):
   ```python
   # Connect control parameter changes
   self.end_time_edit.valueChanged.connect(self._on_control_changed)
   self.delta_t_edit.valueChanged.connect(self._on_control_changed)
   self.write_interval_edit.valueChanged.connect(self._on_control_changed)
   self.tolerance_edit.textChanged.connect(self._on_control_changed)
   
   # Connect control buttons
   self.change_control_button.clicked.connect(self._on_change_control_clicked)
   self.run_button.clicked.connect(self._on_run_clicked)
   self.pause_button.clicked.connect(self._on_pause_clicked)
   self.stop_button.clicked.connect(self._on_stop_clicked)
   ```

**Success Criteria**:
- ✅ All UI widgets emit signals when changed
- ✅ All buttons trigger appropriate slots
- ✅ Parameter changes are captured and validated
- ✅ No unconnected widgets

**Validation Tests**:
```python
# Test signal connections
def test_signal_connections():
    interface = CarbonInterface()
    
    # Test geometry signals
    interface.length_edit.setText("200")
    # Verify _on_geometry_changed was called
    
    # Test button clicks
    interface.change_geometry_button.click()
    # Verify _on_change_geometry_clicked was called
    
    # Test parameter validation
    interface.radius_edit.setText("invalid")
    # Verify validation error handling
```

---

### Phase 2: Parameter Integration (Day 2)

#### Task 2.1: Connect UI Inputs to blockMeshDict
**Duration**: 2 hours
**Priority**: HIGH

**Objectives**:
- Map UI geometry parameters to blockMeshDict
- Implement parameter validation
- Generate valid OpenFOAM blockMeshDict files

**Detailed Steps**:

1. **Parameter Mapping** (1 hour):
   ```python
   def _update_block_mesh_dict(self):
       """Update blockMeshDict with current UI parameters."""
       try:
           # Get validated parameters from UI
           length = float(self.length_edit.text())
           width = float(self.width_edit.text())
           height = float(self.height_edit.text())
           unit_factor = self._get_unit_factor()
           
           # Convert to meters
           length_m = length * unit_factor
           width_m = width * unit_factor
           height_m = height * unit_factor
           
           # Generate blockMeshDict content
           content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
   =========                 |
   \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
   \\  /    A nd           | Version:  6
   \\/     M anipulation  |
   \\*---------------------------------------------------------------------------*/
   FoamFile
   {{
       version     2.0;
       format      ascii;
       class       dictionary;
       object      blockMeshDict;
   }}
   // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
   
   convertToMeters {unit_factor};
   
   vertices
   (
       ({-length_m/2} {-width_m/2} {-height_m/2})
       ({length_m/2} {-width_m/2} {-height_m/2})
       ({length_m/2} {width_m/2} {-height_m/2})
       ({-length_m/2} {width_m/2} {-height_m/2})
       ({-length_m/2} {-width_m/2} {height_m/2})
       ({length_m/2} {-width_m/2} {height_m/2})
       ({length_m/2} {width_m/2} {height_m/2})
       ({-length_m/2} {width_m/2} {height_m/2})
   );
   
   blocks
   (
       hex (0 1 2 3 4 5 6 7) ({self.x_div_edit.value()} {self.y_div_edit.value()} {self.z_div_edit.value()}) simpleGrading (1 1 1)
   );
   
   edges
   (
   );
   
   boundary
   (
       inlet
       {{
           type patch;
           faces
           (
               (0 4 7 3)
           );
       }}
       outlet
       {{
           type patch;
           faces
           (
               (2 6 5 1)
           );
       }}
       fixedWalls
       {{
           type wall;
           faces
           (
               (3 7 6 2)
               (7 4 5 6)
               (0 3 2 1)
               (1 5 4 0)
           );
       }}
   );
   
   mergePatchPairs
   (
   );
   
   // ************************************************************************* //
   """
           
           # Write to file
           block_mesh_path = os.path.join(self.case_path, "system", "blockMeshDict")
           with open(block_mesh_path, 'w') as f:
               f.write(content)
               
           logger.info("blockMeshDict updated successfully")
           
       except Exception as e:
           logger.error(f"Failed to update blockMeshDict: {e}")
           raise
   ```

2. **Parameter Validation** (0.5 hour):
   ```python
   def _validate_geometry_parameters(self):
       """Validate geometry parameters before updating files."""
       errors = []
       
       try:
           length = float(self.length_edit.text())
           width = float(self.width_edit.text())
           height = float(self.height_edit.text())
           radius = float(self.radius_edit.text())
           
           # Check positive values
           if length <= 0:
               errors.append("Length must be positive")
           if width <= 0:
               errors.append("Width must be positive")
           if height <= 0:
               errors.append("Height must be positive")
           if radius <= 0:
               errors.append("Radius must be positive")
           
           # Check radius constraints
           min_dimension = min(length, width, height)
           if radius >= min_dimension / 2:
               errors.append("Radius must be smaller than half of length, width, and height")
           
           # Check division constraints
           x_div = self.x_div_edit.value()
           y_div = self.y_div_edit.value()
           z_div = self.z_div_edit.value()
           
           if x_div <= 0 or y_div <= 0 or z_div <= 0:
               errors.append("Division values must be positive")
           
           if x_div > 1000 or y_div > 1000 or z_div > 1000:
               errors.append("Division values should be less than 1000")
               
       except ValueError as e:
           errors.append(f"Invalid numeric value: {e}")
       
       return errors
   ```

3. **Integration with UI** (0.5 hour):
   ```python
   def _on_geometry_changed(self):
       """Handle geometry parameter changes."""
       # Validate parameters
       errors = self._validate_geometry_parameters()
       
       if errors:
           # Show validation errors
           error_msg = "\n".join(errors)
           self._show_validation_error("Geometry Validation Error", error_msg)
           return
       
       # Update blockMeshDict
       try:
           self._update_block_mesh_dict()
           self._show_status_message("Geometry parameters updated successfully")
       except Exception as e:
           self._show_error_message(f"Failed to update geometry: {e}")
   ```

**Success Criteria**:
- ✅ UI parameters correctly mapped to blockMeshDict
- ✅ Parameter validation prevents invalid values
- ✅ Generated blockMeshDict is syntactically correct
- ✅ Error handling for invalid parameters

**Validation Tests**:
```python
def test_block_mesh_dict_generation():
    interface = CarbonInterface()
    
    # Set valid parameters
    interface.length_edit.setText("100")
    interface.width_edit.setText("100")
    interface.height_edit.setText("100")
    interface.radius_edit.setText("50")
    interface.x_div_edit.setValue(20)
    interface.y_div_edit.setValue(20)
    interface.z_div_edit.setValue(20)
    
    # Generate blockMeshDict
    interface._update_block_mesh_dict()
    
    # Verify file exists and is valid
    block_mesh_path = os.path.join(interface.case_path, "system", "blockMeshDict")
    assert os.path.exists(block_mesh_path)
    
    # Verify content
    with open(block_mesh_path, 'r') as f:
        content = f.read()
        assert "convertToMeters 1e-06" in content
        assert "hex (0 1 2 3 4 5 6 7) (20 20 20)" in content
```

---

#### Task 2.2: Connect UI Inputs to LiProperties
**Duration**: 2 hours
**Priority**: HIGH

**Objectives**:
- Map UI material parameters to LiProperties
- Implement material-specific property validation
- Generate valid OpenFOAM LiProperties files

**Detailed Steps**:

1. **Parameter Mapping** (1 hour):
   ```python
   def _update_li_properties(self):
       """Update LiProperties with current UI parameters."""
       try:
           # Get parameters from UI
           ds_value = float(self.param_edits["DS_value"].text())
           cs_max = float(self.param_edits["CS_max"].text())
           k_react = float(self.param_edits["kReact"].text())
           r_value = float(self.param_edits["R"].text())
           f_value = float(self.param_edits["F"].text())
           ce = float(self.param_edits["Ce"].text())
           alpha_a = float(self.param_edits["alphaA"].text())
           alpha_c = float(self.param_edits["alphaC"].text())
           t_temp = float(self.param_edits["T_temp"].text())
           i_app = float(self.param_edits["I_app"].text())
           initial_cs = float(self.param_edits["initial_cs"].text())
           
           # Determine material
           material = "OCV_Gr.H" if self.material_carbon.isChecked() else "OCV_Si.H"
           
           # Generate LiProperties content
           content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
   =========                 |
   \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
   \\  /    A nd           | Version:  6
   \\/     M anipulation  |
   \\*---------------------------------------------------------------------------*/
   FoamFile
   {{
       version     2.0;
       format      ascii;
       class       dictionary;
       object      LiProperties;
   }}
   // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
   
   Li
   {{
       Ds [0 2 -1 0 0 0 0] {ds_value};
       Cs_max [0 0 -3 0 0 0 0] {cs_max};
       kReact [0 0 -1 0 0 0 0] {k_react};
       R [0 0 0 0 0 0 0] {r_value};
       F [0 0 0 0 0 1 0] {f_value};
       Ce [0 0 -3 0 0 0 0] {ce};
       alphaA [0 0 0 0 0 0 0] {alpha_a};
       alphaC [0 0 0 0 0 0 0] {alpha_c};
       T [0 0 0 1 0 0 0] {t_temp};
       I_app [0 0 -2 0 0 1 0] {i_app};
       initial_cs [0 0 -3 0 0 0 0] {initial_cs};
       
       #include "{material}"
   }}
   
   // ************************************************************************* //
   """
           
           # Write to file
           li_props_path = os.path.join(self.case_path, "constant", "LiProperties")
           with open(li_props_path, 'w') as f:
               f.write(content)
               
           logger.info("LiProperties updated successfully")
           
       except Exception as e:
           logger.error(f"Failed to update LiProperties: {e}")
           raise
   ```

2. **Material-Specific Validation** (0.5 hour):
   ```python
   def _validate_material_parameters(self):
       """Validate material parameters based on selected material."""
       errors = []
       
       try:
           ds_value = float(self.param_edits["DS_value"].text())
           cs_max = float(self.param_edits["CS_max"].text())
           k_react = float(self.param_edits["kReact"].text())
           alpha_a = float(self.param_edits["alphaA"].text())
           alpha_c = float(self.param_edits["alphaC"].text())
           i_app = float(self.param_edits["I_app"].text())
           
           # Validate diffusivity range
           if not (1e-20 <= ds_value <= 1e-6):
               errors.append("DS value should be between 1e-20 and 1e-6")
           
           # Validate concentration range
           if not (1000 <= cs_max <= 100000):
               errors.append("CS_max should be between 1000 and 100000")
           
           # Validate reaction rate
           if not (1e-20 <= k_react <= 1e-6):
               errors.append("kReact should be between 1e-20 and 1e-6")
           
           # Validate transfer coefficients
           if not (0.0 <= alpha_a <= 1.0):
               errors.append("alphaA should be between 0.0 and 1.0")
           if not (0.0 <= alpha_c <= 1.0):
               errors.append("alphaC should be between 0.0 and 1.0")
           
           # Validate current density
           if not (-10000 <= i_app <= 10000):
               errors.append("I_app should be between -10000 and 10000")
               
       except ValueError as e:
           errors.append(f"Invalid numeric value: {e}")
       
       return errors
   ```

3. **Integration with UI** (0.5 hour):
   ```python
   def _on_constants_changed(self):
       """Handle material parameter changes."""
       # Validate parameters
       errors = self._validate_material_parameters()
       
       if errors:
           # Show validation errors
           error_msg = "\n".join(errors)
           self._show_validation_error("Material Validation Error", error_msg)
           return
       
       # Update LiProperties
       try:
           self._update_li_properties()
           self._show_status_message("Material parameters updated successfully")
       except Exception as e:
           self._show_error_message(f"Failed to update material properties: {e}")
   ```

**Success Criteria**:
- ✅ UI parameters correctly mapped to LiProperties
- ✅ Material-specific validation works
- ✅ Generated LiProperties is syntactically correct
- ✅ Material selection updates file correctly

**Validation Tests**:
```python
def test_li_properties_generation():
    interface = CarbonInterface()
    
    # Set material parameters
    interface.param_edits["DS_value"].setText("1e-14")
    interface.param_edits["CS_max"].setText("30000")
    interface.param_edits["kReact"].setText("1e-11")
    interface.material_carbon.setChecked(True)
    
    # Generate LiProperties
    interface._update_li_properties()
    
    # Verify file exists and is valid
    li_props_path = os.path.join(interface.case_path, "constant", "LiProperties")
    assert os.path.exists(li_props_path)
    
    # Verify content
    with open(li_props_path, 'r') as f:
        content = f.read()
        assert "Ds [0 2 -1 0 0 0 0] 1e-14" in content
        assert "#include \"OCV_Gr.H\"" in content
```

---

#### Task 2.3: Connect UI Inputs to fvSchemes/fvSolution
**Duration**: 2 hours
**Priority**: HIGH

**Objectives**:
- Map UI discretization parameters to fvSchemes
- Map UI solver parameters to fvSolution
- Generate valid OpenFOAM configuration files

**Detailed Steps**:

1. **fvSchemes Generation** (1 hour):
   ```python
   def _update_fv_schemes(self):
       """Update fvSchemes with current UI parameters."""
       try:
           # Get discretization schemes from UI
           ddt_scheme = self.ddtschemes_combo.currentText()
           grad_scheme = self.gradschemes_combo.currentText()
           div_scheme = self.divschemes_combo.currentText()
           laplacian_scheme = self.laplacianschemes_combo.currentText()
           interpolation_scheme = self.interpolationschemes_combo.currentText()
           
           # Generate fvSchemes content
           content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
   =========                 |
   \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
   \\  /    A nd           | Version:  6
   \\/     M anipulation  |
   \\*---------------------------------------------------------------------------*/
   FoamFile
   {{
       version     2.0;
       format      ascii;
       class       dictionary;
       object      fvSchemes;
   }}
   // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
   
   ddtSchemes
   {{
       default         {ddt_scheme};
   }}
   
   gradSchemes
   {{
       default         {grad_scheme};
   }}
   
   divSchemes
   {{
       default         none;
       div(phi,Gamma)  {div_scheme};
   }}
   
   laplacianSchemes
   {{
       default         {laplacian_scheme};
   }}
   
   interpolationSchemes
   {{
       default         {interpolation_scheme};
   }}
   
   snGradSchemes
   {{
       default         corrected;
   }}
   
   wallDist
   {{
       method          meshWave;
   }}
   
   // ************************************************************************* //
   """
           
           # Write to file
           fv_schemes_path = os.path.join(self.case_path, "system", "fvSchemes")
           with open(fv_schemes_path, 'w') as f:
               f.write(content)
               
           logger.info("fvSchemes updated successfully")
           
       except Exception as e:
           logger.error(f"Failed to update fvSchemes: {e}")
           raise
   ```

2. **fvSolution Generation** (1 hour):
   ```python
   def _update_fv_solution(self):
       """Update fvSolution with current UI parameters."""
       try:
           # Get tolerance from UI
           tolerance = float(self.tolerance_edit.text())
           
           # Generate fvSolution content
           content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
   =========                 |
   \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
   \\  /    A nd           | Version:  6
   \\/     M anipulation  |
   \\*---------------------------------------------------------------------------*/
   FoamFile
   {{
       version     2.0;
       format      ascii;
       class       dictionary;
       object      fvSolution;
   }}
   // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
   
   solvers
   {{
       cs
       {{
           solver          PCG;
           preconditioner  DIC;
           tolerance       {tolerance};
           relTol          0.1;
       }}
   }}
   
   PIMPLE
   {{
       nNonOrthogonalCorrectors 0;
   }}
   
   // ************************************************************************* //
   """
           
           # Write to file
           fv_solution_path = os.path.join(self.case_path, "system", "fvSolution")
           with open(fv_solution_path, 'w') as f:
               f.write(content)
               
           logger.info("fvSolution updated successfully")
           
       except Exception as e:
           logger.error(f"Failed to update fvSolution: {e}")
           raise
   ```

**Success Criteria**:
- ✅ UI parameters correctly mapped to fvSchemes/fvSolution
- ✅ Generated files are syntactically correct
- ✅ Scheme selection updates files correctly

**Validation Tests**:
```python
def test_fv_schemes_generation():
    interface = CarbonInterface()
    
    # Set discretization schemes
    interface.ddtschemes_combo.setCurrentText("Euler")
    interface.gradschemes_combo.setCurrentText("Gauss linear")
    
    # Generate fvSchemes
    interface._update_fv_schemes()
    
    # Verify file exists and is valid
    fv_schemes_path = os.path.join(interface.case_path, "system", "fvSchemes")
    assert os.path.exists(fv_schemes_path)
    
    # Verify content
    with open(fv_schemes_path, 'r') as f:
        content = f.read()
        assert "ddtSchemes" in content
        assert "default         Euler" in content
```

---

#### Task 2.4: Connect UI Inputs to controlDict
**Duration**: 2 hours
**Priority**: HIGH

**Objectives**:
- Map UI control parameters to controlDict
- Implement simulation control parameter validation
- Generate valid OpenFOAM controlDict files

**Detailed Steps**:

1. **Parameter Mapping** (1 hour):
   ```python
   def _update_control_dict(self):
       """Update controlDict with current UI parameters."""
       try:
           # Get control parameters from UI
           end_time = float(self.end_time_edit.value())
           delta_t = float(self.delta_t_edit.value())
           write_interval = float(self.write_interval_edit.value())
           
           # Generate controlDict content
           content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
   =========                 |
   \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
   \\  /    A nd           | Version:  6
   \\/     M anipulation  |
   \\*---------------------------------------------------------------------------*/
   FoamFile
   {{
       version     2.0;
       format      ascii;
       class       dictionary;
       object      controlDict;
   }}
   // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
   
   application     SPMFoam_OF6;
   
   startFrom       startTime;
   
   startTime       0;
   
   stopAt          endTime;
   
   endTime         {end_time};
   
   deltaT          {delta_t};
   
   writeControl    time;
   
   writeInterval   {write_interval};
   
   purgeWrite      0;
   
   writeFormat     ascii;
   
   writePrecision  6;
   
   writeCompression off;
   
   timeFormat      general;
   
   timePrecision   6;
   
   runTimeModifiable true;
   
   functions
   {{
       probes
       {{
           type            probes;
           functionObjectLibs ("libsampling.so");
           outputControl   time;
           outputInterval  1;
           probeLocations
           (
               (0 0 0)
           );
           fields
           (
               cs
           );
       }}
   }}
   
   // ************************************************************************* //
   """
           
           # Write to file
           control_dict_path = os.path.join(self.case_path, "system", "controlDict")
           with open(control_dict_path, 'w') as f:
               f.write(content)
               
           logger.info("controlDict updated successfully")
           
       except Exception as e:
           logger.error(f"Failed to update controlDict: {e}")
           raise
   ```

2. **Control Parameter Validation** (0.5 hour):
   ```python
   def _validate_control_parameters(self):
       """Validate control parameters."""
       errors = []
       
       try:
           end_time = float(self.end_time_edit.value())
           delta_t = float(self.delta_t_edit.value())
           write_interval = float(self.write_interval_edit.value())
           tolerance = float(self.tolerance_edit.text())
           
           # Validate time parameters
           if end_time <= 0:
               errors.append("End time must be positive")
           if delta_t <= 0:
               errors.append("Delta T must be positive")
           if write_interval <= 0:
               errors.append("Write interval must be positive")
           
           # Validate tolerance
           if not (1e-12 <= tolerance <= 1e-3):
               errors.append("Tolerance should be between 1e-12 and 1e-3")
           
           # Check consistency
           if delta_t > end_time:
               errors.append("Delta T should be smaller than end time")
           if write_interval > end_time:
               errors.append("Write interval should be smaller than end time")
               
       except ValueError as e:
           errors.append(f"Invalid numeric value: {e}")
       
       return errors
   ```

3. **Integration with UI** (0.5 hour):
   ```python
   def _on_control_changed(self):
       """Handle control parameter changes."""
       # Validate parameters
       errors = self._validate_control_parameters()
       
       if errors:
           # Show validation errors
           error_msg = "\n".join(errors)
           self._show_validation_error("Control Validation Error", error_msg)
           return
       
       # Update controlDict
       try:
           self._update_control_dict()
           self._show_status_message("Control parameters updated successfully")
       except Exception as e:
           self._show_error_message(f"Failed to update control parameters: {e}")
   ```

**Success Criteria**:
- ✅ UI parameters correctly mapped to controlDict
- ✅ Control parameter validation works
- ✅ Generated controlDict is syntactically correct
- ✅ Simulation parameters are consistent

**Validation Tests**:
```python
def test_control_dict_generation():
    interface = CarbonInterface()
    
    # Set control parameters
    interface.end_time_edit.setValue(10.0)
    interface.delta_t_edit.setValue(0.1)
    interface.write_interval_edit.setValue(1.0)
    
    # Generate controlDict
    interface._update_control_dict()
    
    # Verify file exists and is valid
    control_dict_path = os.path.join(interface.case_path, "system", "controlDict")
    assert os.path.exists(control_dict_path)
    
    # Verify content
    with open(control_dict_path, 'r') as f:
        content = f.read()
        assert "endTime         10" in content
        assert "deltaT          0.1" in content
        assert "application     SPMFoam_OF6" in content
```

---

### Phase 3: OpenFOAM Execution (Day 3)

#### Task 3.1: Implement "Run Simulation" Button
**Duration**: 3 hours
**Priority**: HIGH

**Objectives**:
- Create comprehensive simulation workflow
- Implement proper sequence of OpenFOAM commands
- Handle simulation execution and monitoring

**Detailed Steps**:

1. **Simulation Workflow** (1.5 hours):
   ```python
   def _on_run_clicked(self):
       """Handle simulation start."""
       try:
           # Validate all parameters
           if not self._validate_all_parameters():
               return
           
           # Check if case path is set
           if not self.case_path:
               self._show_error_message("Case path not set. Please create a project first.")
               return
           
           # Check if OpenFOAM is available
           if not self._check_openfoam_availability():
               return
           
           # Generate all OpenFOAM files
           self._generate_all_openfoam_files()
           
           # Start simulation workflow
           self._start_simulation_workflow()
           
       except Exception as e:
           logger.error(f"Failed to start simulation: {e}", exc_info=True)
           self._show_critical_error(f"Failed to start simulation: {e}")
   
   def _validate_all_parameters(self):
       """Validate all simulation parameters."""
       errors = []
       
       # Validate geometry
       errors.extend(self._validate_geometry_parameters())
       
       # Validate material properties
       errors.extend(self._validate_material_parameters())
       
       # Validate control parameters
       errors.extend(self._validate_control_parameters())
       
       if errors:
           error_msg = "\n".join(errors)
           self._show_validation_error("Parameter Validation Error", error_msg)
           return False
       
       return True
   
   def _generate_all_openfoam_files(self):
       """Generate all required OpenFOAM configuration files."""
       # Update all configuration files
       self._update_block_mesh_dict()
       self._update_li_properties()
       self._update_fv_schemes()
       self._update_fv_solution()
       self._update_control_dict()
       
       # Update topoSetDict for particle region
       self._update_topo_set_dict()
       
       self._show_status_message("All OpenFOAM configuration files updated")
   
   def _start_simulation_workflow(self):
       """Start the complete simulation workflow."""
       # Define workflow steps
       workflow_steps = [
           ("Running blockMesh", self._run_block_mesh),
           ("Running topoSet", self._run_topo_set),
           ("Running splitMeshRegions", self._run_split_mesh_regions),
           ("Compiling SPMFoam solver", self._compile_solver),
           ("Running SPMFoam simulation", self._run_spm_foam)
       ]
       
       # Execute workflow
       self._execute_workflow(workflow_steps)
   ```

2. **OpenFOAM Command Execution** (1 hour):
   ```python
   def _run_block_mesh(self):
       """Run blockMesh command."""
       command = "blockMesh"
       return self._execute_openfoam_command(command)
   
   def _run_topo_set(self):
       """Run topoSet command."""
       command = "topoSet"
       return self._execute_openfoam_command(command)
   
   def _run_split_mesh_regions(self):
       """Run splitMeshRegions command."""
       command = "splitMeshRegions -cellZones -overwrite"
       return self._execute_openfoam_command(command)
   
   def _compile_solver(self):
       """Compile SPMFoam solver."""
       solver_path = os.path.join(self.solver_path, "SPMFoam_OF6")
       commands = [
           f"cd {solver_path} && wclean",
           "wmake"
       ]
       
       for command in commands:
           result = self._execute_openfoam_command(command)
           if result != 0:
               return result
       
       return 0
   
   def _run_spm_foam(self):
       """Run SPMFoam simulation."""
       command = f"cd {self.case_path} && SPMFoam_OF6"
       return self._execute_openfoam_command(command)
   
   def _execute_openfoam_command(self, command):
       """Execute OpenFOAM command with proper error handling."""
       try:
           logger.info(f"Executing: {command}")
           
           # Use MSYS2 executor for Windows
           if sys.platform == "win32":
               from src.openfoam.msys2_executor import get_executor
               executor = get_executor()
               
               return_code = executor.execute_command_with_callback(
                   command,
                   self.case_path,
                   self._on_process_output,
                   self._on_process_error
               )
           else:
               # Use subprocess for Linux/macOS
               import subprocess
               result = subprocess.run(
                   command,
                   shell=True,
                   cwd=self.case_path,
                   capture_output=True,
                   text=True
               )
               return_code = result.returncode
               
               # Display output
               if result.stdout:
                   self._on_process_output(result.stdout)
               if result.stderr:
                   self._on_process_error(result.stderr)
           
           return return_code
           
       except Exception as e:
           logger.error(f"Command execution failed: {e}")
           self._on_process_error(f"Command failed: {e}")
           return -1
   ```

3. **Workflow Management** (0.5 hour):
   ```python
   def _execute_workflow(self, steps):
       """Execute workflow steps sequentially."""
       self.simulation_running = True
       self._update_control_buttons()
       
       # Execute steps sequentially
       for step_name, step_function in steps:
           self._show_status_message(f"Step: {step_name}")
           
           try:
               result = step_function()
               
               if result != 0:
                   self._show_error_message(f"Step failed: {step_name}")
                   self.simulation_running = False
                   self._update_control_buttons()
                   return
               
               self._show_status_message(f"Step completed: {step_name}")
               
           except Exception as e:
               logger.error(f"Step failed: {step_name} - {e}")
               self._show_error_message(f"Step failed: {step_name} - {e}")
               self.simulation_running = False
               self._update_control_buttons()
               return
       
       # Workflow completed successfully
       self.simulation_running = False
       self._update_control_buttons()
       self._show_status_message("Simulation completed successfully!")
   ```

**Success Criteria**:
- ✅ Complete simulation workflow implemented
- ✅ All OpenFOAM commands execute in correct sequence
- ✅ Error handling for each workflow step
- ✅ Progress reporting and status updates

**Validation Tests**:
```python
def test_simulation_workflow():
    interface = CarbonInterface()
    
    # Set up test case
    interface.case_path = "/test/case/path"
    interface.solver_path = "/test/solver/path"
    
    # Mock process controller
    interface.process_controller = Mock()
    
    # Test workflow execution
    result = interface._execute_workflow([
        ("Test step", lambda: 0)
    ])
    
    # Verify workflow completed
    assert result is None  # Success case
```

---

#### Task 3.2: Process Control Implementation
**Duration**: 2 hours
**Priority**: HIGH

**Objectives**:
- Implement start/stop/pause functionality
- Add real-time process monitoring
- Handle process lifecycle properly

**Detailed Steps**:

1. **Process Control Integration** (1 hour):
   ```python
   def _on_run_clicked(self):
       """Handle simulation start with process control."""
       try:
           # Validate and prepare
           if not self._validate_and_prepare_simulation():
               return
           
           # Start process with ProcessController
           command = f"cd {self.case_path} && SPMFoam_OF6"
           
           if self.process_controller:
               self.process_controller.start_process(command, self.case_path)
               self.simulation_started.emit()
               self._show_status_message("Simulation started")
           else:
               # Fallback to direct execution
               self._execute_openfoam_command(command)
               
       except Exception as e:
           logger.error(f"Failed to start simulation: {e}", exc_info=True)
           self._show_critical_error(f"Failed to start simulation: {e}")
   
   def _on_stop_clicked(self):
       """Handle simulation stop."""
       try:
           if self.process_controller and self.process_controller.is_running():
               self.process_controller.terminate_process()
               self._show_status_message("Simulation stopped")
               self.simulation_stopped.emit()
           else:
               self._show_warning("No simulation running")
               
       except Exception as e:
           logger.error(f"Failed to stop simulation: {e}", exc_info=True)
           self._show_error_message(f"Failed to stop simulation: {e}")
   
   def _on_pause_clicked(self):
       """Handle simulation pause/resume."""
       try:
           if not self.process_controller or not self.process_controller.is_running():
               self._show_warning("No simulation running")
               return
           
           if self.simulation_paused:
               # Resume
               self.process_controller.resume_process()
               self.simulation_paused = False
               self._show_status_message("Simulation resumed")
               self.simulation_resumed.emit()
           else:
               # Pause
               self.process_controller.pause_process()
               self.simulation_paused = True
               self._show_status_message("Simulation paused")
               self.simulation_paused.emit()
               
       except Exception as e:
           logger.error(f"Failed to pause/resume simulation: {e}", exc_info=True)
           self._show_error_message(f"Failed to pause/resume simulation: {e}")
   ```

2. **Process Monitoring** (1 hour):
   ```python
   def _connect_process_signals(self):
       """Connect process controller signals."""
       if self.process_controller:
           self.process_controller.output_received.connect(self._on_process_output)
           self.process_controller.error_received.connect(self._on_process_error)
           self.process_controller.process_started.connect(self._on_process_started)
           self.process_controller.process_finished.connect(self._on_process_finished)
   
   def _on_process_output(self, output):
       """Handle process output."""
       if self.terminal_output:
           self.terminal_output.append(output)
           self.output_received.emit(output)
           
           # Limit output buffer size
           cursor = self.terminal_output.textCursor()
           block_count = cursor.blockNumber() + 1
           if block_count > 1000:
               self.terminal_output.clear()
               self.terminal_output.append("... Output truncated to prevent memory issues ...")
               self.terminal_output.append(output)
   
   def _on_process_error(self, error):
       """Handle process errors."""
       if self.terminal_output:
           self.terminal_output.append(f"ERROR: {error}")
           self.error_received.emit(error)
   
   def _on_process_started(self):
       """Handle process start."""
       self.simulation_running = True
       self.simulation_paused = False
       self._update_control_buttons()
       self._show_status_message("Process started")
   
   def _on_process_finished(self, exit_code):
       """Handle process completion."""
       self.simulation_running = False
       self._update_control_buttons()
       
       if exit_code == 0:
           self._show_status_message("Process completed successfully")
       else:
           self._show_error_message(f"Process failed with exit code: {exit_code}")
   ```

**Success Criteria**:
- ✅ Start/stop/pause functionality works
- ✅ Real-time process monitoring
- ✅ Proper process lifecycle handling
- ✅ Signal emission for process events

**Validation Tests**:
```python
def test_process_control():
    interface = CarbonInterface()
    
    # Mock process controller
    mock_controller = Mock()
    interface.process_controller = mock_controller
    
    # Test start
    interface._on_run_clicked()
    mock_controller.start_process.assert_called_once()
    
    # Test stop
    mock_controller.is_running.return_value = True
    interface._on_stop_clicked()
    mock_controller.terminate_process.assert_called_once()
```

---

### Phase 4: Output Monitoring (Day 4)

#### Task 4.1: Real-time Terminal Output Display
**Duration**: 2 hours
**Priority**: HIGH

**Objectives**:
- Display real-time simulation output
- Implement output filtering and formatting
- Add search and navigation features

**Detailed Steps**:

1. **Terminal Widget Enhancement** (1 hour):
   ```python
   def _setup_terminal_widget(self):
       """Enhance terminal widget with additional features."""
       # Create terminal widget
       self.terminal_output = QTextEdit()
       self.terminal_output.setReadOnly(True)
       self.terminal_output.setFont(QFont("Courier", 10))
       
       # Add search functionality
       search_layout = QHBoxLayout()
       self.search_edit = QLineEdit()
       self.search_edit.setPlaceholderText("Search output...")
       self.search_edit.textChanged.connect(self._on_search_text_changed)
       
       self.search_next_button = QPushButton("Next")
       self.search_next_button.clicked.connect(self._on_search_next)
       
       self.search_prev_button = QPushButton("Previous")
       self.search_prev_button.clicked.connect(self._on_search_previous)
       
       search_layout.addWidget(self.search_edit)
       search_layout.addWidget(self.search_next_button)
       search_layout.addWidget(self.search_prev_button)
       
       # Add clear button
       self.clear_output_button = QPushButton("Clear Output")
       self.clear_output_button.clicked.connect(self._on_clear_output)
       
       # Add to terminal layout
       terminal_layout = QVBoxLayout()
       terminal_layout.addLayout(search_layout)
       terminal_layout.addWidget(self.terminal_output)
       terminal_layout.addWidget(self.clear_output_button)
       
       return terminal_layout
   
   def _on_search_text_changed(self, text):
       """Handle search text changes."""
       if text:
           # Highlight search terms
           self._highlight_search_terms(text)
       else:
           # Clear highlighting
           self._clear_search_highlighting()
   
   def _highlight_search_terms(self, text):
       """Highlight search terms in terminal output."""
       # Implementation for highlighting search terms
       # This could use QTextEdit's find functionality
       pass
   
   def _on_clear_output(self):
       """Clear terminal output."""
       self.terminal_output.clear()
   ```

2. **Output Formatting** (0.5 hour):
   ```python
   def _on_process_output(self, output):
       """Handle process output with formatting."""
       # Format output
       formatted_output = self._format_output(output)
       
       # Add timestamp
       timestamp = datetime.now().strftime("%H:%M:%S")
       display_text = f"[{timestamp}] {formatted_output}"
       
       # Add to terminal
       self.terminal_output.append(display_text)
       
       # Emit signal
       self.output_received.emit(formatted_output)
       
       # Auto-scroll to bottom
       self.terminal_output.moveCursor(QTextCursor.MoveOperation.End)
   
   def _format_output(self, output):
       """Format output for better readability."""
       # Remove excessive whitespace
       formatted = ' '.join(output.split())
       
       # Add color coding for different types of messages
       if "ERROR" in formatted:
           formatted = f"<span style='color: red;'>{formatted}</span>"
       elif "WARNING" in formatted:
           formatted = f"<span style='color: orange;'>{formatted}</span>"
       elif "SUCCESS" in formatted:
           formatted = f"<span style='color: green;'>{formatted}</span>"
       
       return formatted
   ```

3. **Output Filtering** (0.5 hour):
   ```python
   def _setup_output_filters(self):
       """Set up output filtering options."""
       filter_layout = QHBoxLayout()
       
       # Filter checkboxes
       self.show_errors_checkbox = QCheckBox("Show Errors")
       self.show_warnings_checkbox = QCheckBox("Show Warnings")
       self.show_info_checkbox = QCheckBox("Show Info")
       
       self.show_errors_checkbox.setChecked(True)
       self.show_warnings_checkbox.setChecked(True)
       self.show_info_checkbox.setChecked(True)
       
       self.show_errors_checkbox.stateChanged.connect(self._on_filter_changed)
       self.show_warnings_checkbox.stateChanged.connect(self._on_filter_changed)
       self.show_info_checkbox.stateChanged.connect(self._on_filter_changed)
       
       filter_layout.addWidget(self.show_errors_checkbox)
       filter_layout.addWidget(self.show_warnings_checkbox)
       filter_layout.addWidget(self.show_info_checkbox)
       
       return filter_layout
   
   def _on_filter_changed(self):
       """Handle filter changes."""
       # Re-display output based on current filters
       self._apply_output_filters()
   
   def _apply_output_filters(self):
       """Apply current filters to displayed output."""
       # Get current output
       current_output = self.terminal_output.toPlainText()
       
       # Clear and re-display based on filters
       self.terminal_output.clear()
       
       lines = current_output.split('\n')
       for line in lines:
           if self._should_show_line(line):
               self.terminal_output.append(line)
   
   def _should_show_line(self, line):
       """Determine if line should be shown based on filters."""
       if "ERROR" in line and not self.show_errors_checkbox.isChecked():
           return False
       if "WARNING" in line and not self.show_warnings_checkbox.isChecked():
           return False
       if "INFO" in line and not self.show_info_checkbox.isChecked():
           return False
       
       return True
   ```

**Success Criteria**:
- ✅ Real-time output display works
- ✅ Search functionality implemented
- ✅ Output filtering works correctly
- ✅ Auto-scroll and formatting features work

**Validation Tests**:
```python
def test_terminal_output():
    interface = CarbonInterface()
    
    # Test output display
    test_output = "Test output message"
    interface._on_process_output(test_output)
    
    # Verify output appears in terminal
    assert test_output in interface.terminal_output.toPlainText()
```

---

#### Task 4.2: Error Detection and Reporting
**Duration**: 2 hours
**Priority**: HIGH

**Objectives**:
- Detect common OpenFOAM errors
- Provide user-friendly error messages
- Suggest solutions for common issues
- Log errors for debugging

**Detailed Steps**:

1. **Error Pattern Detection** (1 hour):
   ```python
   # Error patterns for OpenFOAM
   ERROR_PATTERNS = {
       "mesh_error": {
           "pattern": r"Mesh is not valid",
           "message": "Mesh generation failed. Check geometry parameters.",
           "solution": "Verify that geometry dimensions and divisions are valid."
       },
       "solver_error": {
           "pattern": r"Solver diverged",
           "message": "Simulation diverged. Check solver settings.",
           "solution": "Try reducing timestep or adjusting solver tolerance."
       },
       "file_error": {
           "pattern": r"Cannot open file",
           "message": "Required file not found.",
           "solution": "Ensure all OpenFOAM configuration files are generated."
       },
       "convergence_error": {
           "pattern": r"Maximum number of iterations",
           "message": "Solution did not converge.",
           "solution": "Check boundary conditions and initial values."
       },
       "memory_error": {
           "pattern": r"Out of memory",
           "message": "Insufficient memory for simulation.",
           "solution": "Reduce mesh resolution or increase system memory."
       }
   }
   
   def _on_process_error(self, error):
       """Handle process errors with pattern detection."""
       # Display error
       self.terminal_output.append(f"ERROR: {error}")
       
       # Detect error pattern
       error_info = self._detect_error_pattern(error)
       
       if error_info:
           # Show user-friendly error message
           self._show_error_dialog(error_info["message"], error_info["solution"])
       
       # Log error
       logger.error(f"Process error: {error}")
       
       # Emit error signal
       self.error_received.emit(error)
   
   def _detect_error_pattern(self, error_text):
       """Detect error pattern and return appropriate message."""
       for error_type, pattern_info in self.ERROR_PATTERNS.items():
           if re.search(pattern_info["pattern"], error_text, re.IGNORECASE):
               return pattern_info
       
       # Default error handling
       return {
           "message": "An unknown error occurred.",
           "solution": "Check the terminal output for more details."
       }
   ```

2. **User-Friendly Error Dialogs** (0.5 hour):
   ```python
   def _show_error_dialog(self, message, solution):
       """Show user-friendly error dialog."""
       dialog = QDialog(self)
       dialog.setWindowTitle("Simulation Error")
       dialog.setModal(True)
       dialog.resize(500, 300)
       
       layout = QVBoxLayout()
       
       # Error message
       error_label = QLabel(message)
       error_label.setWordWrap(True)
       error_label.setStyleSheet("color: red; font-weight: bold;")
       layout.addWidget(error_label)
       
       # Solution
       solution_label = QLabel(f"Solution: {solution}")
       solution_label.setWordWrap(True)
       layout.addWidget(solution_label)
       
       # Details button
       details_button = QPushButton("Show Details")
       details_button.clicked.connect(lambda: self._show_error_details(dialog))
       layout.addWidget(details_button)
       
       # OK button
       ok_button = QPushButton("OK")
       ok_button.clicked.connect(dialog.accept)
       layout.addWidget(ok_button)
       
       dialog.setLayout(layout)
       dialog.exec()
   
   def _show_error_details(self, parent_dialog):
       """Show detailed error information."""
       details_dialog = QDialog(parent_dialog)
       details_dialog.setWindowTitle("Error Details")
       details_dialog.resize(600, 400)
       
       layout = QVBoxLayout()
       
       # Show recent terminal output
       terminal_text = self.terminal_output.toPlainText()
       recent_output = '\n'.join(terminal_text.split('\n')[-50:])
       
       details_text = QTextEdit()
       details_text.setPlainText(recent_output)
       details_text.setReadOnly(True)
       layout.addWidget(details_text)
       
       # Close button
       close_button = QPushButton("Close")
       close_button.clicked.connect(details_dialog.accept)
       layout.addWidget(close_button)
       
       details_dialog.setLayout(layout)
       details_dialog.exec()
   ```

3. **Error Logging and Reporting** (0.5 hour):
   ```python
   def _log_error_details(self, error_info):
       """Log detailed error information."""
       error_log = {
           "timestamp": datetime.now().isoformat(),
           "error_type": error_info.get("type", "unknown"),
           "error_message": error_info.get("message", ""),
           "solution": error_info.get("solution", ""),
           "parameters": self._get_current_parameters(),
           "system_info": self._get_system_info()
       }
       
       # Save to error log file
       error_log_path = os.path.join(self.case_path, "error_log.json")
       try:
           if os.path.exists(error_log_path):
               with open(error_log_path, 'r') as f:
                   logs = json.load(f)
           else:
               logs = []
           
           logs.append(error_log)
           
           with open(error_log_path, 'w') as f:
               json.dump(logs, f, indent=2)
               
       except Exception as e:
           logger.error(f"Failed to save error log: {e}")
   
   def _get_current_parameters(self):
       """Get current simulation parameters for error reporting."""
       return {
           "geometry": {
               "length": self.length_edit.text(),
               "width": self.width_edit.text(),
               "height": self.height_edit.text(),
               "radius": self.radius_edit.text(),
               "divisions": {
                   "x": self.x_div_edit.value(),
                   "y": self.y_div_edit.value(),
                   "z": self.z_div_edit.value()
               }
           },
           "material": {
               "ds_value": self.param_edits["DS_value"].text(),
               "cs_max": self.param_edits["CS_max"].text(),
               "k_react": self.param_edits["kReact"].text()
           },
           "control": {
               "end_time": self.end_time_edit.value(),
               "delta_t": self.delta_t_edit.value(),
               "tolerance": self.tolerance_edit.text()
           }
       }
   
   def _get_system_info(self):
       """Get system information for error reporting."""
       import platform
       import sys
       
       return {
           "platform": platform.platform(),
           "python_version": sys.version,
           "openfoam_version": self._get_openfoam_version(),
           "working_directory": os.getcwd()
       }
   ```

**Success Criteria**:
- ✅ Error pattern detection works
- ✅ User-friendly error messages displayed
- ✅ Error solutions provided
- ✅ Error logging implemented
- ✅ System information captured

**Validation Tests**:
```python
def test_error_detection():
    interface = CarbonInterface()
    
    # Test mesh error detection
    mesh_error = "Mesh is not valid"
    error_info = interface._detect_error_pattern(mesh_error)
    assert error_info["message"] == "Mesh generation failed. Check geometry parameters."
    
    # Test solver error detection
    solver_error = "Solver diverged"
    error_info = interface._detect_error_pattern(solver_error)
    assert error_info["message"] == "Simulation diverged. Check solver settings."
```

---

#### Task 4.3: Simulation Progress Tracking
**Duration**: 2 hours
**Priority**: MEDIUM

**Objectives**:
- Track simulation progress in real-time
- Display progress indicators
- Estimate time to completion
- Monitor simulation health

**Detailed Steps**:

1. **Progress Tracking** (1 hour):
   ```python
   def _setup_progress_tracking(self):
       """Set up simulation progress tracking."""
       # Progress bar
       self.progress_bar = QProgressBar()
       self.progress_bar.setMinimum(0)
       self.progress_bar.setMaximum(100)
       self.progress_bar.setValue(0)
       
       # Progress labels
       self.progress_label = QLabel("Simulation progress: 0%")
       self.time_remaining_label = QLabel("Time remaining: --:--:--")
       
       # Progress tracking variables
       self.simulation_start_time = None
       self.last_progress_update = None
       self.progress_history = []
       
       return self.progress_bar, self.progress_label, self.time_remaining_label
   
   def _on_process_output(self, output):
       """Handle process output and update progress."""
       # Call parent method for display
       super()._on_process_output(output)
       
       # Update progress based on output
       self._update_simulation_progress(output)
   
   def _update_simulation_progress(self, output):
       """Update simulation progress based on output."""
       # Parse OpenFOAM output for time information
       time_match = re.search(r"Time = ([0-9.e-]+)", output)
       if time_match:
           current_time = float(time_match.group(1))
           
           # Get end time from controlDict
           end_time = float(self.end_time_edit.value())
           
           # Calculate progress
           if end_time > 0:
               progress = min(100, int((current_time / end_time) * 100))
               
               # Update progress bar
               self.progress_bar.setValue(progress)
               self.progress_label.setText(f"Simulation progress: {progress}%")
               
               # Update time remaining
               self._update_time_remaining(current_time, end_time, progress)
               
               # Store progress history
               self.progress_history.append({
                   'time': current_time,
                   'progress': progress,
                   'timestamp': time.time()
               })
       
       # Parse for iteration information
       iter_match = re.search(r"Iterations: ([0-9]+)", output)
       if iter_match:
           iterations = int(iter_match.group(1))
           self._update_iteration_info(iterations)
   
   def _update_time_remaining(self, current_time, end_time, progress):
       """Estimate time remaining for simulation."""
       if progress > 0 and self.simulation_start_time:
           # Calculate elapsed time
           elapsed = time.time() - self.simulation_start_time
           
           # Estimate total time
           estimated_total = elapsed / (progress / 100.0)
           
           # Calculate remaining time
           remaining = estimated_total - elapsed
           
           # Format remaining time
           if remaining > 0:
               hours = int(remaining // 3600)
               minutes = int((remaining % 3600) // 60)
               seconds = int(remaining % 60)
               
               time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
               self.time_remaining_label.setText(f"Time remaining: {time_str}")
   ```

2. **Simulation Health Monitoring** (0.5 hour):
   ```python
   def _setup_health_monitoring(self):
       """Set up simulation health monitoring."""
       # Health status indicators
       self.health_status = QLabel("Health: Good")
       self.health_status.setStyleSheet("color: green; font-weight: bold;")
       
       # Health monitoring variables
       self.last_output_time = time.time()
       self.output_stalled = False
       self.error_count = 0
       
       # Start health monitoring timer
       self.health_timer = QTimer()
       self.health_timer.timeout.connect(self._check_simulation_health)
       self.health_timer.start(5000)  # Check every 5 seconds
   
   def _check_simulation_health(self):
       """Check simulation health and update status."""
       current_time = time.time()
       
       # Check for output stall
       if current_time - self.last_output_time > 60:  # No output for 60 seconds
           if not self.output_stalled:
               self.output_stalled = True
               self._update_health_status("Warning: No output for 60 seconds", "orange")
       
       # Check error count
       if self.error_count > 5:
           self._update_health_status("Critical: High error count", "red")
       
       # Check if process is still running
       if self.process_controller and not self.process_controller.is_running():
           if self.simulation_running:
               self._update_health_status("Error: Process stopped unexpectedly", "red")
   
   def _update_health_status(self, message, color):
       """Update health status display."""
       self.health_status.setText(f"Health: {message}")
       self.health_status.setStyleSheet(f"color: {color}; font-weight: bold;")
       
       # Log health warning
       logger.warning(f"Health warning: {message}")
   
   def _on_process_output(self, output):
       """Handle process output and update health monitoring."""
       # Update last output time
       self.last_output_time = time.time()
       self.output_stalled = False
       
       # Check for error indicators
       if "ERROR" in output or "error" in output:
           self.error_count += 1
       
       # Update health status if recovered
       if self.error_count <= 2 and self.output_stalled:
           self._update_health_status("Good", "green")
   ```

3. **Progress Visualization** (0.5 hour):
   ```python
   def _setup_progress_visualization(self):
       """Set up progress visualization with charts."""
       # Use pyqtgraph for real-time plotting
       try:
           import pyqtgraph as pg
           
           # Time vs Progress plot
           self.progress_plot = pg.PlotWidget()
           self.progress_plot.setTitle("Simulation Progress")
           self.progress_plot.setLabel('left', 'Progress (%)')
           self.progress_plot.setLabel('bottom', 'Time')
           
           # Iterations vs Time plot
           self.iteration_plot = pg.PlotWidget()
           self.iteration_plot.setTitle("Iterations")
           self.iteration_plot.setLabel('left', 'Iterations')
           self.iteration_plot.setLabel('bottom', 'Time')
           
           return [self.progress_plot, self.iteration_plot]
           
       except ImportError:
           logger.warning("pyqtgraph not available, skipping progress visualization")
           return []
   
   def _update_progress_plots(self, current_time, progress, iterations=None):
       """Update progress visualization plots."""
       try:
           import pyqtgraph as pg
           
           # Update progress plot
           if hasattr(self, 'progress_plot'):
               # Get existing data
               current_data = self.progress_plot.getPlotItem().listDataItems()[0].yData
               if current_data is None:
                   current_data = []
               
               # Add new data point
               current_data.append(progress)
               
               # Update plot
               self.progress_plot.clear()
               self.progress_plot.plot(current_data, pen='b')
           
           # Update iteration plot
           if iterations is not None and hasattr(self, 'iteration_plot'):
               current_iter_data = self.iteration_plot.getPlotItem().listDataItems()[0].yData
               if current_iter_data is None:
                   current_iter_data = []
               
               current_iter_data.append(iterations)
               
               self.iteration_plot.clear()
               self.iteration_plot.plot(current_iter_data, pen='r')
               
       except ImportError:
           pass  # Skip if pyqtgraph not available
   ```

**Success Criteria**:
- ✅ Progress tracking works in real-time
- ✅ Progress bar updates correctly
- ✅ Time remaining estimation works
- ✅ Health monitoring detects issues
- ✅ Progress visualization displays correctly

**Validation Tests**:
```python
def test_progress_tracking():
    interface = CarbonInterface()
    
    # Mock progress update
    test_output = "Time = 5.0"
    interface._update_simulation_progress(test_output)
    
    # Verify progress bar updated
    assert interface.progress_bar.value() > 0
    assert "Simulation progress: " in interface.progress_label.text()
```

---

## Implementation Timeline

### Week 1: Implementation Schedule

**Day 1 (Monday)**: Signal Connection Completion
- Morning: Geometry and Constants tab signals
- Afternoon: Boundary, Functions, and Control tab signals
- Evening: Testing and validation

**Day 2 (Tuesday)**: Parameter Integration
- Morning: blockMeshDict integration
- Afternoon: LiProperties integration
- Evening: fvSchemes/fvSolution integration

**Day 3 (Wednesday)**: OpenFOAM Execution
- Morning: Run simulation workflow
- Afternoon: Process control implementation
- Evening: Testing and debugging

**Day 4 (Thursday)**: Output Monitoring
- Morning: Real-time terminal output
- Afternoon: Error detection and reporting
- Evening: Progress tracking implementation

**Day 5 (Friday)**: Integration and Testing
- Morning: End-to-end testing
- Afternoon: Bug fixes and optimization
- Evening: Documentation and final validation

### Resource Allocation

- **Senior Developer**: 40 hours (implementation)
- **QA Engineer**: 16 hours (testing)
- **DevOps Engineer**: 8 hours (environment setup)

### Budget Estimate

- **Development**: $12,800 (40 hours × $320/hour)
- **QA/Testing**: $6,400 (16 hours × $400/hour)
- **DevOps**: $3,200 (8 hours × $400/hour)
- **Total**: $22,400

## Success Criteria

### Technical Success Criteria

1. **Signal Connections**: All UI widgets properly connected to slots
2. **Parameter Integration**: All UI inputs correctly mapped to OpenFOAM files
3. **OpenFOAM Execution**: Complete workflow executes successfully
4. **Output Monitoring**: Real-time monitoring and error detection works
5. **Process Control**: Start/stop/pause functionality works correctly

### Functional Success Criteria

1. **End-to-End Simulation**: SPM simulation runs completely on Windows
2. **User Experience**: Intuitive interface with clear feedback
3. **Error Handling**: Comprehensive error detection and user-friendly messages
4. **Performance**: Simulation executes within reasonable time
5. **Reliability**: Consistent execution without crashes

### Validation Tests

```python
def test_complete_spm_workflow():
    """Test complete SPM simulation workflow."""
    # Create interface
    interface = CarbonInterface()
    
    # Set parameters
    interface.length_edit.setText("100")
    interface.width_edit.setText("100")
    interface.height_edit.setText("100")
    interface.radius_edit.setText("50")
    interface.param_edits["DS_value"].setText("1e-14")
    interface.param_edits["CS_max"].setText("30000")
    interface.end_time_edit.setValue(10.0)
    interface.delta_t_edit.setValue(0.1)
    
    # Generate files
    interface._generate_all_openfoam_files()
    
    # Verify files created
    assert os.path.exists(os.path.join(interface.case_path, "system", "blockMeshDict"))
    assert os.path.exists(os.path.join(interface.case_path, "constant", "LiProperties"))
    assert os.path.exists(os.path.join(interface.case_path, "system", "fvSchemes"))
    assert os.path.exists(os.path.join(interface.case_path, "system", "fvSolution"))
    assert os.path.exists(os.path.join(interface.case_path, "system", "controlDict"))
    
    # Test simulation start
    # (This would require actual OpenFOAM installation for full test)
    print("SPM workflow test completed successfully!")
```

## Risk Mitigation

### High Risk: OpenFOAM Integration
**Risk**: OpenFOAM commands fail to execute properly
**Mitigation**:
- Test with minimal OpenFOAM installation
- Implement comprehensive error handling
- Provide fallback mechanisms
- Create detailed troubleshooting guide

### Medium Risk: Windows Compatibility
**Risk**: MSYS2 integration issues on Windows
**Mitigation**:
- Test on multiple Windows versions
- Implement path conversion utilities
- Create Windows-specific documentation
- Provide alternative execution methods

### Low Risk: Performance Issues
**Risk**: Large simulations cause performance problems
**Mitigation**:
- Implement progress indicators
- Add simulation cancellation
- Optimize file generation
- Provide memory usage monitoring

## Conclusion

This implementation plan provides a detailed roadmap for completing the Carbon/SPM interface to achieve a fully working end-to-end simulation on Windows. The plan is structured to be completed in 5 days with clear milestones, success criteria, and validation tests.

### Key Success Factors
1. **Strong Implementation**: Follow the detailed code examples
2. **Comprehensive Testing**: Validate each component thoroughly
3. **User Focus**: Ensure intuitive interface and clear feedback
4. **Quality Assurance**: Rigorous testing and validation
5. **Documentation**: Clear implementation and user guides

With proper execution, the Carbon/SPM interface will be fully functional with complete end-to-end simulation capability on Windows.

---

**Document Version**: 1.0
**Created**: December 2025
**Next Review**: Implementation Start
**Owner**: Project Architect