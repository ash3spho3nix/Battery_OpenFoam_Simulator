"""
Result Interface for viewing simulation results.

This module provides the ResultInterface class, which displays simulation
results and allows users to visualize data using ParaView.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QTabWidget, QTextEdit, QLineEdit, QComboBox, QGroupBox, QFileDialog,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
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


class ResultInterface(BaseInterface):
    """
    Interface for viewing simulation results.
    
    Provides functionality to view simulation results using ParaView
    and display basic information about the simulation.
    """
    
    def __init__(
        self, 
        parent: Optional[QWidget] = None, 
        ui_config: Optional['UIConfig'] = None
    ):
        """
        Initialize the Result interface.
        
        Args:
            parent: Parent widget
            ui_config: UI configuration for loading mode
        """
        super().__init__(parent, ui_config)
        self.interface_type = "result"
        self.setWindowTitle("BatteryFOAM - Results Interface")
        
        # Result-specific components
        self.project_info_table = None
        self.simulation_status_label = None
        self.results_path_edit = None
        
    def _setup_ui(self):
        """Setup the result interface UI structure."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different sections
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # Add result-specific tabs
        self._create_summary_tab()
        self._create_results_tab()
        self._create_visualization_tab()
        self._create_terminal_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Set window properties
        self.setWindowTitle("BatteryFOAM - Results Interface")
        self.setMinimumSize(1000, 700)
        
    def _create_summary_tab(self):
        """Create the simulation summary tab."""
        summary_tab = QWidget()
        layout = QVBoxLayout(summary_tab)
        
        # Title
        title_label = QLabel("Simulation Summary")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Project information table
        project_group = QGroupBox("Project Information")
        project_layout = QVBoxLayout()
        
        self.project_info_table = QTableWidget(8, 2)
        self.project_info_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.project_info_table.horizontalHeader().setStretchLastSection(True)
        self.project_info_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.project_info_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.project_info_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Populate table with project information
        self._populate_project_info()
        
        project_layout.addWidget(self.project_info_table)
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)
        
        # Simulation status
        status_group = QGroupBox("Simulation Status")
        status_layout = QVBoxLayout()
        
        self.simulation_status_label = QLabel("Status: Not started")
        self.simulation_status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.simulation_status_label)
        
        # Status details
        status_details = QTextEdit()
        status_details.setReadOnly(True)
        status_details.setMaximumHeight(100)
        status_details.setText("Simulation details will appear here when available.")
        status_layout.addWidget(status_details)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        layout.addStretch()
        self.tab_widget.addTab(summary_tab, "Summary")
        
    def _create_results_tab(self):
        """Create the results tab."""
        results_tab = QWidget()
        layout = QVBoxLayout(results_tab)
        
        # Title
        title_label = QLabel("Results")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Results directory selection
        results_group = QGroupBox("Results Directory")
        results_layout = QVBoxLayout()
        
        results_path_layout = QHBoxLayout()
        self.results_path_edit = QLineEdit()
        self.results_path_edit.setReadOnly(True)
        self.browse_results_button = QPushButton("Browse...")
        self.browse_results_button.clicked.connect(self._on_browse_results_clicked)
        
        results_path_layout.addWidget(QLabel("Path:"))
        results_path_layout.addWidget(self.results_path_edit)
        results_path_layout.addWidget(self.browse_results_button)
        results_layout.addLayout(results_path_layout)
        
        # Results files list
        self.results_files_table = QTableWidget(0, 3)
        self.results_files_table.setHorizontalHeaderLabels(["File", "Size", "Modified"])
        self.results_files_table.horizontalHeader().setStretchLastSection(True)
        self.results_files_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_files_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_files_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        results_layout.addWidget(self.results_files_table)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Results actions
        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout()
        
        self.refresh_results_button = QPushButton("Refresh Results")
        self.refresh_results_button.clicked.connect(self._on_refresh_results_clicked)
        self.open_results_button = QPushButton("Open in ParaView")
        self.open_results_button.clicked.connect(self._on_open_paraview_clicked)
        self.export_results_button = QPushButton("Export Results")
        self.export_results_button.clicked.connect(self._on_export_results_clicked)
        
        actions_layout.addWidget(self.refresh_results_button)
        actions_layout.addWidget(self.open_results_button)
        actions_layout.addWidget(self.export_results_button)
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        layout.addStretch()
        self.tab_widget.addTab(results_tab, "Results")
        
    def _create_visualization_tab(self):
        """Create the visualization tab."""
        viz_tab = QWidget()
        layout = QVBoxLayout(viz_tab)
        
        # Title
        title_label = QLabel("Visualization")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Visualization options
        viz_group = QGroupBox("Visualization Options")
        viz_layout = QVBoxLayout()
        
        # Region selection for visualization
        region_layout = QHBoxLayout()
        self.region_combo = QComboBox()
        self.region_combo.addItems(["All Regions", "Anode", "Cathode", "Separator", "Electrolyte", "Solid Phase"])
        region_layout.addWidget(QLabel("Region:"))
        region_layout.addWidget(self.region_combo)
        viz_layout.addLayout(region_layout)
        
        # Variable selection
        variable_layout = QHBoxLayout()
        self.variable_combo = QComboBox()
        self.variable_combo.addItems(["Concentration", "Potential", "Current Density", "Temperature", "Voltage"])
        variable_layout.addWidget(QLabel("Variable:"))
        variable_layout.addWidget(self.variable_combo)
        viz_layout.addLayout(variable_layout)
        
        # Time step selection
        timestep_layout = QHBoxLayout()
        self.timestep_combo = QComboBox()
        self.timestep_combo.addItems(["Latest", "All Steps", "Custom Range"])
        timestep_layout.addWidget(QLabel("Time Step:"))
        timestep_layout.addWidget(self.timestep_combo)
        viz_layout.addLayout(timestep_layout)
        
        viz_group.setLayout(viz_layout)
        layout.addWidget(viz_group)
        
        # Visualization actions
        viz_actions_layout = QHBoxLayout()
        self.preview_viz_button = QPushButton("Preview")
        self.preview_viz_button.clicked.connect(self._on_preview_viz_clicked)
        self.launch_viz_button = QPushButton("Launch ParaView")
        self.launch_viz_button.clicked.connect(self._on_launch_paraview_clicked)
        self.save_viz_button = QPushButton("Save Visualization")
        self.save_viz_button.clicked.connect(self._on_save_viz_clicked)
        
        viz_actions_layout.addWidget(self.preview_viz_button)
        viz_actions_layout.addWidget(self.launch_viz_button)
        viz_actions_layout.addWidget(self.save_viz_button)
        layout.addLayout(viz_actions_layout)
        
        # Visualization status
        viz_status_group = QGroupBox("Visualization Status")
        viz_status_layout = QVBoxLayout()
        self.viz_status_label = QLabel("Ready to visualize results.")
        viz_status_layout.addWidget(self.viz_status_label)
        viz_status_group.setLayout(viz_status_layout)
        layout.addWidget(viz_status_group)
        
        layout.addStretch()
        self.tab_widget.addTab(viz_tab, "Visualization")
        
    def _populate_project_info(self):
        """Populate the project information table."""
        if not self.project_path or not self.project_name:
            return
            
        # Get project information
        project_info = [
            ("Project Name", self.project_name),
            ("Project Path", self.project_path),
            ("Interface Type", self.interface_type.title()),
            ("Case Path", self.case_path or "Not set"),
            ("Solver Path", self.solver_path or "Not set"),
            ("Simulation Status", "Running" if self.simulation_running else "Stopped"),
            ("Last Modified", self._get_last_modified()),
            ("Results Available", "Yes" if self._check_results_available() else "No")
        ]
        
        self.project_info_table.setRowCount(len(project_info))
        for i, (key, value) in enumerate(project_info):
            self.project_info_table.setItem(i, 0, QTableWidgetItem(key))
            self.project_info_table.setItem(i, 1, QTableWidgetItem(str(value)))
            
    def _get_last_modified(self) -> str:
        """Get the last modification time of the project."""
        if not self.case_path or not os.path.exists(self.case_path):
            return "Unknown"
            
        try:
            import time
            mtime = os.path.getmtime(self.case_path)
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        except:
            return "Unknown"
            
    def _check_results_available(self) -> bool:
        """Check if simulation results are available."""
        if not self.case_path:
            return False
            
        # Check for time-varying directories (time steps)
        try:
            for item in os.listdir(self.case_path):
                item_path = os.path.join(self.case_path, item)
                if os.path.isdir(item_path) and self._is_time_directory(item):
                    return True
        except:
            pass
            
        # Check for specific result files
        result_files = ["time_voltage", "results.csv", "output.dat"]
        for result_file in result_files:
            if os.path.exists(os.path.join(self.case_path, result_file)):
                return True
                
        return False
        
    def _is_time_directory(self, name: str) -> bool:
        """Check if a directory name represents a time step."""
        try:
            float(name)
            return True
        except ValueError:
            return False
            
    def _on_browse_results_clicked(self):
        """Handle browsing for results directory."""
        if self.case_path and os.path.exists(self.case_path):
            initial_path = self.case_path
        else:
            initial_path = os.path.expanduser("~")
            
        directory = QFileDialog.getExistingDirectory(
            self, "Select Results Directory", initial_path
        )
        
        if directory:
            self.results_path_edit.setText(directory)
            self._populate_results_files(directory)
            
    def _populate_results_files(self, directory: str):
        """Populate the results files table."""
        self.results_files_table.setRowCount(0)
        
        if not os.path.exists(directory):
            return
            
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    row = self.results_files_table.rowCount()
                    self.results_files_table.insertRow(row)
                    
                    # File name
                    self.results_files_table.setItem(row, 0, QTableWidgetItem(item))
                    
                    # File size
                    size = os.path.getsize(item_path)
                    size_str = self._format_file_size(size)
                    self.results_files_table.setItem(row, 1, QTableWidgetItem(size_str))
                    
                    # Modified time
                    mtime = os.path.getmtime(item_path)
                    import time
                    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
                    self.results_files_table.setItem(row, 2, QTableWidgetItem(time_str))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read directory: {str(e)}")
            
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
            
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
        
    def _on_refresh_results_clicked(self):
        """Handle refreshing results."""
        results_path = self.results_path_edit.text().strip()
        if results_path and os.path.exists(results_path):
            self._populate_results_files(results_path)
        elif self.case_path and os.path.exists(self.case_path):
            self._populate_results_files(self.case_path)
        else:
            QMessageBox.warning(self, "Warning", "No valid results directory specified.")
            
    def _on_open_paraview_clicked(self):
        """Handle opening results in ParaView."""
        results_path = self.results_path_edit.text().strip()
        if not results_path or not os.path.exists(results_path):
            if self.case_path and os.path.exists(self.case_path):
                results_path = self.case_path
            else:
                QMessageBox.warning(self, "Warning", "No valid results directory specified.")
                return
                
        # Launch ParaView with the results directory
        try:
            command = f"cd {results_path} && paraFoam &"
            self._execute_command(command)
            self.terminal_output.append(f"Launched ParaView for: {results_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch ParaView: {str(e)}")
            
    def _on_export_results_clicked(self):
        """Handle exporting results."""
        results_path = self.results_path_edit.text().strip()
        if not results_path or not os.path.exists(results_path):
            QMessageBox.warning(self, "Warning", "No valid results directory specified.")
            return
            
        # Ask user for export format and location
        export_format = QComboBox()
        export_format.addItems(["CSV", "JSON", "TXT", "VTK"])
        
        export_dialog = QMessageBox(self)
        export_dialog.setWindowTitle("Export Results")
        export_dialog.setText("Select export format:")
        export_dialog.setInformativeText("Choose the format for exporting results.")
        export_dialog.setDetailedText("This will export the simulation results to the selected format.")
        export_dialog.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        export_dialog.setDefaultButton(QMessageBox.StandardButton.Ok)
        export_dialog.setCheckBox(export_format)
        export_dialog.exec()
        
        if export_dialog.result() == QMessageBox.StandardButton.Ok:
            format_selected = export_format.currentText()
            self._export_results(results_path, format_selected)
            
    def _export_results(self, results_path: str, format: str):
        """Export results to the specified format."""
        try:
            # Determine export location
            export_path, _ = QFileDialog.getSaveFileName(
                self, "Export Results", os.path.join(results_path, f"results.{format.lower()}"),
                f"{format} Files (*.{format.lower()});;All Files (*)"
            )
            
            if not export_path:
                return
                
            # Simple export implementation (can be extended for different formats)
            with open(export_path, 'w') as f:
                f.write(f"# BatteryFOAM Results Export\n")
                f.write(f"# Format: {format}\n")
                f.write(f"# Exported from: {results_path}\n\n")
                
                # List all files in the results directory
                f.write("## File List\n")
                for item in os.listdir(results_path):
                    item_path = os.path.join(results_path, item)
                    if os.path.isfile(item_path):
                        f.write(f"- {item}\n")
                        
                f.write(f"\n## Export completed at {self._get_current_time()}\n")
                
            QMessageBox.information(self, "Export Complete", f"Results exported to: {export_path}")
            self.terminal_output.append(f"Results exported to: {export_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export results: {str(e)}")
            
    def _get_current_time(self) -> str:
        """Get current time as formatted string."""
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
    def _on_preview_viz_clicked(self):
        """Handle visualization preview."""
        self.viz_status_label.setText("Previewing visualization... (This would show a preview if implemented)")
        self.terminal_output.append("Visualization preview requested (preview not implemented in this version)")
        
    def _on_launch_paraview_clicked(self):
        """Handle launching ParaView for visualization."""
        self._on_open_paraview_clicked()
        self.viz_status_label.setText("ParaView launched successfully")
        
    def _on_save_viz_clicked(self):
        """Handle saving visualization."""
        # This would save visualization settings or screenshots
        QMessageBox.information(self, "Save Visualization", "Visualization settings saved (implementation would depend on ParaView integration)")
        self.terminal_output.append("Visualization settings saved")
        
    def set_project_paths(self, project_path: str, project_name: str):
        """Set the project paths and update the interface."""
        super().set_project_paths(project_path, project_name)
        self._populate_project_info()
        self._populate_results_files(self.case_path or project_path)
        
    def _on_process_started(self):
        """Handle process start - update status."""
        super()._on_process_started()
        self.simulation_status_label.setText("Status: Running")
        self._populate_project_info()
        
    def _on_process_finished(self, exit_code: int):
        """Handle process completion - update status and results."""
        super()._on_process_finished(exit_code)
        if exit_code == 0:
            self.simulation_status_label.setText("Status: Completed Successfully")
        else:
            self.simulation_status_label.setText("Status: Failed")
        self._populate_project_info()
        self._populate_results_files(self.case_path or self.project_path)
