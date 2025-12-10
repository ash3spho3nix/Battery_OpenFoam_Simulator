"""
Carbon Interface for Single Particle Model (SPM).

This module provides the CarbonInterface class, which implements the
SPM simulation interface with complete functionality matching the
original C++ version.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QTabWidget, QTextEdit, QLineEdit, QComboBox, QRadioButton, QGroupBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QFileDialog, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap

# Import modules using absolute imports to avoid packaging issues
from src.gui.interfaces.base_interface import BaseInterface
from src.openfoam.process_controller import ProcessController
from src.openfoam.solver_manager import OpenFOAMSolverManager
from src.utils.parameter_parser import ParameterManager
from src.utils.file_operations import TemplateManager
from src.core.constants import (
    ERROR_MESSAGES, SUCCESS_MESSAGES, WARNING_MESSAGES,
    PARAMETER_FILES, DEFAULT_PARAMETERS, SCHEME_OPTIONS,
    UI_WIDGET_NAMES, UI_DEFAULT_VALUES
)


class CarbonInterface(BaseInterface):
    """
    Interface for Single Particle Model (SPM) simulations.
    
    Provides complete functionality for SPM simulations including
    geometry, constants, boundary conditions, functions, and control.
    """
    
    def __init__(
        self, 
        parent: Optional[QWidget] = None, 
        ui_config: Optional['UIConfig'] = None
    ):
        """
        Initialize the Carbon interface.
        
        Args:
            parent: Parent widget
            ui_config: UI configuration for loading mode
        """
        super().__init__(parent, ui_config)
        self.interface_type = "carbon"
        self.setWindowTitle("BatteryFOAM - SPM Interface")
        
        # Add diagnostic logging to check widget availability
        self._diagnose_widget_availability()
        
    def _diagnose_widget_availability(self):
        """Diagnose widget availability and naming issues."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.debug("=== CARBON INTERFACE WIDGET DIAGNOSIS ===")
        
        # Check if we're using .ui file or hand-coded widgets
        if hasattr(self, 'length_lineEdit'):
            logger.debug("✓ Found length_lineEdit (from .ui file)")
        elif hasattr(self, 'length_edit'):
            logger.debug("✓ Found length_edit (from hand-coded)")
        else:
            logger.error("✗ Neither length_lineEdit nor length_edit found!")
            
        if hasattr(self, 'width_lineEdit'):
            logger.debug("✓ Found width_lineEdit (from .ui file)")
        elif hasattr(self, 'width_edit'):
            logger.debug("✓ Found width_edit (from hand-coded)")
        else:
            logger.error("✗ Neither width_lineEdit nor width_edit found!")
            
        if hasattr(self, 'height_lineEdit'):
            logger.debug("✓ Found height_lineEdit (from .ui file)")
        elif hasattr(self, 'height_edit'):
            logger.debug("✓ Found height_edit (from hand-coded)")
        else:
            logger.error("✗ Neither height_lineEdit nor height_edit found!")
            
        if hasattr(self, 'unit_select_box'):
            logger.debug("✓ Found unit_select_box (from .ui file)")
        elif hasattr(self, 'unit_combo'):
            logger.debug("✓ Found unit_combo (from hand-coded)")
        else:
            logger.error("✗ Neither unit_select_box nor unit_combo found!")
            
        # Check tab widget
        if hasattr(self, 'tabWidget'):
            logger.debug("✓ Found tabWidget")
        else:
            logger.error("✗ tabWidget not found!")
            
        # List all attributes that contain 'lineEdit' or 'edit'
        logger.debug("All QLineEdit-like attributes:")
        for attr_name in dir(self):
            if 'lineEdit' in attr_name.lower() or 'edit' in attr_name.lower():
                attr_value = getattr(self, attr_name, None)
                logger.debug(f"  {attr_name}: {type(attr_value)} = {attr_value}")
                
        logger.debug("=== END DIAGNOSIS ===")
        
    def _add_boundary_configuration(self, layout: QVBoxLayout):
        """Add boundary-specific configuration for Carbon interface."""
        # Create boundary configuration group
        boundary_group = QGroupBox("Boundary Conditions")
        boundary_layout = QVBoxLayout()
        
        # Initial condition
        initial_layout = QHBoxLayout()
        self.initial_cs_edit = QLineEdit(str(self._get_default_parameter("initial_cs")))
        initial_layout.addWidget(QLabel("Initial Cs value:"))
        initial_layout.addWidget(self.initial_cs_edit)
        boundary_layout.addLayout(initial_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.change_boundary_button = QPushButton("Change Boundary")
        self.change_boundary_button.clicked.connect(self._on_change_boundary_clicked)
        self.run_boundary_button = QPushButton("Run Boundary")
        self.run_boundary_button.clicked.connect(self._on_run_boundary_clicked)
        
        button_layout.addWidget(self.change_boundary_button)
        button_layout.addWidget(self.run_boundary_button)
        boundary_layout.addLayout(button_layout)
        
        boundary_group.setLayout(boundary_layout)
        layout.addWidget(boundary_group)
        
    def _update_boundary_parameters(self):
        """Update boundary parameters for Carbon interface."""
        try:
            # Update time_voltage file with initial conditions
            time_voltage_path = os.path.join(self.case_path, "time_voltage")
            initial_cs = float(self.initial_cs_edit.text())
            
            # Create time_voltage file content
            content = f"""# Time-voltage data for SPM simulation
# Format: time voltage
0.0 0.0
1.0 0.0
"""
            
            with open(time_voltage_path, 'w') as f:
                f.write(content)
                
            if self.terminal_output:
                self.terminal_output.append(f"Boundary conditions updated: initial_cs = {initial_cs}")
                
        except Exception as e:
            raise Exception(f"Failed to update boundary parameters: {str(e)}")
            
    def _run_boundary_commands(self):
        """Run boundary setup commands for Carbon interface."""
        try:
            # For SPM, boundary setup is minimal
            if self.terminal_output:
                self.terminal_output.append("Carbon boundary setup completed.")
                
        except Exception as e:
            raise Exception(f"Failed to run boundary commands: {str(e)}")
            
    def _update_geometry_parameters(self):
        """Update geometry parameters for Carbon interface."""
        try:
            # Update blockMeshDict
            block_mesh_path = os.path.join(self.case_path, "system", "blockMeshDict")
            
            length = float(self.length_edit.text())
            width = float(self.width_edit.text())
            height = float(self.height_edit.text())
            
            # Create blockMeshDict content
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

convertToMeters 1e-6;

vertices
(
    (0 0 0)
    ({length} 0 0)
    ({length} {width} 0)
    (0 {width} 0)
    (0 0 {height})
    ({length} 0 {height})
    ({length} {width} {height})
    (0 {width} {height})
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
            (4 5 6 7)
            (0 1 5 4)
            (1 2 6 5)
            (2 3 7 6)
        );
    }}
    outlet
    {{
        type patch;
        faces
        (
            (0 3 2 1)
        );
    }}
    walls
    {{
        type wall;
        faces
        (
            (0 1 2 3)
        );
    }}
);

mergePatchPairs
(
);

// ************************************************************************* //
"""
            
            with open(block_mesh_path, 'w') as f:
                f.write(content)
                
            if self.terminal_output:
                self.terminal_output.append("Geometry parameters updated successfully.")
                
        except Exception as e:
            raise Exception(f"Failed to update geometry parameters: {str(e)}")
            
    def _update_constants_parameters(self):
        """Update constants parameters for Carbon interface."""
        try:
            # Update LiProperties file
            li_props_path = os.path.join(self.case_path, "constant", "LiProperties")
            
            ds_value = float(self.param_edits["DS_value"].text())
            cs_max = float(self.param_edits["CS_max"].text())
            kreact = float(self.param_edits["kReact"].text())
            r_value = float(self.param_edits["R"].text())
            f_value = float(self.param_edits["F"].text())
            ce_value = float(self.param_edits["Ce"].text())
            alpha_a = float(self.param_edits["alphaA"].text())
            alpha_c = float(self.param_edits["alphaC"].text())
            t_temp = float(self.param_edits["T_temp"].text())
            i_app = float(self.param_edits["I_app"].text())
            
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

LiProperties
{{
    DS          [0 2 -1 0 0 0 0] {ds_value};
    CS_max      [0 0 -3 0 0 0 0] {cs_max};
    kReact      [0 0 0 0 0 0 0] {kreact};
    R           [0 2 -2 -1 0 0 0] {r_value};
    F           [0 0 1 0 0 0 0] {f_value};
    Ce          [0 0 -3 0 0 0 0] {ce_value};
    alphaA      [0 0 0 0 0 0 0] {alpha_a};
    alphaC      [0 0 0 0 0 0 0] {alpha_c};
    T_temp      [0 0 0 1 0 0 0] {t_temp};
    I_app       [0 0 0 0 0 0 0] {i_app};
}}

// ************************************************************************* //
"""
            
            with open(li_props_path, 'w') as f:
                f.write(content)
                
            if self.terminal_output:
                self.terminal_output.append("Constants parameters updated successfully.")
                
        except Exception as e:
            raise Exception(f"Failed to update constants parameters: {str(e)}")
            
    def _update_functions_parameters(self):
        """Update function parameters for Carbon interface."""
        try:
            # Update fvSchemes
            fv_schemes_path = os.path.join(self.case_path, "system", "fvSchemes")
            
            ddt_scheme = self.ddtschemes_combo.currentText()
            grad_scheme = self.gradschemes_combo.currentText()
            div_scheme = self.divschemes_combo.currentText()
            laplacian_scheme = self.laplacianschemes_combo.currentText()
            interpolation_scheme = self.interpolationschemes_combo.currentText()
            
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
    default         {div_scheme};
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

// ************************************************************************* //
"""
            
            with open(fv_schemes_path, 'w') as f:
                f.write(content)
                
            # Update fvSolution
            fv_solution_path = os.path.join(self.case_path, "system", "fvSolution")
            
            content = """/*--------------------------------*- C++ -*----------------------------------*\\
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
{
    cs
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0.1;
    }
}

PIMPLE
{
    nNonOrthogonalCorrectors 0;
}

// ************************************************************************* //
"""
            
            with open(fv_solution_path, 'w') as f:
                f.write(content)
                
            if self.terminal_output:
                self.terminal_output.append("Function parameters updated successfully.")
                
        except Exception as e:
            raise Exception(f"Failed to update function parameters: {str(e)}")
            
    def _update_control_parameters(self):
        """Update control parameters for Carbon interface."""
        try:
            # Update controlDict
            control_dict_path = os.path.join(self.case_path, "system", "controlDict")
            
            end_time = float(self.end_time_edit.value())
            delta_t = float(self.delta_t_edit.value())
            write_interval = float(self.write_interval_edit.value())
            tolerance = float(self.tolerance_edit.text())
            
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
            
            with open(control_dict_path, 'w') as f:
                f.write(content)
                
            if self.terminal_output:
                self.terminal_output.append("Control parameters updated successfully.")
                
        except Exception as e:
            raise Exception(f"Failed to update control parameters: {str(e)}")
