"""
Carbon Interface OpenFOAM Execution Workflow.

This module extends the CarbonInterface with complete OpenFOAM execution
capabilities, including the full simulation workflow.
"""

import os
import sys
import logging
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import QWidget, QMessageBox, QProgressBar, QLabel, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt

# Import modules using absolute imports
from src.gui.interfaces.carbon_interface import CarbonInterface
from src.openfoam.process_controller import ProcessController
from src.openfoam.solver_manager import OpenFOAMSolverManager
from src.core.constants import ERROR_MESSAGES, SUCCESS_MESSAGES

class CarbonInterfaceExecution(CarbonInterface):
    """
    Extended Carbon Interface with complete OpenFOAM execution workflow.
    
    Provides full simulation execution capabilities including:
    - Complete workflow execution (blockMesh, topoSet, splitMeshRegions, SPMFoam)
    - Real-time process monitoring
    - Progress tracking and time estimation
    - Comprehensive error detection and reporting
    - Process control (start/stop/pause)
    """
    
    def __init__(
        self, 
        parent: Optional[QWidget] = None, 
        ui_config: Optional['UIConfig'] = None
    ):
        """
        Initialize the Carbon interface with execution capabilities.
        
        Args:
            parent: Parent widget
            ui_config: UI configuration for loading mode
        """
        logger = logging.getLogger(__name__)
        logger.debug("CarbonInterfaceExecution.__init__() called")
        
        super().__init__(parent, ui_config)
        
        # Execution state
        self.execution_state = {
            'current_step': 0,
            'total_steps': 5,  # blockMesh, topoSet, splitMeshRegions, SPMFoam, completion
            'step_names': ['blockMesh', 'topoSet', 'splitMeshRegions', 'SPMFoam', 'Complete'],
            'execution_start_time': None,
            'current_process': None,
            'execution_completed': False
        }
        
        # Progress tracking
        self.progress_bar = None
        self.progress_label = None
        self.time_estimate_label = None
        
        # Setup execution UI
        self._setup_execution_ui()
        
        # Connect execution signals
        self._connect_execution_signals()
        
        logger.debug("CarbonInterfaceExecution initialized successfully")
    
    def _setup_execution_ui(self):
        """Setup UI elements for execution monitoring."""
        logger = logging.getLogger(__name__)
        logger.debug("Setting up execution UI...")
        
        # Add progress bar to control tab
        if hasattr(self, 'change_control_button'):
            control_tab = self.tab_widget.widget(4)  # Control tab is index 4
            
            # Create progress layout
            progress_layout = QVBoxLayout()
            
            # Progress bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(0)
            self.progress_bar.setTextVisible(True)
            self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            progress_layout.addWidget(self.progress_bar)
            
            # Progress label
            self.progress_label = QLabel("Ready to run simulation")
            self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            progress_layout.addWidget(self.progress_label)
            
            # Time estimate label
            self.time_estimate_label = QLabel("Estimated time: Calculating...")
            self.time_estimate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            progress_layout.addWidget(self.time_estimate_label)
            
            # Add to control tab layout
            control_tab.layout().insertLayout(2, progress_layout)
            
            logger.debug("Execution UI setup completed")
    
    def _connect_execution_signals(self):
        """Connect execution-specific signals."""
        logger = logging.getLogger(__name__)
        logger.debug("Connecting execution signals...")
        
        # Connect process controller signals
        if self.process_controller:
            self.process_controller.output_received.connect(self._on_execution_output)
            self.process_controller.error_received.connect(self._on_execution_error)
            self.process_controller.process_started.connect(self._on_execution_started)
            self.process_controller.process_finished.connect(self._on_execution_finished)
        
        logger.debug("Execution signals connected")
    
    def _on_run_clicked(self):
        """Handle simulation start with complete workflow."""
        logger = logging.getLogger(__name__)
        logger.info("Starting complete SPM simulation workflow")
        
        try:
            # Validate all parameters before starting
            if not self._validate_all_parameters():
                logger.warning("Parameter validation failed")
                return
            
            # Confirm execution
            reply = QMessageBox.question(
                self, 
                "Start Simulation", 
                "This will execute the complete SPM simulation workflow:\n"
                "1. Generate geometry (blockMesh)\n"
                "2. Set up regions (topoSet)\n"
                "3. Split mesh regions (splitMeshRegions)\n"
                "4. Run SPM solver (SPMFoam)\n\n"
                "Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                logger.info("User cancelled simulation")
                return
            
            # Initialize execution state
            self._initialize_execution()
            
            # Start complete workflow
            self._start_complete_workflow()
            
        except Exception as e:
            logger.error(f"Failed to start simulation: {e}", exc_info=True)
            self._show_error_message(f"Failed to start simulation: {str(e)}")
    
    def _validate_all_parameters(self):
        """Validate all simulation parameters."""
        logger = logging.getLogger(__name__)
        logger.debug("Validating all parameters...")
        
        errors = []
        
        # Validate geometry parameters
        geometry_errors = self._validate_geometry_parameters()
        errors.extend(geometry_errors)
        
        # Validate material parameters
        material_errors = self._validate_material_parameters()
        errors.extend(material_errors)
        
        # Validate control parameters
        control_errors = self._validate_control_parameters()
        errors.extend(control_errors)
        
        if errors:
            error_msg = "Parameter validation failed:\n\n" + "\n".join(errors)
            self._show_validation_error("Parameter Validation Error", error_msg)
            return False
        
        logger.debug("All parameters validated successfully")
        return True
    
    def _initialize_execution(self):
        """Initialize execution state and UI."""
        logger = logging.getLogger(__name__)
        logger.info("Initializing execution state...")
        
        # Reset execution state
        self.execution_state.update({
            'current_step': 0,
            'execution_start_time': time.time(),
            'current_process': None,
            'execution_completed': False
        })
        
        # Update UI
        if self.progress_bar:
            self.progress_bar.setValue(0)
        
        if self.progress_label:
            self.progress_label.setText("Initializing simulation...")
        
        if self.time_estimate_label:
            self.time_estimate_label.setText("Estimated time: Calculating...")
        
        # Update button states
        self._update_execution_buttons(running=True)
        
        logger.info("Execution state initialized")
    
    def _start_complete_workflow(self):
        """Start the complete simulation workflow."""
        logger = logging.getLogger(__name__)
        logger.info("Starting complete workflow...")
        
        # Step 1: Generate geometry
        self._execute_block_mesh()
    
    def _execute_block_mesh(self):
        """Execute blockMesh command."""
        logger = logging.getLogger(__name__)
        logger.info("Executing blockMesh...")
        
        self._update_progress(0, "Generating geometry with blockMesh...")
        
        try:
            command = f"cd {self.case_path} && blockMesh"
            self._execute_command_with_callback(
                command,
                success_callback=self._on_block_mesh_complete,
                error_callback=self._on_block_mesh_failed
            )
            
        except Exception as e:
            logger.error(f"Failed to execute blockMesh: {e}")
            self._on_block_mesh_failed(str(e))
    
    def _on_block_mesh_complete(self):
        """Handle blockMesh completion."""
        logger = logging.getLogger(__name__)
        logger.info("blockMesh completed successfully")
        
        self._update_progress(1, "Geometry generation completed")
        
        # Step 2: Execute topoSet
        self._execute_topo_set()
    
    def _on_block_mesh_failed(self, error: str):
        """Handle blockMesh failure."""
        logger = logging.getLogger(__name__)
        logger.error(f"blockMesh failed: {error}")
        
        self._show_error_message(f"Geometry generation failed: {error}")
        self._update_execution_buttons(running=False)
    
    def _execute_topo_set(self):
        """Execute topoSet command."""
        logger = logging.getLogger(__name__)
        logger.info("Executing topoSet...")
        
        self._update_progress(1, "Setting up regions with topoSet...")
        
        try:
            command = f"cd {self.case_path} && topoSet"
            self._execute_command_with_callback(
                command,
                success_callback=self._on_topo_set_complete,
                error_callback=self._on_topo_set_failed
            )
            
        except Exception as e:
            logger.error(f"Failed to execute topoSet: {e}")
            self._on_topo_set_failed(str(e))
    
    def _on_topo_set_complete(self):
        """Handle topoSet completion."""
        logger = logging.getLogger(__name__)
        logger.info("topoSet completed successfully")
        
        self._update_progress(2, "Region setup completed")
        
        # Step 3: Execute splitMeshRegions
        self._execute_split_mesh_regions()
    
    def _on_topo_set_failed(self, error: str):
        """Handle topoSet failure."""
        logger = logging.getLogger(__name__)
        logger.error(f"topoSet failed: {error}")
        
        self._show_error_message(f"Region setup failed: {error}")
        self._update_execution_buttons(running=False)
    
    def _execute_split_mesh_regions(self):
        """Execute splitMeshRegions command."""
        logger = logging.getLogger(__name__)
        logger.info("Executing splitMeshRegions...")
        
        self._update_progress(2, "Splitting mesh regions...")
        
        try:
            command = f"cd {self.case_path} && splitMeshRegions -cellZones -overwrite"
            self._execute_command_with_callback(
                command,
                success_callback=self._on_split_mesh_regions_complete,
                error_callback=self._on_split_mesh_regions_failed
            )
            
        except Exception as e:
            logger.error(f"Failed to execute splitMeshRegions: {e}")
            self._on_split_mesh_regions_failed(str(e))
    
    def _on_split_mesh_regions_complete(self):
        """Handle splitMeshRegions completion."""
        logger = logging.getLogger(__name__)
        logger.info("splitMeshRegions completed successfully")
        
        self._update_progress(3, "Mesh region splitting completed")
        
        # Step 4: Execute SPMFoam
        self._execute_spm_solver()
    
    def _on_split_mesh_regions_failed(self, error: str):
        """Handle splitMeshRegions failure."""
        logger = logging.getLogger(__name__)
        logger.error(f"splitMeshRegions failed: {error}")
        
        self._show_error_message(f"Mesh region splitting failed: {error}")
        self._update_execution_buttons(running=False)
    
    def _execute_spm_solver(self):
        """Execute SPMFoam solver."""
        logger = logging.getLogger(__name__)
        logger.info("Executing SPMFoam solver...")
        
        self._update_progress(3, "Running SPM solver...")
        
        try:
            # First, compile the solver if needed
            self._compile_solver()
            
            # Then run the simulation
            command = f"cd {self.case_path} && {self._get_solver_name()}"
            self._execute_command_with_callback(
                command,
                success_callback=self._on_spm_solver_complete,
                error_callback=self._on_spm_solver_failed
            )
            
        except Exception as e:
            logger.error(f"Failed to execute SPMFoam: {e}")
            self._on_spm_solver_failed(str(e))
    
    def _compile_solver(self):
        """Compile the SPM solver."""
        logger = logging.getLogger(__name__)
        logger.info("Compiling SPM solver...")
        
        try:
            # Clean previous build
            clean_command = f"cd {self.solver_path} && wclean"
            self._execute_command_sync(clean_command)
            
            # Compile solver
            compile_command = f"cd {self.solver_path} && wmake"
            result = self._execute_command_sync(compile_command)
            
            if result.returncode != 0:
                raise Exception(f"Solver compilation failed with exit code: {result.returncode}")
            
            logger.info("Solver compilation completed successfully")
            
        except Exception as e:
            logger.error(f"Solver compilation failed: {e}")
            raise
    
    def _on_spm_solver_complete(self):
        """Handle SPMFoam completion."""
        logger = logging.getLogger(__name__)
        logger.info("SPMFoam completed successfully")
        
        self._update_progress(4, "Simulation completed successfully!")
        
        # Step 5: Complete execution
        self._complete_execution()
    
    def _on_spm_solver_failed(self, error: str):
        """Handle SPMFoam failure."""
        logger = logging.getLogger(__name__)
        logger.error(f"SPMFoam failed: {error}")
        
        self._show_error_message(f"Simulation failed: {error}")
        self._update_execution_buttons(running=False)
    
    def _complete_execution(self):
        """Complete the execution workflow."""
        logger = logging.getLogger(__name__)
        logger.info("Completing execution workflow...")
        
        self.execution_state['execution_completed'] = True
        execution_time = time.time() - self.execution_state['execution_start_time']
        
        # Update final progress
        self._update_progress(4, f"Execution completed in {execution_time:.1f} seconds")
        
        # Show success message
        QMessageBox.information(
            self,
            "Simulation Complete",
            f"SPM simulation completed successfully!\n"
            f"Total execution time: {execution_time:.1f} seconds\n\n"
            f"Results are available in: {self.case_path}"
        )
        
        # Update button states
        self._update_execution_buttons(running=False)
        
        logger.info("Execution workflow completed successfully")
    
    def _update_progress(self, step: int, message: str):
        """Update progress bar and labels."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Updating progress: step {step}/4 - {message}")
        
        self.execution_state['current_step'] = step
        
        # Update progress bar (0-100%)
        progress_percent = int((step / self.execution_state['total_steps']) * 100)
        
        if self.progress_bar:
            self.progress_bar.setValue(progress_percent)
        
        if self.progress_label:
            self.progress_label.setText(message)
        
        # Update time estimate
        if self.progress_bar:
            elapsed_time = time.time() - self.execution_state['execution_start_time']
            if step > 0:
                # Estimate remaining time based on progress
                estimated_total = elapsed_time / (step / self.execution_state['total_steps'])
                remaining_time = estimated_total - elapsed_time
                self.time_estimate_label.setText(
                    f"Elapsed time: {elapsed_time:.1f}s | "
                    f"Estimated remaining: {remaining_time:.1f}s"
                )
            else:
                self.time_estimate_label.setText(f"Elapsed time: {elapsed_time:.1f}s")
        
        # Update terminal output
        if self.terminal_output:
            self.terminal_output.append(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def _update_execution_buttons(self, running: bool):
        """Update button states based on execution status."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Updating execution buttons: running={running}")
        
        # Update control buttons
        if hasattr(self, 'run_button'):
            self.run_button.setEnabled(not running)
        
        if hasattr(self, 'pause_button'):
            self.pause_button.setEnabled(running)
        
        if hasattr(self, 'stop_button'):
            self.stop_button.setEnabled(running)
        
        # Update other buttons
        if hasattr(self, 'change_geometry_button'):
            self.change_geometry_button.setEnabled(not running)
        
        if hasattr(self, 'change_constants_button'):
            self.change_constants_button.setEnabled(not running)
        
        if hasattr(self, 'change_boundary_button'):
            self.change_boundary_button.setEnabled(not running)
        
        if hasattr(self, 'change_functions_button'):
            self.change_functions_button.setEnabled(not running)
        
        if hasattr(self, 'change_control_button'):
            self.change_control_button.setEnabled(not running)
    
    def _execute_command_with_callback(self, command: str, success_callback, error_callback):
        """Execute command with success and error callbacks."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Executing command with callbacks: {command}")
        
        # Store callback information
        self._current_success_callback = success_callback
        self._current_error_callback = error_callback
        
        # Start process
        self.process_controller.start_process(command)
        
        # Set current process
        self.execution_state['current_process'] = command
    
    def _execute_command_sync(self, command: str) -> subprocess.CompletedProcess:
        """Execute command synchronously and return result."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Executing command synchronously: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Log output
            if result.stdout:
                logger.debug(f"Command output: {result.stdout}")
            
            if result.stderr:
                logger.warning(f"Command stderr: {result.stderr}")
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            raise Exception(f"Command timed out after 300 seconds: {command}")
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise
    
    def _on_execution_output(self, output: str):
        """Handle execution output."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Execution output: {output[:100]}...")
        
        # Update terminal
        if self.terminal_output:
            self.terminal_output.append(output)
    
    def _on_execution_error(self, error: str):
        """Handle execution error."""
        logger = logging.getLogger(__name__)
        logger.error(f"Execution error: {error}")
        
        # Call error callback if available
        if hasattr(self, '_current_error_callback') and self._current_error_callback:
            self._current_error_callback(error)
            # Clear callback after calling
            self._current_error_callback = None
    
    def _on_execution_started(self):
        """Handle execution start."""
        logger = logging.getLogger(__name__)
        logger.info("Execution started")
        
        # Update button states
        self._update_execution_buttons(running=True)
    
    def _on_execution_finished(self, exit_code: int):
        """Handle execution completion."""
        logger = logging.getLogger(__name__)
        logger.info(f"Execution finished with exit code: {exit_code}")
        
        # Check if execution was successful
        if exit_code == 0:
            # Call success callback if available
            if hasattr(self, '_current_success_callback') and self._current_success_callback:
                self._current_success_callback()
                # Clear callback after calling
                self._current_success_callback = None
        else:
            # Handle failure
            error_msg = f"Process failed with exit code: {exit_code}"
            if hasattr(self, '_current_error_callback') and self._current_error_callback:
                self._current_error_callback(error_msg)
                # Clear callback after calling
                self._current_error_callback = None
    
    def _on_stop_clicked(self):
        """Handle simulation stop with workflow interruption."""
        logger = logging.getLogger(__name__)
        logger.info("Stopping simulation workflow")
        
        try:
            # Stop current process
            if self.process_controller:
                self.process_controller.terminate_process()
            
            # Update execution state
            self.execution_state['execution_completed'] = False
            
            # Update UI
            self._update_progress(
                self.execution_state['current_step'],
                "Simulation stopped by user"
            )
            
            # Update button states
            self._update_execution_buttons(running=False)
            
            # Show message
            QMessageBox.information(
                self,
                "Simulation Stopped",
                "Simulation workflow has been stopped by the user."
            )
            
            logger.info("Simulation workflow stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop simulation: {e}")
            self._show_error_message(f"Failed to stop simulation: {str(e)}")
    
    def _on_pause_clicked(self):
        """Handle simulation pause/resume."""
        logger = logging.getLogger(__name__)
        logger.info("Toggling simulation pause/resume")
        
        try:
            if self.process_controller and self.process_controller.is_running():
                if self.simulation_paused:
                    # Resume
                    self._resume_simulation()
                    self._update_progress(
                        self.execution_state['current_step'],
                        f"Resumed {self.execution_state['step_names'][self.execution_state['current_step']]}"
                    )
                else:
                    # Pause
                    self._pause_simulation()
                    self._update_progress(
                        self.execution_state['current_step'],
                        f"Paused {self.execution_state['step_names'][self.execution_state['current_step']]}"
                    )
        except Exception as e:
            logger.error(f"Failed to pause/resume simulation: {e}")
            self._show_error_message(f"Failed to pause/resume simulation: {str(e)}")
    
    def _get_solver_name(self) -> str:
        """Get the solver name for this interface."""
        from src.core.constants import SOLVER_NAMES
        return SOLVER_NAMES.get(self.interface_type, "SPMFoam_OF6")
    
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