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
from src_py.gui.interfaces.base_interface import BaseInterface
from src_py.openfoam.process_controller import ProcessController
from src_py.openfoam.solver_manager import OpenFOAMSolverManager
from src_py.utils.parameter_parser import ParameterManager
from src_py.utils.file_operations import TemplateManager
from src_py.core.constants import (
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
        
    def _add_boundary_configuration(self, layout: QVBoxLayout):
        """Add SPM-specific boundary configuration."""
        # SPM uses simpler boundary conditions
        boundary_group = QGroupBox("Boundary Conditions")
        boundary_layout = QVBoxLayout()
        
        # Initial Cs value (using widget name from .ui file)
        cs_layout = QHBoxLayout()
        self.initial_cs_edit = QLineEdit(str(DEFAULT_PARAMETERS["initial_cs"]))
        cs_layout.addWidget(QLabel("Initial Cs:"))
        cs_layout.addWidget(self.initial_cs_edit)
        boundary_layout.addLayout(cs_layout)
        
        # Current direction (using widget names from .ui file)
        current_layout = QHBoxLayout()
        self.select_charge = QRadioButton("Charge")
        self.select_discharge = QRadioButton("Discharge")
        self.select_charge.setChecked(True)  # Default to charge
        current_layout.addWidget(QLabel("Current direction:"))
        current_layout.addWidget(self.select_charge)
        current_layout.addWidget(self.select_discharge)
        boundary_layout.addLayout(current_layout)
        
        boundary_group.setLayout(boundary_layout)
        layout.addWidget(boundary_group)
        
    def _update_geometry_parameters(self):
        """Update geometry parameters in OpenFOAM files for SPM."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        # Update blockMeshDict
        block_mesh_path = os.path.join(self.case_path, "system", "blockMeshDict")
        if os.path.exists(block_mesh_path):
            with open(block_mesh_path, 'r') as f:
                content = f.read()
                
            # Get dimensions using widget names from BaseInterface
            length = float(self.length_edit.text()) / 2.0  # Convert to half-length
            width = float(self.width_edit.text()) / 2.0
            height = float(self.height_edit.text()) / 2.0
            
            # Update unit conversion
            unit = self.unit_combo.currentText()
            if unit == "micrometer (μm)":
                unit_factor = "1e-6"
            elif unit == "millimeter (mm)":
                unit_factor = "1e-3"
            else:  # meter (m)
                unit_factor = "1e-0"
                
            # Update convertToMeters
            content = content.replace(
                r"convertToMeters 1e-[0-9]+;//[a-z]+",
                f"convertToMeters {unit_factor};//{unit.split()[0].lower()}"
            )
            
            # Update vertex coordinates
            coords = [
                f"({-length} {-width} {-height})",
                f"({-length} {width} {-height})",
                f"({-length} {width} {height})",
                f"({-length} {-width} {height})",
                f"({length} {-width} {-height})",
                f"({length} {width} {-height})",
                f"({length} {width} {height})",
                f"({length} {-width} {height})"
            ]
            
            # Replace vertex coordinates (simplified - would need more robust parsing)
            for i, coord in enumerate(coords):
                content = content.replace(f"({[-length, -length, -length, -length, length, length, length, length][i]} {[-width, width, width, -width, -width, width, width, -width][i]} {[-height, -height, height, height, -height, -height, height, height][i]})", coord)
                
            # Update divisions using widget names from BaseInterface
            x_div = self.x_div_edit.value()
            y_div = self.y_div_edit.value()
            z_div = self.z_div_edit.value()
            content = content.replace(r"[0-9]+ [0-9]+ [0-9+]", f"{x_div} {y_div} {z_div}")
            
            with open(block_mesh_path, 'w') as f:
                f.write(content)
                
        # Update topoSetDict for sphere radius
        topo_set_path = os.path.join(self.case_path, "system", "topoSetDict")
        if os.path.exists(topo_set_path):
            with open(topo_set_path, 'r') as f:
                content = f.read()
                
            radius = float(self.radius_edit.text())
            unit = self.unit_combo.currentText()
            if unit == "micrometer (μm)":
                radius_str = f"{radius}e-06"
            elif unit == "millimeter (mm)":
                radius_str = f"{radius}e-03"
            else:  # meter (m)
                radius_str = f"{radius}e-00"
                
            # Update radius and box coordinates
            content = content.replace(r"[0-9.e-]+", radius_str)
            # Update box coordinates based on dimensions
            content = content.replace(r"[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+", 
                                    f"{-length}e-6 {-width}e-6 {-height}e-6")
            content = content.replace(r"[0-9.e-]+ [ ]+[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+", 
                                    f"{length}e-6 {width}e-6 {height}e-6")
                                    
            with open(topo_set_path, 'w') as f:
                f.write(content)
                
    def _update_constants_parameters(self):
        """Update constants parameters in LiProperties files for SPM."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        # Update LiProperties in constant, ele, and solidPhase directories
        for subdir in ["", "ele", "solidPhase"]:
            li_props_path = os.path.join(self.case_path, "constant", subdir, "LiProperties")
            if os.path.exists(li_props_path):
                with open(li_props_path, 'r') as f:
                    content = f.read()
                    
                # Update parameters using widget names from BaseInterface
                param_map = {
                    "Ds_value": self.param_edits["DS_value"].text(),
                    "Cs_max": self.param_edits["CS_max"].text(),
                    "kReact": self.param_edits["kReact"].text(),
                    "R": self.param_edits["R"].text(),
                    "F": self.param_edits["F"].text(),
                    "Ce": self.param_edits["Ce"].text(),
                    "alphaA": self.param_edits["alphaA"].text(),
                    "alphaC": self.param_edits["alphaC"].text(),
                    "T_temp": self.param_edits["T_temp"].text(),
                    "I_app": self.param_edits["I_app"].text()
                }
                
                for param, value in param_map.items():
                    content = content.replace(rf"{param}[ ]+\[.*?\][ ]+[0-9.e-]+", 
                                            f"{param} [0 -1 0 0 0 0 0] {value}")
                    
                with open(li_props_path, 'w') as f:
                    f.write(content)
                    
        # Update material selection in solveSolid.H using widget names from BaseInterface
        if self.solver_path:
            solve_solid_path = os.path.join(self.solver_path, "SPMFoam", "solid", "solveSolid.H")
            if os.path.exists(solve_solid_path):
                with open(solve_solid_path, 'r') as f:
                    content = f.read()
                    
                if self.material_carbon.isChecked():  # Using widget name from BaseInterface
                    content = content.replace("#include \"OCV_Si.H\"", "//#include \"OCV_Si.H\"")
                    content = content.replace("//#include \"OCV_Gr.H\"", "#include \"OCV_Gr.H\"")
                else:
                    content = content.replace("#include \"OCV_Gr.H\"", "//#include \"OCV_Gr.H\"")
                    content = content.replace("//#include \"OCV_Si.H\"", "#include \"OCV_Si.H\"")
                    
                with open(solve_solid_path, 'w') as f:
                    f.write(content)
                    
    def _update_boundary_parameters(self):
        """Update boundary parameters for SPM."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        # Update initial Cs in 0/solidPhase/Cs using widget name from BaseInterface
        cs_path = os.path.join(self.case_path, "0", "solidPhase", "Cs")
        if os.path.exists(cs_path):
            with open(cs_path, 'r') as f:
                content = f.read()
                
            initial_cs = self.initial_cs_edit.text()  # Using widget name from BaseInterface
            content = content.replace(r"internalField[ ]+uniform[ ]+[0-9.e-]+", 
                                    f"internalField   uniform   {initial_cs}")
                                    
            with open(cs_path, 'w') as f:
                f.write(content)
                
    def _update_functions_parameters(self):
        """Update function parameters in fvSchemes and fvSolution."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        # Update fvSchemes using widget names from BaseInterface
        fv_schemes_path = os.path.join(self.case_path, "system", "fvSchemes")
        if os.path.exists(fv_schemes_path):
            with open(fv_schemes_path, 'r') as f:
                content = f.read()
                
            # Update schemes using widget names from BaseInterface
            scheme_map = {
                "ddtSchemes": self.ddt_schemes_combo.currentText(),
                "gradSchemes": self.grad_schemes_combo.currentText(),
                "divSchemes": self.div_schemes_combo.currentText(),
                "laplacianSchemes": self.laplacian_schemes_combo.currentText(),
                "interpolationSchemes": self.interpolation_schemes_combo.currentText()
            }
            
            for scheme_type, scheme_value in scheme_map.items():
                content = content.replace(rf"{scheme_type}[ ]+\{{[^\}}]+\}}", 
                                        f"{scheme_type}\n{{\n    default         {scheme_value}")
                                          
            with open(fv_schemes_path, 'w') as f:
                f.write(content)
                
        # Update fvSolution using widget name from BaseInterface
        fv_solution_path = os.path.join(self.case_path, "system", "fvSolution")
        if os.path.exists(fv_solution_path):
            with open(fv_solution_path, 'r') as f:
                content = f.read()
                
            tolerance = self.tolerance_edit.text()  # Using widget name from BaseInterface
            content = content.replace(r"tolerance[ ]+[0-9.e-]+", f"tolerance       {tolerance}")
            
            with open(fv_solution_path, 'w') as f:
                f.write(content)
                
        # Update subdirectories
        for subdir in ["ele", "solidPhase"]:
            subdir_schemes = os.path.join(self.case_path, "system", subdir, "fvSchemes")
            subdir_solution = os.path.join(self.case_path, "system", subdir, "fvSolution")
            
            if os.path.exists(fv_schemes_path) and not os.path.exists(subdir_schemes):
                import shutil
                os.makedirs(os.path.dirname(subdir_schemes), exist_ok=True)
                shutil.copy2(fv_schemes_path, subdir_schemes)
                shutil.copy2(fv_solution_path, subdir_solution)
                
    def _update_control_parameters(self):
        """Update control parameters in controlDict."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        control_dict_path = os.path.join(self.case_path, "system", "controlDict")
        if os.path.exists(control_dict_path):
            with open(control_dict_path, 'r') as f:
                content = f.read()
                
            end_time = self.end_time_edit.value()  # Using widget name from BaseInterface
            delta_t = self.delta_t_edit.value()  # Using widget name from BaseInterface
            write_interval = self.write_interval_edit.value()  # Using widget name from BaseInterface
            
            content = content.replace(r"endTime[ ]+[0-9.e-]+", f"endTime         {end_time}")
            content = content.replace(r"deltaT[ ]+[0-9.e-]+", f"deltaT          {delta_t}")
            content = content.replace(r"writeInterval[ ]+[0-9.e-]+", f"writeInterval   {write_interval}")
            
            with open(control_dict_path, 'w') as f:
                f.write(content)
                
    def _on_run_clicked(self):
        """Override run to handle SPM-specific workflow."""
        try:
            # Check if geometry needs to be regenerated
            self._check_and_regenerate_geometry()
            
            # Start simulation
            super()._on_run_clicked()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start SPM simulation: {str(e)}")
            
    def _check_and_regenerate_geometry(self):
        """Check if geometry needs regeneration and do it if needed."""
        # Check if mesh files exist
        poly_mesh_path = os.path.join(self.case_path, "constant", "polyMesh")
        if not os.path.exists(poly_mesh_path):
            self.terminal_output.append("Mesh not found, regenerating geometry...")
            self._run_geometry_commands()
        else:
            # Check modification times to see if regeneration is needed
            # For now, always regenerate if parameters changed recently
            self._run_geometry_commands()
            
    def _on_process_finished(self, exit_code: int):
        """Handle SPM-specific process completion."""
        super()._on_process_finished(exit_code)
        
        if exit_code == 0:
            # Check for time_voltage file
            time_voltage_path = os.path.join(self.case_path, "time_voltage")
            if os.path.exists(time_voltage_path):
                self.terminal_output.append("Results file generated: time_voltage")
                self.terminal_output.append("Use ParaView to visualize results or export for analysis.")
