"""
Half-Cell Interface for P2D Half-Cell Model.

This module provides the HalfCellInterface class, which implements the
P2D half-cell simulation interface with functionality for working electrode
and separator regions.
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

from .base_interface import BaseInterface
from ...openfoam.process_controller import ProcessController
from ...openfoam.solver_manager import OpenFOAMSolverManager
from ...utils.parameter_parser import ParameterManager
from ...utils.file_operations import TemplateManager
from ...core.constants import (
    ERROR_MESSAGES, SUCCESS_MESSAGES, WARNING_MESSAGES,
    PARAMETER_FILES, DEFAULT_PARAMETERS, SCHEME_OPTIONS
)


class HalfCellInterface(BaseInterface):
    """
    Interface for P2D Half-Cell simulations.
    
    Provides functionality for half-cell simulations with working electrode
    and separator regions, including electrochemical modeling parameters.
    """
    
    def __init__(
        self, 
        parent: Optional[QWidget] = None, 
        ui_config: Optional['UIConfig'] = None
    ):
        """
        Initialize the Half-Cell interface.
        
        Args:
            parent: Parent widget
            ui_config: UI configuration for loading mode
        """
        super().__init__(parent, ui_config)
        self.interface_type = "halfcell"
        self.setWindowTitle("BatteryFOAM - P2D Half-Cell Interface")
        
    def _add_boundary_configuration(self, layout: QVBoxLayout):
        """Add half-cell-specific boundary configuration."""
        # Half-cell has more complex boundary conditions
        boundary_group = QGroupBox("Boundary Conditions")
        boundary_layout = QVBoxLayout()
        
        # Working electrode parameters
        we_group = QGroupBox("Working Electrode")
        we_layout = QVBoxLayout()
        
        # Electrode thickness
        thickness_layout = QHBoxLayout()
        self.we_thickness_edit = QLineEdit("50")  # Default 50 μm
        thickness_layout.addWidget(QLabel("WE Thickness (μm):"))
        thickness_layout.addWidget(self.we_thickness_edit)
        we_layout.addLayout(thickness_layout)
        
        # Active material fraction
        amf_layout = QHBoxLayout()
        self.we_amf_edit = QLineEdit("0.5")  # Default 50%
        amf_layout.addWidget(QLabel("Active Material Fraction:"))
        amf_layout.addWidget(self.we_amf_edit)
        we_layout.addLayout(amf_layout)
        
        we_group.setLayout(we_layout)
        boundary_layout.addWidget(we_group)
        
        # Separator parameters
        sep_group = QGroupBox("Separator")
        sep_layout = QVBoxLayout()
        
        # Separator thickness
        sep_thickness_layout = QHBoxLayout()
        self.sep_thickness_edit = QLineEdit("25")  # Default 25 μm
        sep_thickness_layout.addWidget(QLabel("Separator Thickness (μm):"))
        sep_thickness_layout.addWidget(self.sep_thickness_edit)
        sep_layout.addLayout(sep_thickness_layout)
        
        # Porosity
        porosity_layout = QHBoxLayout()
        self.sep_porosity_edit = QLineEdit("0.5")  # Default 50%
        porosity_layout.addWidget(QLabel("Separator Porosity:"))
        porosity_layout.addWidget(self.sep_porosity_edit)
        sep_layout.addLayout(porosity_layout)
        
        sep_group.setLayout(sep_layout)
        boundary_layout.addWidget(sep_group)
        
        # Electrochemical parameters
        electrochem_group = QGroupBox("Electrochemical Parameters")
        electrochem_layout = QVBoxLayout()
        
        # Exchange current density
        j0_layout = QHBoxLayout()
        self.j0_edit = QLineEdit("1e-4")  # Default exchange current density
        j0_layout.addWidget(QLabel("Exchange Current Density:"))
        j0_layout.addWidget(self.j0_edit)
        electrochem_layout.addLayout(j0_layout)
        
        # Double layer capacitance
        cdl_layout = QHBoxLayout()
        self.cdl_edit = QLineEdit("0.1")  # Default double layer capacitance
        cdl_layout.addWidget(QLabel("Double Layer Capacitance:"))
        cdl_layout.addWidget(self.cdl_edit)
        electrochem_layout.addLayout(cdl_layout)
        
        electrochem_group.setLayout(electrochem_layout)
        boundary_layout.addWidget(electrochem_group)
        
        boundary_group.setLayout(boundary_layout)
        layout.addWidget(boundary_group)
        
    def _update_geometry_parameters(self):
        """Update geometry parameters for half-cell."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        # Update blockMeshDict for half-cell geometry
        block_mesh_path = os.path.join(self.case_path, "system", "blockMeshDict")
        if os.path.exists(block_mesh_path):
            with open(block_mesh_path, 'r') as f:
                content = f.read()
                
            # Get dimensions (half-cell specific)
            we_thickness = float(self.we_thickness_edit.text()) / 2.0
            sep_thickness = float(self.sep_thickness_edit.text()) / 2.0
            width = float(self.width_edit.text()) / 2.0
            height = float(self.height_edit.text()) / 2.0
            
            # Total length is WE + separator
            total_length = we_thickness + sep_thickness
            
            # Update unit conversion
            unit = self.unit_combo.currentText()
            if unit == "micrometer (μm)":
                unit_factor = "1e-6"
            elif unit == "millimeter (mm)":
                unit_factor = "1e-3"
            else:  # meter (m)
                unit_factor = "1e-0"
                
            content = content.replace(r"convertToMeters 1e-[0-9]+;//[a-z]+",
                                    f"convertToMeters {unit_factor};//{unit.split()[0].lower()}")
            
            # Update vertex coordinates for half-cell
            coords = [
                f"({-total_length} {-width} {-height})",
                f"({-total_length} {width} {-height})",
                f"({-total_length} {width} {height})",
                f"({-total_length} {-width} {height})",
                f"({0} {-width} {-height})",  # Interface between WE and separator
                f"({0} {width} {-height})",
                f"({0} {width} {height})",
                f"({0} {-width} {height})"
            ]
            
            # Replace vertex coordinates
            for i, coord in enumerate(coords):
                # This is a simplified replacement - would need more robust parsing
                content = content.replace(f"({[-total_length, -total_length, -total_length, -total_length, 0, 0, 0, 0][i]} {[-width, width, width, -width, -width, width, width, -width][i]} {[-height, -height, height, height, -height, -height, height, height][i]})", coord)
                
            # Update divisions
            x_div = self.x_div_edit.value()
            y_div = self.y_div_edit.value()
            z_div = self.z_div_edit.value()
            content = content.replace(r"[0-9]+ [0-9]+ [0-9+]", f"{x_div} {y_div} {z_div}")
            
            with open(block_mesh_path, 'w') as f:
                f.write(content)
                
        # Update topoSetDict for half-cell regions
        topo_set_path = os.path.join(self.case_path, "system", "topoSetDict")
        if os.path.exists(topo_set_path):
            with open(topo_set_path, 'r') as f:
                content = f.read()
                
            # Update box coordinates for WE and separator regions
            # Working electrode region
            content = content.replace(r"boxToCell.*?[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+.*?[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+",
                                    f"boxToCell\n{{\n    box ({-total_length}e-6 {-width}e-6 {-height}e-6) ({0}e-6 {width}e-6 {height}e-6);")
            
            # Separator region
            content = content.replace(r"boxToCell.*?[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+.*?[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+",
                                    f"boxToCell\n{{\n    box ({0}e-6 {-width}e-6 {-height}e-6) ({sep_thickness}e-6 {width}e-6 {height}e-6);")
                                    
            with open(topo_set_path, 'w') as f:
                f.write(content)
                
    def _update_constants_parameters(self):
        """Update constants parameters for half-cell."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        # Update LiProperties for half-cell (similar to SPM but with region-specific values)
        for subdir in ["", "WE", "sep"]:
            li_props_path = os.path.join(self.case_path, "constant", subdir, "LiProperties")
            if os.path.exists(li_props_path):
                with open(li_props_path, 'r') as f:
                    content = f.read()
                    
                # Update parameters (region-specific values may differ)
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
                    
        # Update material selection in solveSolid.H for half-cell
        if self.solver_path:
            solve_solid_path = os.path.join(self.solver_path, "halfCellFoam", "solid", "solveSolid.H")
            if os.path.exists(solve_solid_path):
                with open(solve_solid_path, 'r') as f:
                    content = f.read()
                    
                if self.material_carbon.isChecked():
                    content = content.replace("#include \"OCV_Si.H\"", "//#include \"OCV_Si.H\"")
                    content = content.replace("//#include \"OCV_Gr.H\"", "#include \"OCV_Gr.H\"")
                else:
                    content = content.replace("#include \"OCV_Gr.H\"", "//#include \"OCV_Gr.H\"")
                    content = content.replace("//#include \"OCV_Si.H\"", "#include \"OCV_Si.H\"")
                    
                with open(solve_solid_path, 'w') as f:
                    f.write(content)
                    
    def _update_boundary_parameters(self):
        """Update boundary parameters for half-cell."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        # Update electrochemical parameters in boundary files
        # Update WE properties
        we_props_path = os.path.join(self.case_path, "0", "WE", "fai_s")
        if os.path.exists(we_props_path):
            with open(we_props_path, 'r') as f:
                content = f.read()
                
            j0 = self.j0_edit.text()
            cdl = self.cdl_edit.text()
            amf = self.we_amf_edit.text()
            
            # Update boundary condition parameters
            content = content.replace(r"j0[ ]+[0-9.e-]+", f"j0 {j0}")
            content = content.replace(r"cdl[ ]+[0-9.e-]+", f"cdl {cdl}")
            content = content.replace(r"amf[ ]+[0-9.e-]+", f"amf {amf}")
            
            with open(we_props_path, 'w') as f:
                f.write(content)
                
        # Update separator properties
        sep_props_path = os.path.join(self.case_path, "0", "sep", "Ce")
        if os.path.exists(sep_props_path):
            with open(sep_props_path, 'r') as f:
                content = f.read()
                
            porosity = self.sep_porosity_edit.text()
            content = content.replace(r"internalField[ ]+uniform[ ]+[0-9.e-]+", 
                                    f"internalField   uniform   {porosity}")
                                    
            with open(sep_props_path, 'w') as f:
                f.write(content)
                
    def _update_functions_parameters(self):
        """Update function parameters for half-cell."""
        # Similar to base class but may have region-specific settings
        super()._update_functions_parameters()
        
        # Update region-specific fvSchemes and fvSolution if needed
        if not self.case_path:
            raise ValueError("Case path not set")
            
        for subdir in ["WE", "sep"]:
            # Copy main fvSchemes and fvSolution to subdirectories if they don't exist
            main_schemes = os.path.join(self.case_path, "system", "fvSchemes")
            main_solution = os.path.join(self.case_path, "system", "fvSolution")
            subdir_schemes = os.path.join(self.case_path, "system", subdir, "fvSchemes")
            subdir_solution = os.path.join(self.case_path, "system", subdir, "fvSolution")
            
            if os.path.exists(main_schemes) and not os.path.exists(subdir_schemes):
                import shutil
                os.makedirs(os.path.dirname(subdir_schemes), exist_ok=True)
                shutil.copy2(main_schemes, subdir_schemes)
                shutil.copy2(main_solution, subdir_solution)
                
    def _on_run_clicked(self):
        """Override run to handle half-cell-specific workflow."""
        try:
            # Check if geometry needs to be regenerated
            self._check_and_regenerate_geometry()
            
            # Start simulation
            super()._on_run_clicked()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start half-cell simulation: {str(e)}")
            
    def _check_and_regenerate_geometry(self):
        """Check if geometry needs regeneration and do it if needed."""
        # Check if mesh files exist for both regions
        we_poly_mesh = os.path.join(self.case_path, "constant", "WE", "polyMesh")
        sep_poly_mesh = os.path.join(self.case_path, "constant", "sep", "polyMesh")
        
        if not os.path.exists(we_poly_mesh) or not os.path.exists(sep_poly_mesh):
            self.terminal_output.append("Mesh not found, regenerating half-cell geometry...")
            self._run_geometry_commands()
        else:
            # Check modification times to see if regeneration is needed
            self._run_geometry_commands()
            
    def _on_process_finished(self, exit_code: int):
        """Handle half-cell-specific process completion."""
        super()._on_process_finished(exit_code)
        
        if exit_code == 0:
            self.terminal_output.append("Half-cell simulation completed.")
            self.terminal_output.append("Use ParaView to visualize results in WE and separator regions.")
