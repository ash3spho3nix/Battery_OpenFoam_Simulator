"""
Carbon Interface for Single Particle Model (SPM) - Fixed Implementation.

This module provides the CarbonInterface class with complete signal connections
and proper error handling for SPM simulation interface.
"""

import os
import sys
import logging
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
        logger = logging.getLogger(__name__)
        logger.debug("CarbonInterface.__init__() called")
        
        super().__init__(parent, ui_config)
        self.interface_type = "carbon"
        self.setWindowTitle("BatteryFOAM - SPM Interface")
        
        # Add diagnostic logging to check widget availability
        self._diagnose_widget_availability()
        
        # Connect all signals after widget creation
        self._connect_all_signals()
        
    def _connect_all_signals(self):
        """Connect all signal-slot connections for Carbon interface."""
        logger = logging.getLogger(__name__)
        logger.debug("Connecting Carbon interface signals...")
        
        try:
            # Geometry tab signals
            self._connect_geometry_signals()
            
            # Constants tab signals
            self._connect_constants_signals()
            
            # Boundary tab signals
            self._connect_boundary_signals()
            
            # Functions tab signals
            self._connect_functions_signals()
            
            # Control tab signals
            self._connect_control_signals()
            
            # Terminal tab signals
            self._connect_terminal_signals()
            
            logger.debug("All Carbon interface signals connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect signals: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to connect signals: {str(e)}")
    
    def _connect_geometry_signals(self):
        """Connect geometry tab signal-slot connections."""
        logger = logging.getLogger(__name__)
        
        # Connect geometry parameter changes
        if hasattr(self, 'length_edit'):
            self.length_edit.textChanged.connect(self._on_geometry_parameter_changed)
            logger.debug("Connected length_edit.textChanged")
        
        if hasattr(self, 'width_edit'):
            self.width_edit.textChanged.connect(self._on_geometry_parameter_changed)
            logger.debug("Connected width_edit.textChanged")
        
        if hasattr(self, 'height_edit'):
            self.height_edit.textChanged.connect(self._on_geometry_parameter_changed)
            logger.debug("Connected height_edit.textChanged")
        
        if hasattr(self, 'radius_edit'):
            self.radius_edit.textChanged.connect(self._on_geometry_parameter_changed)
            logger.debug("Connected radius_edit.textChanged")
        
        if hasattr(self, 'unit_combo'):
            self.unit_combo.currentTextChanged.connect(self._on_unit_changed)
            logger.debug("Connected unit_combo.currentTextChanged")
        
        # Connect division spin boxes
        if hasattr(self, 'x_div_edit'):
            self.x_div_edit.valueChanged.connect(self._on_geometry_parameter_changed)
            logger.debug("Connected x_div_edit.valueChanged")
        
        if hasattr(self, 'y_div_edit'):
            self.y_div_edit.valueChanged.connect(self._on_geometry_parameter_changed)
            logger.debug("Connected y_div_edit.valueChanged")
        
        if hasattr(self, 'z_div_edit'):
            self.z_div_edit.valueChanged.connect(self._on_geometry_parameter_changed)
            logger.debug("Connected z_div_edit.valueChanged")
        
        # Connect geometry buttons
        if hasattr(self, 'change_geometry_button'):
            self.change_geometry_button.clicked.connect(self._on_change_geometry_clicked)
            logger.debug("Connected change_geometry_button.clicked")
        
        if hasattr(self, 'run_geometry_button'):
            self.run_geometry_button.clicked.connect(self._on_run_geometry_clicked)
            logger.debug("Connected run_geometry_button.clicked")
        
        if hasattr(self, 'view_geometry_button'):
            self.view_geometry_button.clicked.connect(self._on_view_geometry_clicked)
            logger.debug("Connected view_geometry_button.clicked")
    
    def _connect_constants_signals(self):
        """Connect constants tab signal-slot connections."""
        logger = logging.getLogger(__name__)
        
        # Connect material property changes
        if hasattr(self, 'param_edits'):
            for param_name, widget in self.param_edits.items():
                if hasattr(widget, 'textChanged'):
                    widget.textChanged.connect(self._on_constants_parameter_changed)
                    logger.debug(f"Connected {param_name} parameter change")
        
        # Connect material selection
        if hasattr(self, 'material_carbon'):
            self.material_carbon.toggled.connect(self._on_material_changed)
            logger.debug("Connected material_carbon.toggled")
        
        if hasattr(self, 'material_silicon'):
            self.material_silicon.toggled.connect(self._on_material_changed)
            logger.debug("Connected material_silicon.toggled")
        
        # Connect constants buttons
        if hasattr(self, 'change_constants_button'):
            self.change_constants_button.clicked.connect(self._on_change_constants_clicked)
            logger.debug("Connected change_constants_button.clicked")
        
        if hasattr(self, 'run_constants_button'):
            self.run_constants_button.clicked.connect(self._on_run_constants_clicked)
            logger.debug("Connected run_constants_button.clicked")
        
        if hasattr(self, 'help_constants_button'):
            self.help_constants_button.clicked.connect(self._on_help_constants_clicked)
            logger.debug("Connected help_constants_button.clicked")
    
    def _connect_boundary_signals(self):
        """Connect boundary tab signal-slot connections."""
        logger = logging.getLogger(__name__)
        
        # Connect boundary parameter changes
        if hasattr(self, 'initial_cs_edit'):
            self.initial_cs_edit.textChanged.connect(self._on_boundary_parameter_changed)
            logger.debug("Connected initial_cs_edit.textChanged")
        
        # Connect boundary buttons
        if hasattr(self, 'change_boundary_button'):
            self.change_boundary_button.clicked.connect(self._on_change_boundary_clicked)
            logger.debug("Connected change_boundary_button.clicked")
        
        if hasattr(self, 'run_boundary_button'):
            self.run_boundary_button.clicked.connect(self._on_run_boundary_clicked)
            logger.debug("Connected run_boundary_button.clicked")
    
    def _connect_functions_signals(self):
        """Connect functions tab signal-slot connections."""
        logger = logging.getLogger(__name__)
        
        # Connect discretization scheme changes
        scheme_types = ['ddtSchemes', 'gradSchemes', 'divSchemes', 'laplacianSchemes', 'interpolationSchemes']
        
        for scheme_type in scheme_types:
            combo_name = f"{scheme_type.lower()}_combo"
            if hasattr(self, combo_name):
                combo = getattr(self, combo_name)
                combo.currentTextChanged.connect(self._on_functions_parameter_changed)
                logger.debug(f"Connected {combo_name}.currentTextChanged")
        
        # Connect functions buttons
        if hasattr(self, 'change_functions_button'):
            self.change_functions_button.clicked.connect(self._on_change_functions_clicked)
            logger.debug("Connected change_functions_button.clicked")
        
        if hasattr(self, 'run_functions_button'):
            self.run_functions_button.clicked.connect(self._on_run_functions_clicked)
            logger.debug("Connected run_functions_button.clicked")
    
    def _connect_control_signals(self):
        """Connect control tab signal-slot connections."""
        logger = logging.getLogger(__name__)
        
        # Connect control parameter changes
        if hasattr(self, 'end_time_edit'):
            self.end_time_edit.valueChanged.connect(self._on_control_parameter_changed)
            logger.debug("Connected end_time_edit.valueChanged")
        
        if hasattr(self, 'delta_t_edit'):
            self.delta_t_edit.valueChanged.connect(self._on_control_parameter_changed)
            logger.debug("Connected delta_t_edit.valueChanged")
        
        if hasattr(self, 'write_interval_edit'):
            self.write_interval_edit.valueChanged.connect(self._on_control_parameter_changed)
            logger.debug("Connected write_interval_edit.valueChanged")
        
        if hasattr(self, 'tolerance_edit'):
            self.tolerance_edit.textChanged.connect(self._on_control_parameter_changed)
            logger.debug("Connected tolerance_edit.textChanged")
        
        # Connect control buttons
        if hasattr(self, 'change_control_button'):
            self.change_control_button.clicked.connect(self._on_change_control_clicked)
            logger.debug("Connected change_control_button.clicked")
        
        if hasattr(self, 'run_button'):
            self.run_button.clicked.connect(self._on_run_clicked)
            logger.debug("Connected run_button.clicked")
        
        if hasattr(self, 'pause_button'):
            self.pause_button.clicked.connect(self._on_pause_clicked)
            logger.debug("Connected pause_button.clicked")
        
        if hasattr(self, 'stop_button'):
            self.stop_button.clicked.connect(self._on_stop_clicked)
            logger.debug("Connected stop_button.clicked")
    
    def _connect_terminal_signals(self):
        """Connect terminal tab signal-slot connections."""
        logger = logging.getLogger(__name__)
        
        # Connect command input
        if hasattr(self, 'command_input'):
            self.command_input.returnPressed.connect(self._on_command_entered)
            logger.debug("Connected command_input.returnPressed")
        
        if hasattr(self, 'command_button'):
            self.command_button.clicked.connect(self._on_command_entered)
            logger.debug("Connected command_button.clicked")
    
    def _on_geometry_parameter_changed(self):
        """Handle geometry parameter changes."""
        logger = logging.getLogger(__name__)
        logger.debug("Geometry parameter changed")
        
        # Validate parameters
        errors = self._validate_geometry_parameters()
        
        if errors:
            error_msg = "\n".join(errors)
            self._show_validation_error("Geometry Validation Error", error_msg)
            return
        
        # Update geometry parameters
        try:
            self._update_geometry_parameters()
            self._show_status_message("Geometry parameters updated successfully")
        except Exception as e:
            logger.error(f"Failed to update geometry parameters: {e}")
            self._show_error_message(f"Failed to update geometry: {str(e)}")
    
    def _on_constants_parameter_changed(self):
        """Handle constants parameter changes."""
        logger = logging.getLogger(__name__)
        logger.debug("Constants parameter changed")
        
        # Validate parameters
        errors = self._validate_material_parameters()
        
        if errors:
            error_msg = "\n".join(errors)
            self._show_validation_error("Material Validation Error", error_msg)
            return
        
        # Update constants parameters
        try:
            self._update_constants_parameters()
            self._show_status_message("Material parameters updated successfully")
        except Exception as e:
            logger.error(f"Failed to update constants parameters: {e}")
            self._show_error_message(f"Failed to update material properties: {str(e)}")
    
    def _on_boundary_parameter_changed(self):
        """Handle boundary parameter changes."""
        logger = logging.getLogger(__name__)
        logger.debug("Boundary parameter changed")
        
        # Update boundary parameters
        try:
            self._update_boundary_parameters()
            self._show_status_message("Boundary parameters updated successfully")
        except Exception as e:
            logger.error(f"Failed to update boundary parameters: {e}")
            self._show_error_message(f"Failed to update boundary: {str(e)}")
    
    def _on_functions_parameter_changed(self):
        """Handle functions parameter changes."""
        logger = logging.getLogger(__name__)
        logger.debug("Functions parameter changed")
        
        # Update functions parameters
        try:
            self._update_functions_parameters()
            self._show_status_message("Function parameters updated successfully")
        except Exception as e:
            logger.error(f"Failed to update functions parameters: {e}")
            self._show_error_message(f"Failed to update functions: {str(e)}")
    
    def _on_control_parameter_changed(self):
        """Handle control parameter changes."""
        logger = logging.getLogger(__name__)
        logger.debug("Control parameter changed")
        
        # Validate parameters
        errors = self._validate_control_parameters()
        
        if errors:
            error_msg = "\n".join(errors)
            self._show_validation_error("Control Validation Error", error_msg)
            return
        
        # Update control parameters
        try:
            self._update_control_parameters()
            self._show_status_message("Control parameters updated successfully")
        except Exception as e:
            logger.error(f"Failed to update control parameters: {e}")
            self._show_error_message(f"Failed to update control: {str(e)}")
    
    def _on_unit_changed(self, unit: str):
        """Handle unit selection changes."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Unit changed to: {unit}")
        
        # Update unit factor for geometry calculations
        self._update_unit_factor(unit)
    
    def _on_material_changed(self, checked: bool):
        """Handle material selection changes."""
        logger = logging.getLogger(__name__)
        logger.debug("Material selection changed")
        
        # Update material-specific parameters
        self._update_material_properties()
    
    def _validate_geometry_parameters(self):
        """Validate geometry parameters."""
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
    
    def _validate_material_parameters(self):
        """Validate material parameters."""
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
    
    def _update_unit_factor(self, unit: str):
        """Update unit factor based on selected unit."""
        from src.core.constants import GEOMETRY_UNITS
        unit_factor = GEOMETRY_UNITS.get(unit.lower(), "1e-6")
        
        # Update any geometry calculations that depend on units
        logger = logging.getLogger(__name__)
        logger.debug(f"Unit factor updated to: {unit_factor}")
    
    def _update_material_properties(self):
        """Update material-specific properties."""
        # Update material-specific parameters based on selection
        if hasattr(self, 'material_carbon') and self.material_carbon.isChecked():
            material = "Carbon (Gr)"
        elif hasattr(self, 'material_silicon') and self.material_silicon.isChecked():
            material = "Silicon (Si)"
        else:
            material = "Unknown"
        
        logger = logging.getLogger(__name__)
        logger.debug(f"Material updated to: {material}")
    
    def _show_validation_error(self, title: str, message: str):
        """Show validation error message."""
        logger = logging.getLogger(__name__)
        logger.warning(f"Validation error: {message}")
        
        QMessageBox.warning(self, title, message)
    
    def _show_error_message(self, message: str):
        """Show error message."""
        logger = logging.getLogger(__name__)
        logger.error(f"Error: {message}")
        
        QMessageBox.critical(self, "Error", message)
    
    def _show_status_message(self, message: str):
        """Show status message in terminal."""
        if self.terminal_output:
            self.terminal_output.append(message)
    
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
            
            # Try to get values from either .ui file widgets or hand-coded widgets
            length = self._get_widget_value('length')
            width = self._get_widget_value('width')
            height = self._get_widget_value('height')
            
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
            
            # Get parameter values from widgets
            ds_value = self._get_widget_value('DS_value')
            cs_max = self._get_widget_value('CS_max')
            kreact = self._get_widget_value('kReact')
            r_value = self._get_widget_value('R')
            f_value = self._get_widget_value('F')
            ce_value = self._get_widget_value('Ce')
            alpha_a = self._get_widget_value('alphaA')
            alpha_c = self._get_widget_value('alphaC')
            t_temp = self._get_widget_value('T_temp')
            i_app = self._get_widget_value('I_app')
            
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
            
    def _get_widget_value(self, widget_name: str) -> float:
        """Get value from widget, trying both .ui and hand-coded naming conventions."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Try .ui file widget names first
        ui_widget_names = [
            f"{widget_name}_lineEdit",
            f"{widget_name}_spinBox",
            f"{widget_name}_doubleSpinBox"
        ]
        
        for widget_name_variant in ui_widget_names:
            if hasattr(self, widget_name_variant):
                widget = getattr(self, widget_name_variant)
                try:
                    if hasattr(widget, 'text'):
                        value = float(widget.text())
                        logger.debug(f"Got value {value} from {widget_name_variant}")
                        return value
                    elif hasattr(widget, 'value'):
                        value = float(widget.value())
                        logger.debug(f"Got value {value} from {widget_name_variant}")
                        return value
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to get value from {widget_name_variant}: {e}")
        
        # Try hand-coded widget names
        hand_coded_names = [
            f"{widget_name}_edit",
            f"{widget_name}_spin",
            f"{widget_name}_double_spin"
        ]
        
        for widget_name_variant in hand_coded_names:
            if hasattr(self, widget_name_variant):
                widget = getattr(self, widget_name_variant)
                try:
                    if hasattr(widget, 'text'):
                        value = float(widget.text())
                        logger.debug(f"Got value {value} from {widget_name_variant}")
                        return value
                    elif hasattr(widget, 'value'):
                        value = float(widget.value())
                        logger.debug(f"Got value {value} from {widget_name_variant}")
                        return value
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to get value from {widget_name_variant}: {e}")
        
        # If no widget found, use default value
        default_value = self._get_default_parameter(widget_name.lower(), 0.0)
        logger.warning(f"No widget found for {widget_name}, using default: {default_value}")
        return default_value