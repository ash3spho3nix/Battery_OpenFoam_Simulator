"""
Base interface class for Battery Simulator interfaces.

This module provides the BaseInterface class, which serves as the foundation
for all simulation interfaces (Carbon, HalfCell, FullCell, Result).
It handles common functionality like UI loading, process control, and
parameter management.
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

from ...openfoam.process_controller import ProcessController
from ...openfoam.solver_manager import OpenFOAMSolverManager
from ...utils.parameter_parser import ParameterManager
from ...utils.file_operations import TemplateManager
from ...core.constants import (
    ERROR_MESSAGES, SUCCESS_MESSAGES, WARNING_MESSAGES,
    PARAMETER_FILES, DEFAULT_PARAMETERS, SCHEME_OPTIONS
)


class BaseInterface(QWidget):
    """
    Base class for all simulation interfaces.
    
    Provides common functionality for UI loading, process control,
    parameter management, and file operations.
    """
    
    # Signals for interface events
    exit_signal = pyqtSignal()
    simulation_started = pyqtSignal()
    simulation_stopped = pyqtSignal()
    simulation_paused = pyqtSignal()
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    
    def __init__(
        self, 
        parent: Optional[QWidget] = None, 
        ui_config: Optional['UIConfig'] = None
    ):
        """
        Initialize the base interface.
        
        Args:
            parent: Parent widget
            ui_config: UI configuration for loading mode
        """
        super().__init__(parent)
        
        self.ui_config = ui_config
        self.interface_type = self.__class__.__name__.lower().replace('interface', '')
        
        # Initialize core components
        self.process_controller = ProcessController()
        self.solver_manager = None
        self.parameter_manager = None  # Initialize as None, will be set after project_path
        self.template_manager = TemplateManager(self._get_templates_path())
        
        # UI components
        self.tab_widget = None
        self.terminal_output = None
        self.command_input = None
        
        # Interface state
        self.project_path = None
        self.project_name = None
        self.case_path = None
        self.solver_path = None
        
        # Process state
        self.simulation_running = False
        self.simulation_paused = False
        
        # Connect signals
        self._connect_signals()
        
        # Setup UI
        self._setup_ui()
        
    def _connect_signals(self):
        """Connect process controller signals to handlers."""
        self.process_controller.output_received.connect(self._on_process_output)
        self.process_controller.error_received.connect(self._on_process_error)
        self.process_controller.process_started.connect(self._on_process_started)
        self.process_controller.process_finished.connect(self._on_process_finished)
        
    def _setup_ui(self):
        """Setup the base interface UI structure."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different sections
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # Add common tabs
        self._create_geometry_tab()
        self._create_constants_tab()
        self._create_boundary_tab()
        self._create_functions_tab()
        self._create_control_tab()
        self._create_terminal_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Set window properties
        self.setWindowTitle(f"BatteryFOAM - {self.interface_type.title()} Interface")
        self.setMinimumSize(1000, 700)
        
    def _create_geometry_tab(self):
        """Create the geometry configuration tab."""
        geometry_tab = QWidget()
        layout = QVBoxLayout(geometry_tab)
        
        # Title
        title_label = QLabel("Geometry Configuration")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Geometry parameters group
        geometry_group = QGroupBox("Geometry Parameters")
        geometry_layout = QVBoxLayout()
        
        # Dimensions
        dims_layout = QHBoxLayout()
        self.length_edit = QLineEdit(str(DEFAULT_PARAMETERS["length"]))
        self.width_edit = QLineEdit(str(DEFAULT_PARAMETERS["width"]))
        self.height_edit = QLineEdit(str(DEFAULT_PARAMETERS["height"]))
        
        dims_layout.addWidget(QLabel("Length (μm):"))
        dims_layout.addWidget(self.length_edit)
        dims_layout.addWidget(QLabel("Width (μm):"))
        dims_layout.addWidget(self.width_edit)
        dims_layout.addWidget(QLabel("Height (μm):"))
        dims_layout.addWidget(self.height_edit)
        geometry_layout.addLayout(dims_layout)
        
        # Divisions
        div_layout = QHBoxLayout()
        self.x_div_edit = QSpinBox()
        self.y_div_edit = QSpinBox()
        self.z_div_edit = QSpinBox()
        self.x_div_edit.setValue(DEFAULT_PARAMETERS["x_division"])
        self.y_div_edit.setValue(DEFAULT_PARAMETERS["y_division"])
        self.z_div_edit.setValue(DEFAULT_PARAMETERS["z_division"])
        
        div_layout.addWidget(QLabel("X divisions:"))
        div_layout.addWidget(self.x_div_edit)
        div_layout.addWidget(QLabel("Y divisions:"))
        div_layout.addWidget(self.y_div_edit)
        div_layout.addWidget(QLabel("Z divisions:"))
        div_layout.addWidget(self.z_div_edit)
        geometry_layout.addLayout(div_layout)
        
        # Radius (for particle models)
        radius_layout = QHBoxLayout()
        self.radius_edit = QLineEdit(str(DEFAULT_PARAMETERS["radius"]))
        radius_layout.addWidget(QLabel("Particle radius (μm):"))
        radius_layout.addWidget(self.radius_edit)
        geometry_layout.addLayout(radius_layout)
        
        # Units
        unit_layout = QHBoxLayout()
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["micrometer (μm)", "millimeter (mm)", "meter (m)"])
        self.unit_combo.setCurrentText(DEFAULT_PARAMETERS["unit"])
        unit_layout.addWidget(QLabel("Units:"))
        unit_layout.addWidget(self.unit_combo)
        geometry_layout.addLayout(unit_layout)
        
        geometry_group.setLayout(geometry_layout)
        layout.addWidget(geometry_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.change_geometry_button = QPushButton("Change Geometry")
        self.change_geometry_button.clicked.connect(self._on_change_geometry_clicked)
        self.run_geometry_button = QPushButton("Run Geometry")
        self.run_geometry_button.clicked.connect(self._on_run_geometry_clicked)
        self.view_geometry_button = QPushButton("View Geometry")
        self.view_geometry_button.clicked.connect(self._on_view_geometry_clicked)
        
        button_layout.addWidget(self.change_geometry_button)
        button_layout.addWidget(self.run_geometry_button)
        button_layout.addWidget(self.view_geometry_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.tab_widget.addTab(geometry_tab, "Geometry")
        
    def _create_constants_tab(self):
        """Create the constants configuration tab."""
        constants_tab = QWidget()
        layout = QVBoxLayout(constants_tab)
        
        # Title
        title_label = QLabel("Constants Configuration")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Scroll area for parameters
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Material properties group
        material_group = QGroupBox("Material Properties")
        material_layout = QVBoxLayout()
        
        # Electrochemical parameters
        param_layout = QVBoxLayout()
        self.param_edits = {}
        
        params = [
            ("DS_value", "Li Intrinsic diffusivity in material"),
            ("CS_max", "Maximum Li concentration in material"),
            ("kReact", "Reaction rate constant"),
            ("R", "Universal gas constant"),
            ("F", "Faraday's constant"),
            ("Ce", "Electrolyte concentration"),
            ("alphaA", "Anodic transfer coefficient"),
            ("alphaC", "Cathodic transfer coefficient"),
            ("T_temp", "Temperature (K)"),
            ("I_app", "Applied current density"),
            ("initial_cs", "Initial Cs value")
        ]
        
        for param, description in params:
            row_layout = QHBoxLayout()
            edit = QLineEdit(str(DEFAULT_PARAMETERS.get(param.lower(), 0.0)))
            self.param_edits[param] = edit
            row_layout.addWidget(QLabel(f"{param}:"))
            row_layout.addWidget(edit)
            row_layout.addWidget(QLabel(description))
            param_layout.addLayout(row_layout)
            
        material_layout.addLayout(param_layout)
        material_group.setLayout(material_layout)
        scroll_layout.addWidget(material_group)
        
        # Material selection
        material_select_layout = QHBoxLayout()
        self.material_carbon = QRadioButton("Carbon (Gr)")
        self.material_silicon = QRadioButton("Silicon (Si)")
        self.material_carbon.setChecked(True)
        material_select_layout.addWidget(QLabel("Material:"))
        material_select_layout.addWidget(self.material_carbon)
        material_select_layout.addWidget(self.material_silicon)
        scroll_layout.addLayout(material_select_layout)
        
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.change_constants_button = QPushButton("Change Constants")
        self.change_constants_button.clicked.connect(self._on_change_constants_clicked)
        self.run_constants_button = QPushButton("Run Constants")
        self.run_constants_button.clicked.connect(self._on_run_constants_clicked)
        self.help_constants_button = QPushButton("Help")
        self.help_constants_button.clicked.connect(self._on_help_constants_clicked)
        
        button_layout.addWidget(self.change_constants_button)
        button_layout.addWidget(self.run_constants_button)
        button_layout.addWidget(self.help_constants_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.tab_widget.addTab(constants_tab, "Constants")
        
    def _create_boundary_tab(self):
        """Create the boundary conditions tab."""
        boundary_tab = QWidget()
        layout = QVBoxLayout(boundary_tab)
        
        # Title
        title_label = QLabel("Boundary Conditions")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Boundary configuration (implementation specific to each interface)
        self._add_boundary_configuration(layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.change_boundary_button = QPushButton("Change Boundary")
        self.change_boundary_button.clicked.connect(self._on_change_boundary_clicked)
        self.run_boundary_button = QPushButton("Run Boundary")
        self.run_boundary_button.clicked.connect(self._on_run_boundary_clicked)
        
        button_layout.addWidget(self.change_boundary_button)
        button_layout.addWidget(self.run_boundary_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.tab_widget.addTab(boundary_tab, "Boundary")
        
    def _create_functions_tab(self):
        """Create the solver functions tab."""
        functions_tab = QWidget()
        layout = QVBoxLayout(functions_tab)
        
        # Title
        title_label = QLabel("Solver Functions")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Discretization schemes
        schemes_group = QGroupBox("Discretization Schemes")
        schemes_layout = QVBoxLayout()
        
        for scheme_type, options in SCHEME_OPTIONS.items():
            row_layout = QHBoxLayout()
            combo = QComboBox()
            combo.addItems(options)
            combo.setCurrentText(DEFAULT_PARAMETERS.get(scheme_type, options[0]))
            setattr(self, f"{scheme_type.lower()}_combo", combo)
            row_layout.addWidget(QLabel(f"{scheme_type}:"))
            row_layout.addWidget(combo)
            schemes_layout.addLayout(row_layout)
            
        schemes_group.setLayout(schemes_layout)
        layout.addWidget(schemes_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.change_functions_button = QPushButton("Change Functions")
        self.change_functions_button.clicked.connect(self._on_change_functions_clicked)
        self.run_functions_button = QPushButton("Run Functions")
        self.run_functions_button.clicked.connect(self._on_run_functions_clicked)
        
        button_layout.addWidget(self.change_functions_button)
        button_layout.addWidget(self.run_functions_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.tab_widget.addTab(functions_tab, "Functions")
        
    def _create_control_tab(self):
        """Create the control parameters tab."""
        control_tab = QWidget()
        layout = QVBoxLayout(control_tab)
        
        # Title
        title_label = QLabel("Control Parameters")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Control parameters
        control_group = QGroupBox("Simulation Control")
        control_layout = QVBoxLayout()
        
        # Time parameters
        time_layout = QHBoxLayout()
        self.end_time_edit = QDoubleSpinBox()
        self.end_time_edit.setValue(DEFAULT_PARAMETERS["endTime"])
        self.end_time_edit.setRange(0, 1e6)
        self.delta_t_edit = QDoubleSpinBox()
        self.delta_t_edit.setValue(DEFAULT_PARAMETERS["deltaT"])
        self.delta_t_edit.setRange(1e-6, 1e3)
        self.write_interval_edit = QDoubleSpinBox()
        self.write_interval_edit.setValue(DEFAULT_PARAMETERS["writeInterval"])
        self.write_interval_edit.setRange(1e-3, 1e6)
        
        time_layout.addWidget(QLabel("End time:"))
        time_layout.addWidget(self.end_time_edit)
        time_layout.addWidget(QLabel("Delta T:"))
        time_layout.addWidget(self.delta_t_edit)
        time_layout.addWidget(QLabel("Write interval:"))
        time_layout.addWidget(self.write_interval_edit)
        control_layout.addLayout(time_layout)
        
        # Tolerance
        tol_layout = QHBoxLayout()
        self.tolerance_edit = QLineEdit(str(DEFAULT_PARAMETERS["tolerance"]))
        tol_layout.addWidget(QLabel("Tolerance:"))
        tol_layout.addWidget(self.tolerance_edit)
        control_layout.addLayout(tol_layout)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.change_control_button = QPushButton("Change Control")
        self.change_control_button.clicked.connect(self._on_change_control_clicked)
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self._on_run_clicked)
        self.pause_button = QPushButton("Pause/Resume")
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self._on_stop_clicked)
        
        button_layout.addWidget(self.change_control_button)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.tab_widget.addTab(control_tab, "Control")
        
    def _create_terminal_tab(self):
        """Create the terminal output tab."""
        terminal_tab = QWidget()
        layout = QVBoxLayout(terminal_tab)
        
        # Title
        title_label = QLabel("Terminal Output")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Terminal output
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        # QTextEdit doesn't have setMaximumBlockCount, so we'll limit output manually
        layout.addWidget(self.terminal_output)
        
        # Command input
        command_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command (e.g., 'cd /path && command')")
        self.command_input.returnPressed.connect(self._on_command_entered)
        self.command_button = QPushButton("Execute")
        self.command_button.clicked.connect(self._on_command_entered)
        
        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.command_button)
        layout.addLayout(command_layout)
        
        self.tab_widget.addTab(terminal_tab, "Terminal")
        
    def _add_boundary_configuration(self, layout: QVBoxLayout):
        """Add boundary-specific configuration (to be overridden by subclasses)."""
        # Default implementation - can be overridden by specific interfaces
        info_label = QLabel("Boundary configuration specific to this interface will be added here.")
        layout.addWidget(info_label)
        
    def _connect_signals(self):
        """Connect interface-specific signals."""
        pass
        
    def _get_templates_path(self) -> str:
        """Get the path to OpenFOAM templates."""
        from ...core.constants import TEMPLATES_PATH
        return str(TEMPLATES_PATH)
        
    def _on_process_output(self, output: str):
        """Handle process output."""
        self.terminal_output.append(output)
        self.output_received.emit(output)
        
        # Limit output to prevent memory issues (manual limit for QTextEdit)
        cursor = self.terminal_output.textCursor()
        block_count = cursor.blockNumber() + 1
        if block_count > 1000:
            # Remove old content to keep memory usage reasonable
            self.terminal_output.clear()
            self.terminal_output.append("... Output truncated to prevent memory issues ...")
            self.terminal_output.append(output)
        
    def _on_process_error(self, error: str):
        """Handle process errors."""
        self.terminal_output.append(f"ERROR: {error}")
        self.error_received.emit(error)
        
    def _on_process_started(self):
        """Handle process start."""
        self.simulation_running = True
        self.simulation_paused = False
        self.simulation_started.emit()
        self._update_control_buttons()
        
    def _on_process_finished(self, exit_code: int):
        """Handle process completion."""
        self.simulation_running = False
        self.simulation_stopped.emit()
        self._update_control_buttons()
        if exit_code == 0:
            self.terminal_output.append("Simulation completed successfully.")
        else:
            self.terminal_output.append(f"Simulation failed with exit code: {exit_code}")
            
    def _update_control_buttons(self):
        """Update control button states based on simulation status."""
        if self.simulation_running:
            self.run_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.pause_button.setText("Pause" if not self.simulation_paused else "Resume")
        else:
            self.run_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.pause_button.setText("Pause/Resume")
            
    def _on_change_geometry_clicked(self):
        """Handle geometry parameter changes."""
        try:
            # Update blockMeshDict and topoSetDict
            self._update_geometry_parameters()
            self.terminal_output.append("Geometry parameters updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update geometry: {str(e)}")
            
    def _on_run_geometry_clicked(self):
        """Handle geometry generation."""
        try:
            # Run mesh generation commands
            self._run_geometry_commands()
            self.terminal_output.append("Geometry generation completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run geometry: {str(e)}")
            
    def _on_view_geometry_clicked(self):
        """Handle geometry visualization."""
        try:
            # Launch ParaView for geometry viewing
            self._launch_paraview()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch ParaView: {str(e)}")
            
    def _on_change_constants_clicked(self):
        """Handle constants parameter changes."""
        try:
            self._update_constants_parameters()
            self.terminal_output.append("Constants parameters updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update constants: {str(e)}")
            
    def _on_run_constants_clicked(self):
        """Handle constants setup."""
        try:
            self._run_constants_commands()
            self.terminal_output.append("Constants setup completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run constants: {str(e)}")
            
    def _on_help_constants_clicked(self):
        """Show constants help."""
        help_text = """
        DS value: Li Intrinsic diffusivity in material
        CS max: Maximum Li concentration in material
        kreact: Reaction rate constant
        R: Universal gas constant
        F: Faraday's constant
        Ce: Transfer coefficient
        alphaA: Anodic
        alphaC: Cathodic
        T: Temperature
        Iapp: Applied current density
        """
        QMessageBox.information(self, "Constants Help", help_text)
        
    def _on_change_boundary_clicked(self):
        """Handle boundary parameter changes."""
        try:
            self._update_boundary_parameters()
            self.terminal_output.append("Boundary parameters updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update boundary: {str(e)}")
            
    def _on_run_boundary_clicked(self):
        """Handle boundary setup."""
        try:
            self._run_boundary_commands()
            self.terminal_output.append("Boundary setup completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run boundary: {str(e)}")
            
    def _on_change_functions_clicked(self):
        """Handle function parameter changes."""
        try:
            self._update_functions_parameters()
            self.terminal_output.append("Function parameters updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update functions: {str(e)}")
            
    def _on_run_functions_clicked(self):
        """Handle function setup."""
        try:
            self._run_functions_commands()
            self.terminal_output.append("Function setup completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run functions: {str(e)}")
            
    def _on_change_control_clicked(self):
        """Handle control parameter changes."""
        try:
            self._update_control_parameters()
            self.terminal_output.append("Control parameters updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update control: {str(e)}")
            
    def _on_run_clicked(self):
        """Handle simulation start."""
        try:
            self._start_simulation()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start simulation: {str(e)}")
            
    def _on_pause_clicked(self):
        """Handle simulation pause/resume."""
        if self.simulation_running:
            if self.simulation_paused:
                self._resume_simulation()
            else:
                self._pause_simulation()
                
    def _on_stop_clicked(self):
        """Handle simulation stop."""
        try:
            self._stop_simulation()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop simulation: {str(e)}")
            
    def _on_command_entered(self):
        """Handle manual command execution."""
        command = self.command_input.text().strip()
        if command:
            self.terminal_output.append(f"$ {command}")
            self._execute_command(command)
            self.command_input.clear()
            
    def _update_geometry_parameters(self):
        """Update geometry parameters in OpenFOAM files."""
        # Implementation to update blockMeshDict and topoSetDict
        pass
        
    def _run_geometry_commands(self):
        """Run geometry generation commands."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        commands = [
            f"cd {self.case_path} && blockMesh",
            "topoSet",
            "splitMeshRegions -cellZones -overwrite",
            "paraFoam -touchAll"
        ]
        
        for command in commands:
            self._execute_command(command)
            # Wait for completion before next command
            while self.process_controller.is_running():
                import time
                time.sleep(0.1)
                
    def _launch_paraview(self):
        """Launch ParaView for visualization."""
        if not self.case_path:
            raise ValueError("Case path not set")
            
        command = f"cd {self.case_path} && paraFoam &"
        self._execute_command(command)
        
    def _update_constants_parameters(self):
        """Update constants parameters in OpenFOAM files."""
        # Implementation to update LiProperties files
        pass
        
    def _run_constants_commands(self):
        """Run constants setup commands."""
        if not self.solver_path:
            raise ValueError("Solver path not set")
            
        commands = [
            f"cd {self.solver_path} && wclean",
            "wmake"
        ]
        
        for command in commands:
            self._execute_command(command)
            while self.process_controller.is_running():
                import time
                time.sleep(0.1)
                
    def _update_boundary_parameters(self):
        """Update boundary parameters in OpenFOAM files."""
        # Implementation specific to each interface
        pass
        
    def _run_boundary_commands(self):
        """Run boundary setup commands."""
        # Implementation specific to each interface
        pass
        
    def _update_functions_parameters(self):
        """Update function parameters in OpenFOAM files."""
        # Implementation to update fvSchemes and fvSolution
        pass
        
    def _run_functions_commands(self):
        """Run function setup commands."""
        # Implementation specific to each interface
        pass
        
    def _update_control_parameters(self):
        """Update control parameters in OpenFOAM files."""
        # Implementation to update controlDict
        pass
        
    def _start_simulation(self):
        """Start the OpenFOAM simulation."""
        if not self.solver_manager:
            raise ValueError("Solver manager not initialized")
            
        if not self.case_path:
            raise ValueError("Case path not set")
            
        self.solver_manager.run_simulation(self.case_path)
        self.simulation_started.emit()
        
    def _pause_simulation(self):
        """Pause the simulation."""
        if self.process_controller.is_running():
            self.process_controller.send_signal(19)  # SIGSTOP
            self.simulation_paused = True
            self.simulation_paused.emit()
            self._update_control_buttons()
            
    def _resume_simulation(self):
        """Resume the simulation."""
        if self.process_controller.is_running():
            self.process_controller.send_signal(18)  # SIGCONT
            self.simulation_paused = False
            self._update_control_buttons()
            
    def _stop_simulation(self):
        """Stop the simulation."""
        self.process_controller.terminate_process()
        self.simulation_stopped.emit()
        self._update_control_buttons()
        
    def _execute_command(self, command: str):
        """Execute a command using the process controller."""
        self.process_controller.start_process(command)
        
    def set_project_paths(self, project_path: str, project_name: str):
        """Set the project paths for this interface."""
        self.project_path = project_path
        self.project_name = project_name
        self.case_path = os.path.join(project_path, project_name, "Case")
        self.solver_path = os.path.join(project_path, project_name)
        
        # Initialize solver manager
        solver_name = self._get_solver_name()
        self.solver_manager = OpenFOAMSolverManager(self.solver_path, solver_name)
        
        # Initialize parameter manager with project path
        self.parameter_manager = ParameterManager(self.project_path)
        
    def _get_solver_name(self) -> str:
        """Get the solver name for this interface."""
        from ...core.constants import SOLVER_NAMES
        return SOLVER_NAMES.get(self.interface_type, self.interface_type)
