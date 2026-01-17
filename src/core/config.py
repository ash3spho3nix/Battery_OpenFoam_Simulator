"""
Application configuration and constants.

This module contains application configuration and constants that can be imported
without causing circular dependencies. It separates core configuration from business logic.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List
from pathlib import Path
import json
import os


class SimulationModule(Enum):
    """
    Supported simulation modules.
    
    Defines the different simulation modules available in the application.
    """
    SPM = "SPM"              # Single Particle Model
    HALF_CELL = "halfCell"   # P2D Half Cell
    FULL_CELL = "fullCell"   # P2D Full Cell


@dataclass
class ApplicationConfig:
    """
    Application configuration settings.
    
    Contains all application-wide configuration that can be safely imported
    without causing circular dependencies.
    """
    app_name: str = "BatteryFOAM"
    app_version: str = "1.0.0"
    default_project_path: str = "~"
    ui_files_path: str = "resources/ui/files"
    templates_path: str = "resources/templates"
    
    @property
    def resolved_default_path(self) -> str:
        """Get resolved default project path."""
        return str(Path(self.default_project_path).expanduser())
    
    @property
    def ui_files_path_resolved(self) -> str:
        """Get resolved UI files path."""
        return str(Path(self.ui_files_path))
    
    @property
    def templates_path_resolved(self) -> str:
        """Get resolved templates path."""
        return str(Path(self.templates_path))


class ConfigManager:
    """
    Configuration manager for application settings.
    
    Provides centralized access to application configuration and constants
    without causing circular imports.
    """
    
    def __init__(self):
        self.app_config = ApplicationConfig()
    
    def get_app_name(self) -> str:
        """Get application name."""
        return self.app_config.app_name
    
    def get_app_version(self) -> str:
        """Get application version."""
        return self.app_config.app_version
    
    def get_default_project_path(self) -> str:
        """Get default project path."""
        return self.app_config.resolved_default_path
    
    def get_ui_files_path(self) -> str:
        """Get UI files path."""
        return self.app_config.ui_files_path_resolved
    
    def get_templates_path(self) -> str:
        """Get templates path."""
        return self.app_config.templates_path_resolved
    
    def get_supported_modules(self) -> Dict[str, str]:
        """Get supported simulation modules."""
        return SUPPORTED_MODULES.copy()
    
    def get_solver_name(self, module: str) -> str:
        """Get solver name for a module."""
        return SOLVER_NAMES.get(module, "")
    
    def get_parameter_file(self, file_type: str) -> str:
        """Get parameter file path for a type."""
        return PARAMETER_FILES.get(file_type, "")
    
    def get_default_parameter(self, param_name: str) -> Any:
        """Get default value for a parameter."""
        return DEFAULT_PARAMETERS.get(param_name)


# Application metadata
APP_NAME = "BatteryFOAM"
APP_VERSION = "1.0.0"

# Supported simulation modules
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

# Default paths
DEFAULT_PROJECT_PATH = str(Path("~").expanduser())

# Path to UI files (equivalent to .ui files in C++)
UI_FILES_PATH = str(Path("resources/ui"))

# Path to OpenFOAM templates (equivalent to GUI/OpenfoamModule)
TEMPLATES_PATH = str(Path("resources/templates"))

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


class UserConfig:
    """
    User configuration manager for persistent settings.
    
    Handles saving and loading user preferences like project paths,
    recent projects, and custom parameter defaults.
    """
    
    def __init__(self):
        self.config_dir = Path.home() / ".batteryfoam"
        self.config_file = self.config_dir / "user_config.json"
        self._ensure_config_dir()
        self._config = self._load_config()
    
    def _ensure_config_dir(self):
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load user config: {e}")
                return self._get_default_config()
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "last_project_path": str(Path.home()),
            "recent_projects": [],
            "custom_defaults": {}
        }
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save user config: {e}")
    
    def get_last_project_path(self) -> str:
        """Get the last used project path."""
        return self._config.get("last_project_path", str(Path.home()))
    
    def set_last_project_path(self, path: str):
        """Set the last used project path."""
        self._config["last_project_path"] = path
        self.save_config()
    
    def get_recent_projects(self) -> List[str]:
        """Get list of recent projects."""
        return self._config.get("recent_projects", [])
    
    def add_recent_project(self, project_path: str):
        """Add a project to recent projects list."""
        recent = self._config.get("recent_projects", [])
        if project_path in recent:
            recent.remove(project_path)
        recent.insert(0, project_path)
        # Keep only the most recent MAX_RECENT_PROJECTS
        self._config["recent_projects"] = recent[:MAX_RECENT_PROJECTS]
        self.save_config()
    
    def get_custom_default(self, key: str) -> Any:
        """Get a custom default value."""
        return self._config.get("custom_defaults", {}).get(key)
    
    def set_custom_default(self, key: str, value: Any):
        """Set a custom default value."""
        if "custom_defaults" not in self._config:
            self._config["custom_defaults"] = {}
        self._config["custom_defaults"][key] = value
        self.save_config()


# Global configuration manager instance
_config_manager = None
_user_config = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_user_config() -> UserConfig:
    """Get the global user configuration instance."""
    global _user_config
    if _user_config is None:
        _user_config = UserConfig()
    return _user_config