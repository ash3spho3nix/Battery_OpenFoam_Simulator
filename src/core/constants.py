"""
Application constants and configuration.

This module contains all the constants used throughout the application,
migrated from the C++ implementation to maintain consistency.
"""

import os
from pathlib import Path

# Application metadata
APP_NAME = "BatteryFOAM"
APP_VERSION = "1.0.0"

# Supported simulation modules (equivalent to C++ radio buttons)
SUPPORTED_MODULES = {
    "SPM": "Single Particle Model",
    "halfCell": "P2D Model (Half Cell)",
    "fullCell": "P2D Model (Full Cell)"
}

# Module descriptions for UI
MODULE_DESCRIPTIONS = {
    "SPM": "Single Particle Model for battery simulation",
    "halfCell": "Pseudo-2D Model for half-cell configuration",
    "fullCell": "Pseudo-2D Model for full-cell configuration"
}

# Default paths (migrated from C++ project structure)
DEFAULT_PROJECT_PATH = os.path.expanduser("~")

# Path to UI files (equivalent to .ui files in C++)
UI_FILES_PATH = Path(__file__).parent.parent / "resources" / "ui"

# Path to OpenFOAM templates (equivalent to GUI/OpenfoamModule)
TEMPLATES_PATH = Path(__file__).parent.parent / "resources" / "templates"

# OpenFOAM solver names (from C++ Make/files)
SOLVER_NAMES = {
    "SPM": "SPMFoam_OF6",
    "halfCell": "halfCellFoam_OF6", 
    "fullCell": "fullCellFoam_OF6"
}

# File extensions and patterns
UI_FILE_EXTENSION = ".ui"
TEMPLATE_FILE_PATTERN = "*"

# Parameter file names (from C++ implementation)
PARAMETER_FILES = {
    "blockMeshDict": "system/blockMeshDict",
    "topoSetDict": "system/topoSetDict", 
    "LiProperties": "constant/LiProperties",
    "fvSchemes": "system/fvSchemes",
    "fvSolution": "system/fvSolution",
    "controlDict": "system/controlDict",
    "timeVoltage": "time_voltage"
}

# Geometry units (from C++ unit_select_box)
GEOMETRY_UNITS = {
    "micrometer": "1e-6",
    "millimeter": "1e-3", 
    "meter": "1e-0"
}

# Default parameter values (from C++ initialization)
DEFAULT_PARAMETERS = {
    "project_name": "project1",
    "length": 100.0,  # micrometers
    "width": 100.0,   # micrometers  
    "height": 100.0,  # micrometers
    "radius": 50.0,   # micrometers
    "unit": "micrometer",
    "x_division": 20,
    "y_division": 20,
    "z_division": 20,
    "DS_value": 1e-14,
    "CS_max": 30000,
    "kReact": 1e-11,
    "R": 8.314,
    "F": 96485,
    "Ce": 1000,
    "alphaA": 0.5,
    "alphaC": 0.5,
    "T_temp": 298.15,
    "I_app": 0.0,
    "initial_cs": 0.0,
    "endTime": 10.0,
    "deltaT": 0.1,
    "writeInterval": 1.0,
    "tolerance": 1e-6
}

# Solver scheme options (from C++ comboBoxes)
SCHEME_OPTIONS = {
    "ddtSchemes": ["Euler", "backward", "localEuler", "steadyState", "none"],
    "gradSchemes": ["Gauss linear", "Gauss cubic", "leastSquares", "none"],
    "divSchemes": ["bounded Gauss upwind", "none"],
    "laplacianSchemes": ["Gauss linear uncorrected", "Gauss linear corrected", 
                        "Gauss linear orthogonal", "none"],
    "interpolationSchemes": ["linear", "cubic", "none"]
}

# Material options (from C++ radio buttons)
MATERIAL_OPTIONS = {
    "carbon": "OCV_Gr.H",
    "silicon": "OCV_Si.H"
}

# Process control constants
PROCESS_TIMEOUT = 30000  # milliseconds
OUTPUT_BUFFER_SIZE = 1000  # lines

# File operation constants
MAX_RECENT_PROJECTS = 5
BACKUP_SUFFIX = ".backup"

# Error messages (migrated from C++ QMessageBox)
ERROR_MESSAGES = {
    "file_read": "Cannot open file for Reading",
    "file_write": "Cannot open file for Writing", 
    "invalid_path": "Path should not be empty",
    "invalid_name": "Project name should not be empty",
    "name_exists": "Cannot create the folder, because a file or folder with that name already exists",
    "invalid_project": "The folder you chose is invalid",
    "radius_too_large": "The radius should be smaller than the half of length & width & height",
    "solver_error": "Error during solver execution",
    "template_error": "Error copying template files"
}

# Success messages
SUCCESS_MESSAGES = {
    "project_created": "Create successfully",
    "parameters_modified": "Modify successfully", 
    "parameters_changed": "Change successfully",
    "solver_built": "Solver built successfully",
    "simulation_started": "Simulation started",
    "simulation_stopped": "Simulation stopped"
}

# Warning messages
WARNING_MESSAGES = {
    "end_time_mismatch": "It seems that the current 'Endtime' and/or 'Timestep' doesn't match your time_voltage file, please check!",
    "soc_limit": "SOC out of their limits!!",
    "voltage_limit": "Voltage cannot be lower than 0V!",
    "over_delithiated": "Over-delithiated!",
    "over_lithiated": "Over-lithiated!"
}

# UI Widget Names (extracted from .ui files)
UI_WIDGET_NAMES = {
    "main_window": {
        "intro_browser": "intro_browser",
        "label_pic_vertical": "label_pic_vertical",
        "tab_widget": "tabWidget",
        "carbon_button": "carbon_button",
        "halfcell_button": "halfCell_button",
        "fullcell_button": "fullCell_button",
        "project_name_edit": "pro_name_editline",
        "project_path_label": "main_path_label",
        "project_path_button": "main_path_button",
        "project_next_button": "main_next_button",
        "project_name_hint": "main_name_hint"
    },
    "carbon_interface": {
        "unit_select_box": "unit_select_box",
        "length_line_edit": "length_lineEdit",
        "width_line_edit": "width_lineEdit",
        "height_line_edit": "height_lineEdit",
        "radius_line_edit": "radius_lineEdit",
        "x_divide_line_edit": "x_divide_lineEdit",
        "y_divide_line_edit": "y_divide_lineEdit",
        "z_divide_line_edit": "z_divide_lineEdit",
        "change_geometry_button": "change_geometry_button",
        "run_geometry_button": "run_geometry_button",
        "ds_line_edit": "DS_lineEdit",
        "cs_line_edit": "CS_lineEdit",
        "kreact_line_edit": "KReact_lineEdit",
        "r_line_edit": "R_lineEdit",
        "f_line_edit": "F_lineEdit",
        "ce_line_edit": "Ce_lineEdit",
        "alphaa_line_edit": "alphaA_lineEdit",
        "alphac_line_edit": "alphaC_lineEdit",
        "temp_line_edit": "Temp_lineEdit",
        "i_line_edit": "I_lineEdit",
        "select_charge": "select_charge",
        "select_discharge": "select_discharge",
        "select_carbon": "select_carbon",
        "select_silicon": "select_silicon",
        "change_constant_button": "change_constant_button",
        "run_constant_button": "run_constant_button",
        "help_constant_button": "help_constant_button",
        "initial_cs_line_edit": "initial_cs_lineEdit",
        "change_boundary_button": "change_boundary_button",
        "run_boundary_button": "run_boundary_button",
        "derivative_combo_box": "derivative_comboBox",
        "gradient_combo_box": "gardient_comboBox",
        "divergence_combo_box": "divergence_comboBox",
        "laplacian_combo_box": "laplacian_comboBox",
        "interpolation_combo_box": "interpolation_comboBox",
        "change_function_button": "change_function_button",
        "run_function_button": "run_function_button",
        "tolerance_line_edit": "tolerance_lineEdit",
        "endtime_line_edit": "endtime_lineEdit",
        "timestep_line_edit": "timestep_lineEdit",
        "interval_line_edit": "interval_lineEdit",
        "change_control_button": "change_control_button",
        "run_button": "run_button",
        "pause_run_button": "pause_run_button",
        "open_paraview_button": "open_paraview_Button",
        "view_result_button": "view_result_button",
        "c_back_button": "c_back_Button",
        "terminal_output_window": "terminal_output_window",
        "command_input_line_edit": "command_input_lineEdit",
        "push_button": "pushButton"
    },
    "result_interface": {
        "custom_plot": "customPlot",
        "voltage_button": "voltage_button",
        "file_path_label": "file_path_label",
        "choose_file_button": "choose_file_button",
        "view_another_button": "view_another_button",
        "combo_box_x": "comboBox_x",
        "combo_box_y": "comboBox_y"
    }
}

# UI Tab Titles (from .ui files)
UI_TAB_TITLES = {
    "main_window": {
        "new_tab": "New",
        "open_tab": "Open"
    },
    "carbon_interface": {
        "geometry_tab": "Geometry->",
        "constant_tab": "Constant->",
        "initial_condition_tab": "Initial condition->",
        "discretization_tab": "Discretization->",
        "control_tab": "Control"
    },
    "result_interface": {
        "voltage_plot_tab": "Voltage-time plot",
        "results_tab": "Results",
        "visualization_tab": "Visualization",
        "terminal_tab": "Terminal"
    }
}

# UI Default Values (from .ui files)
UI_DEFAULT_VALUES = {
    "main_window": {
        "project_name": "project1",
        "tab_index": 0
    },
    "carbon_interface": {
        "unit_index": 0,  # micrometer(um)
        "material_index": 0,  # Graphite
        "direction_index": 0,  # Charge
        "derivative_index": 0,  # Euler
        "gradient_index": 0,  # Gauss linear
        "divergence_index": 0,  # bounded Gauss upwind
        "laplacian_index": 0,  # Gauss linear uncorrected
        "interpolation_index": 0  # linear
    }
}
