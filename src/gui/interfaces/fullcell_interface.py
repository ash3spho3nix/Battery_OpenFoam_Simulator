"""
Full-Cell Interface for P2D Full-Cell Model.

This module provides the FullCellInterface class, which implements the
P2D full-cell simulation interface with functionality for anode, cathode,
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


class FullCellInterface(BaseInterface):
    """
    Interface for P2D Full-Cell simulations.
    
    Provides functionality for full-cell simulations with anode, cathode,
    and separator regions, including advanced electrochemical modeling.
    """
    
    def __init__(
        self, 
        parent: Optional[QWidget] = None, 
        ui_config: Optional['UIConfig'] = None
    ):
        """
        Initialize the Full-Cell interface.
        
        Args:
            parent: Parent widget
            ui_config: UI configuration for loading mode
        """
        super().__init__(parent, ui_config)
        self.interface_type = "fullcell"
        self.setWindowTitle("BatteryFOAM - P2D Full-Cell Interface")
        
    def _add_boundary_configuration(self, layout: QVBoxLayout):
        """Add full-cell-specific boundary configuration."""
        # Full-cell has the most complex boundary conditions
        boundary_group = QGroupBox("Boundary Conditions")
        boundary_layout = QVBoxLayout()
        
        # Anode parameters
        anode_group = QGroupBox("Anode")
        anode_layout = QVBoxLayout()
        
        # Anode thickness
        anode_thickness_layout = QHBoxLayout()
        self.anode_thickness_edit = QLineEdit("100")  # Default 100 μm
        anode_thickness_layout.addWidget(QLabel("Anode Thickness (μm):"))
        anode_thickness_layout.addWidget(self.anode_thickness_edit)
        anode_layout.addLayout(anode_thickness_layout)
        
        # Anode active material fraction
        anode_amf_layout = QHBoxLayout()
        self.anode_amf_edit = QLineEdit("0.5")  # Default 50%
        anode_amf_layout.addWidget(QLabel("Anode AM Fraction:"))
        anode_amf_layout.addWidget(self.anode_amf_edit)
        anode_layout.addLayout(anode_amf_layout)
        
        # Anode material selection
        anode_material_layout = QHBoxLayout()
        self.anode_material_combo = QComboBox()
        self.anode_material_combo.addItems(["Graphite (Gr)", "Silicon (Si)", "LFP", "NCA", "LionSimba"])
        self.anode_material_combo.setCurrentText("Graphite (Gr)")
        anode_material_layout.addWidget(QLabel("Anode Material:"))
        anode_material_layout.addWidget(self.anode_material_combo)
        anode_layout.addLayout(anode_material_layout)
        
        anode_group.setLayout(anode_layout)
        boundary_layout.addWidget(anode_group)
        
        # Cathode parameters
        cathode_group = QGroupBox("Cathode")
        cathode_layout = QVBoxLayout()
        
        # Cathode thickness
        cathode_thickness_layout = QHBoxLayout()
        self.cathode_thickness_edit = QLineEdit("100")  # Default 100 μm
        cathode_thickness_layout.addWidget(QLabel("Cathode Thickness (μm):"))
        cathode_thickness_layout.addWidget(self.cathode_thickness_edit)
        cathode_layout.addLayout(cathode_thickness_layout)
        
        # Cathode active material fraction
        cathode_amf_layout = QHBoxLayout()
        self.cathode_amf_edit = QLineEdit("0.5")  # Default 50%
        cathode_amf_layout.addWidget(QLabel("Cathode AM Fraction:"))
        cathode_amf_layout.addWidget(self.cathode_amf_edit)
        cathode_layout.addLayout(cathode_amf_layout)
        
        # Cathode material selection
        cathode_material_layout = QHBoxLayout()
        self.cathode_material_combo = QComboBox()
        self.cathode_material_combo.addItems(["LFP", "NCA", "LionSimba", "Graphite (Gr)", "Silicon (Si)"])
        self.cathode_material_combo.setCurrentText("LFP")
        cathode_material_layout.addWidget(QLabel("Cathode Material:"))
        cathode_material_layout.addWidget(self.cathode_material_combo)
        cathode_layout.addLayout(cathode_material_layout)
        
        cathode_group.setLayout(cathode_layout)
        boundary_layout.addWidget(cathode_group)
        
        # Separator parameters
        sep_group = QGroupBox("Separator")
        sep_layout = QVBoxLayout()
        
        # Separator thickness
        sep_thickness_layout = QHBoxLayout()
        self.sep_thickness_edit = QLineEdit("25")  # Default 25 μm
        sep_thickness_layout.addWidget(QLabel("Separator Thickness (μm):"))
        sep_thickness_layout.addWidget(self.sep_thickness_edit)
        sep_layout.addLayout(sep_thickness_layout)
        
        # Separator porosity
        sep_porosity_layout = QHBoxLayout()
        self.sep_porosity_edit = QLineEdit("0.5")  # Default 50%
        sep_porosity_layout.addWidget(QLabel("Separator Porosity:"))
        sep_porosity_layout.addWidget(self.sep_porosity_edit)
        sep_layout.addLayout(sep_porosity_layout)
        
        sep_group.setLayout(sep_layout)
        boundary_layout.addWidget(sep_group)
        
        # Electrochemical parameters
        electrochem_group = QGroupBox("Electrochemical Parameters")
        electrochem_layout = QVBoxLayout()
        
        # Exchange current density for anode and cathode
        j0_layout = QHBoxLayout()
        self.anode_j0_edit = QLineEdit("1e-4")  # Default exchange current density
        self.cathode_j0_edit = QLineEdit("1e-4")
        j0_layout.addWidget(QLabel("Anode j0:"))
        j0_layout.addWidget(self.anode_j0_edit)
        j0_layout.addWidget(QLabel("Cathode j0:"))
        j0_layout.addWidget(self.cathode_j0_edit)
        electrochem_layout.addLayout(j0_layout)
        
        # Double layer capacitance
        cdl_layout = QHBoxLayout()
        self.anode_cdl_edit = QLineEdit("0.1")  # Default double layer capacitance
        self.cathode_cdl_edit = QLineEdit("0.1")
        cdl_layout.addWidget(QLabel("Anode Cdl:"))
        cdl_layout.addWidget(self.anode_cdl_edit)
        cdl_layout.addWidget(QLabel("Cathode Cdl:"))
        cdl_layout.addWidget(self.cathode_cdl_edit)
        electrochem_layout.addLayout(cdl_layout)
        
        electrochem_group.setLayout(electrochem_layout)
        boundary_layout.addWidget(electrochem_group)
        
        boundary_group.setLayout(boundary_layout)
        layout.addWidget(boundary_group)
        
    def _update_geometry_parameters(self):
        """Update geometry parameters for full-cell."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        # Update blockMeshDict for full-cell geometry
        block_mesh_path = os.path.join(self.case_path, "system", "blockMeshDict")
        if os.path.exists(block_mesh_path):
            with open(block_mesh_path, 'r') as f:
                content = f.read()
                
            # Get dimensions (full-cell specific)
            anode_thickness = float(self.anode_thickness_edit.text()) / 2.0
            sep_thickness = float(self.sep_thickness_edit.text()) / 2.0
            cathode_thickness = float(self.cathode_thickness_edit.text()) / 2.0
            width = float(self.width_edit.text()) / 2.0
            height = float(self.height_edit.text()) / 2.0
            
            # Total length is anode + separator + cathode
            total_length = anode_thickness + sep_thickness + cathode_thickness
            
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
            
            # Update vertex coordinates for full-cell (8 vertices)
            coords = [
                f"({-total_length} {-width} {-height})",  # Anode start
                f"({-total_length} {width} {-height})",
                f"({-total_length} {width} {height})",
                f"({-total_length} {-width} {height})",
                f"({-sep_thickness - cathode_thickness} {-width} {-height})",  # Anode/separator interface
                f"({-sep_thickness - cathode_thickness} {width} {-height})",
                f"({-sep_thickness - cathode_thickness} {width} {height})",
                f"({-sep_thickness - cathode_thickness} {-width} {height})"
            ]
            
            # Replace vertex coordinates (simplified - would need more robust parsing)
            for i, coord in enumerate(coords):
                # This is a simplified replacement - would need more robust parsing
                content = content.replace(f"({[-total_length, -total_length, -total_length, -total_length, -sep_thickness-cathode_thickness, -sep_thickness-cathode_thickness, -sep_thickness-cathode_thickness, -sep_thickness-cathode_thickness][i]} {[-width, width, width, -width, -width, width, width, -width][i]} {[-height, -height, height, height, -height, -height, height, height][i]})", coord)
                
            # Update divisions
            x_div = self.x_div_edit.value()
            y_div = self.y_div_edit.value()
            z_div = self.z_div_edit.value()
            content = content.replace(r"[0-9]+ [0-9]+ [0-9+]", f"{x_div} {y_div} {z_div}")
            
            with open(block_mesh_path, 'w') as f:
                f.write(content)
                
        # Update topoSetDict for full-cell regions
        topo_set_path = os.path.join(self.case_path, "system", "topoSetDict")
        if os.path.exists(topo_set_path):
            with open(topo_set_path, 'r') as f:
                content = f.read()
                
            # Update box coordinates for anode, separator, and cathode regions
            # Anode region
            content = content.replace(r"boxToCell.*?[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+.*?[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+",
                                    f"boxToCell\n{{\n    box ({-total_length}e-6 {-width}e-6 {-height}e-6) ({-sep_thickness-cathode_thickness}e-6 {width}e-6 {height}e-6);")
            
            # Separator region
            content = content.replace(r"boxToCell.*?[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+.*?[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+",
                                    f"boxToCell\n{{\n    box ({-sep_thickness-cathode_thickness}e-6 {-width}e-6 {-height}e-6) ({-cathode_thickness}e-6 {width}e-6 {height}e-6);")
            
            # Cathode region
            content = content.replace(r"boxToCell.*?[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+.*?[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+ [ ]+[-]?[0-9.e-]+",
                                    f"boxToCell\n{{\n    box ({-cathode_thickness}e-6 {-width}e-6 {-height}e-6) ({0}e-6 {width}e-6 {height}e-6);")
                                    
            with open(topo_set_path, 'w') as f:
                f.write(content)
                
    def _update_constants_parameters(self):
        """Update constants parameters for full-cell."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        # Update LiProperties for each region (anode, cathode, separator)
        for subdir in ["", "anode", "cathode", "sep"]:
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
                    
        # Update material selection in solveSolid.H for full-cell
        if self.solver_path:
            solve_solid_path = os.path.join(self.solver_path, "fullCellFoam", "solid", "solveSolid.H")
            if os.path.exists(solve_solid_path):
                with open(solve_solid_path, 'r') as f:
                    content = f.read()
                    
                # Update anode material
                anode_material = self.anode_material_combo.currentText()
                if "Graphite" in anode_material:
                    content = content.replace("#include \"OCV_Si.H\"", "//#include \"OCV_Si.H\"")
                    content = content.replace("//#include \"OCV_Gr.H\"", "#include \"OCV_Gr.H\"")
                    content = content.replace("#include \"OCV_LFP.H\"", "//#include \"OCV_LFP.H\"")
                    content = content.replace("#include \"OCV_NCA.H\"", "//#include \"OCV_NCA.H\"")
                    content = content.replace("#include \"OCV_LionSimba_cathode.H\"", "//#include \"OCV_LionSimba_cathode.H\"")
                elif "Silicon" in anode_material:
                    content = content.replace("#include \"OCV_Gr.H\"", "//#include \"OCV_Gr.H\"")
                    content = content.replace("//#include \"OCV_Si.H\"", "#include \"OCV_Si.H\"")
                    content = content.replace("#include \"OCV_LFP.H\"", "//#include \"OCV_LFP.H\"")
                    content = content.replace("#include \"OCV_NCA.H\"", "//#include \"OCV_NCA.H\"")
                    content = content.replace("#include \"OCV_LionSimba_cathode.H\"", "//#include \"OCV_LionSimba_cathode.H\"")
                    
                # Update cathode material
                cathode_material = self.cathode_material_combo.currentText()
                if "LFP" in cathode_material:
                    content = content.replace("#include \"OCV_Gr.H\"", "//#include \"OCV_Gr.H\"")
                    content = content.replace("#include \"OCV_Si.H\"", "//#include \"OCV_Si.H\"")
                    content = content.replace("//#include \"OCV_LFP.H\"", "#include \"OCV_LFP.H\"")
                    content = content.replace("#include \"OCV_NCA.H\"", "//#include \"OCV_NCA.H\"")
                    content = content.replace("#include \"OCV_LionSimba_cathode.H\"", "//#include \"OCV_LionSimba_cathode.H\"")
                elif "NCA" in cathode_material:
                    content = content.replace("#include \"OCV_Gr.H\"", "//#include \"OCV_Gr.H\"")
                    content = content.replace("#include \"OCV_Si.H\"", "//#include \"OCV_Si.H\"")
                    content = content.replace("#include \"OCV_LFP.H\"", "//#include \"OCV_LFP.H\"")
                    content = content.replace("//#include \"OCV_NCA.H\"", "#include \"OCV_NCA.H\"")
                    content = content.replace("#include \"OCV_LionSimba_cathode.H\"", "//#include \"OCV_LionSimba_cathode.H\"")
                elif "LionSimba" in cathode_material:
                    content = content.replace("#include \"OCV_Gr.H\"", "//#include \"OCV_Gr.H\"")
                    content = content.replace("#include \"OCV_Si.H\"", "//#include \"OCV_Si.H\"")
                    content = content.replace("#include \"OCV_LFP.H\"", "//#include \"OCV_LFP.H\"")
                    content = content.replace("#include \"OCV_NCA.H\"", "//#include \"OCV_NCA.H\"")
                    content = content.replace("//#include \"OCV_LionSimba_cathode.H\"", "#include \"OCV_LionSimba_cathode.H\"")
                    
                with open(solve_solid_path, 'w') as f:
                    f.write(content)
                    
    def _update_boundary_parameters(self):
        """Update boundary parameters for full-cell."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        # Update electrochemical parameters in boundary files for each region
        # Update anode properties
        anode_props_path = os.path.join(self.case_path, "0", "anode", "fai_s")
        if os.path.exists(anode_props_path):
            with open(anode_props_path, 'r') as f:
                content = f.read()
                
            j0 = self.anode_j0_edit.text()
            cdl = self.anode_cdl_edit.text()
            amf = self.anode_amf_edit.text()
            
            # Update boundary condition parameters
            content = content.replace(r"j0[ ]+[0-9.e-]+", f"j0 {j0}")
            content = content.replace(r"cdl[ ]+[0-9.e-]+", f"cdl {cdl}")
            content = content.replace(r"amf[ ]+[0-9.e-]+", f"amf {amf}")
            
            with open(anode_props_path, 'w') as f:
                f.write(content)
                
        # Update cathode properties
        cathode_props_path = os.path.join(self.case_path, "0", "cathode", "fai_s")
        if os.path.exists(cathode_props_path):
            with open(cathode_props_path, 'r') as f:
                content = f.read()
                
            j0 = self.cathode_j0_edit.text()
            cdl = self.cathode_cdl_edit.text()
            amf = self.cathode_amf_edit.text()
            
            # Update boundary condition parameters
            content = content.replace(r"j0[ ]+[0-9.e-]+", f"j0 {j0}")
            content = content.replace(r"cdl[ ]+[0-9.e-]+", f"cdl {cdl}")
            content = content.replace(r"amf[ ]+[0-9.e-]+", f"amf {amf}")
            
            with open(cathode_props_path, 'w') as f:
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
        """Update function parameters for full-cell."""
        # Similar to base class but may have region-specific settings
        super()._update_functions_parameters()
        
        # Update region-specific fvSchemes and fvSolution if needed
        if not self.case_path:
            raise ValueError("Case path not set")
            
        for subdir in ["anode", "cathode", "sep"]:
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
        """Override run to handle full-cell-specific workflow."""
        try:
            # Check if geometry needs to be regenerated
            self._check_and_regenerate_geometry()
            
            # Start simulation
            super()._on_run_clicked()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start full-cell simulation: {str(e)}")
            
    def _check_and_regenerate_geometry(self):
        """Check if geometry needs regeneration and do it if needed."""
        # Check if mesh files exist for all regions
        anode_poly_mesh = os.path.join(self.case_path, "constant", "anode", "polyMesh")
        cathode_poly_mesh = os.path.join(self.case_path, "constant", "cathode", "polyMesh")
        sep_poly_mesh = os.path.join(self.case_path, "constant", "sep", "polyMesh")
        
        if (not os.path.exists(anode_poly_mesh) or 
            not os.path.exists(cathode_poly_mesh) or 
            not os.path.exists(sep_poly_mesh)):
            self.terminal_output.append("Mesh not found, regenerating full-cell geometry...")
            self._run_geometry_commands()
        else:
            # Check modification times to see if regeneration is needed
            self._run_geometry_commands()
            
    def _on_process_finished(self, exit_code: int):
        """Handle full-cell-specific process completion."""
        super()._on_process_finished(exit_code)
        
        if exit_code == 0:
            self.terminal_output.append("Full-cell simulation completed.")
            self.terminal_output.append("Use ParaView to visualize results in anode, cathode, and separator regions.")
