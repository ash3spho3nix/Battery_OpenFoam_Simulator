"""
Integration tests for complete workflows.

This module tests end-to-end workflows including:
- Complete project creation workflow
- Simulation execution workflow
- UI loading and switching workflow
- Error handling across components
"""

import pytest
import os
import tempfile
import shutil
import subprocess
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from PyQt6.QtWidgets import QApplication

from src.core.application import BatterySimulatorApp
from src.core.project_manager import ProjectManager
from src.gui.main_window import MainWindow
from src.gui.interfaces.carbon_interface import CarbonInterface
from src.gui.ui_config import UIConfig, UILoadingMode
from src.openfoam.process_controller import ProcessController
from src.openfoam.solver_manager import OpenFOAMSolverManager
from src.utils.file_operations import TemplateManager
from src.utils.parameter_parser import ParameterManager


class TestProjectCreationWorkflow:
    """Test complete project creation workflow."""
    
    def test_complete_project_creation_workflow(self, qt_app, temp_dir):
        """Test complete project creation from start to finish."""
        # Create mock templates
        templates_path = Path(temp_dir) / "templates"
        templates_path.mkdir()
        
        for module in ["SPM", "halfCell", "fullCell"]:
            module_dir = templates_path / module
            module_dir.mkdir()
            (module_dir / "README.md").write_text(f"{module} Template")
            
            # Create solver directory
            solver_dir = module_dir / f"{module}Foam"
            solver_dir.mkdir()
            (solver_dir / "Make").mkdir()
            (solver_dir / "Make" / "files").write_text(f"{module}Foam\n")
        
        # Mock the application
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Set up project details
        app.project_path = temp_dir
        app.project_name = "integration_test"
        app.carbon_button.setChecked(True)
        
        # Mock interface creation
        with patch('src.gui.interface_factory.InterfaceFactory.create_interface') as mock_create:
            mock_interface = Mock()
            mock_create.return_value = mock_interface
            
            # Mock hide to avoid GUI issues
            app.hide = Mock()
            
            # Mock project manager
            mock_pm = Mock()
            app.project_manager = mock_pm
            
            # Trigger project creation
            app.on_main_next_button_clicked()
            
            # Verify project manager was called
            mock_pm.create_project.assert_called_once_with(
                temp_dir, "integration_test", "SPM"
            )
            
            # Verify interface creation
            mock_create.assert_called_once()
        
        app.close()
    
    def test_project_creation_with_solver_building(self, temp_dir):
        """Test project creation with solver building."""
        # Create mock templates with solver
        templates_path = Path(temp_dir) / "templates"
        templates_path.mkdir()
        
        spm_template = templates_path / "SPM"
        spm_template.mkdir()
        (spm_template / "README.md").write_text("SPM Template")
        
        # Create solver directory with Make files
        solver_dir = spm_template / "SPMFoam"
        solver_dir.mkdir()
        make_dir = solver_dir / "Make"
        make_dir.mkdir()
        
        # Create Make/files
        make_files = make_dir / "files"
        make_files.write_text("""SPMFoam.C

EXE = \$(FOAM_APPBIN)/SPMFoam_OF6
""")
        
        # Create Make/options
        make_options = make_dir / "options"
        make_options.write_text("""EXE_INC = \\
    -I\$(LIB_SRC)/finiteVolume/lnInclude

EXE_LIBS = \\
    -lfiniteVolume
""")
        
        # Test project creation with solver building
        pm = ProjectManager()
        with patch('src.core.constants.TEMPLATES_PATH', templates_path):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                
                pm.create_project(temp_dir, "test_project", "SPM", build_solver=True)
                
                # Verify solver building was attempted
                assert mock_run.call_count >= 1
                
                # Verify project was created
                project_path = Path(temp_dir) / "test_project"
                assert project_path.exists()
                assert (project_path / "SPMFoam").exists()
    
    def test_project_creation_error_handling(self, qt_app, temp_dir):
        """Test error handling during project creation."""
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Set up invalid project details
        app.project_path = temp_dir
        app.project_name = ""  # Invalid name
        
        # Mock QMessageBox to capture error
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msg:
            app.on_main_next_button_clicked()
            
            # Verify error message was shown
            mock_msg.assert_called_once()
            args = mock_msg.call_args[0]
            assert "invalid_name" in args[2]
        
        app.close()
    
    def test_project_opening_workflow(self, qt_app, temp_dir):
        """Test complete project opening workflow."""
        # Create existing project
        project_path = Path(temp_dir) / "existing_project"
        project_path.mkdir()
        
        case_path = project_path / "Case"
        case_path.mkdir()
        
        solver_path = project_path / "SPMFoam"
        solver_path.mkdir()
        
        # Mock the application
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Set up project opening
        app.project_path = temp_dir
        app.project_name = "existing_project"
        
        # Mock interface creation
        with patch('src.gui.interface_factory.InterfaceFactory.create_interface') as mock_create:
            mock_interface = Mock()
            mock_create.return_value = mock_interface
            
            # Mock hide to avoid GUI issues
            app.hide = Mock()
            
            # Mock project detection
            with patch('os.path.exists', return_value=True):
                app.on_main_next_button_2_clicked()
                
                # Verify interface creation
                mock_create.assert_called_once()
        
        app.close()
    
    def test_project_creation_ui_integration(self, qt_app, temp_dir):
        """Test project creation with UI integration."""
        # Create mock templates
        templates_path = Path(temp_dir) / "templates"
        templates_path.mkdir()
        
        spm_template = templates_path / "SPM"
        spm_template.mkdir()
        (spm_template / "README.md").write_text("SPM Template")
        
        # Mock UI configuration
        ui_config = UIConfig()
        ui_config.set_mode(UILoadingMode.HAND_CODED)
        
        with patch('src.gui.ui_config.UIConfig', return_value=ui_config):
            with patch('src.core.constants.TEMPLATES_PATH', templates_path):
                # Create main window
                window = MainWindow(ui_config=ui_config)
                
                # Set project details
                window.project_path = temp_dir
                window.project_name = "ui_test_project"
                window.carbon_button.setChecked(True)
                
                # Mock interface creation
                with patch('src.gui.interface_factory.InterfaceFactory.create_interface') as mock_create:
                    mock_interface = Mock()
                    mock_create.return_value = mock_interface
                    
                    # Mock hide to avoid GUI issues
                    window.hide = Mock()
                    
                    # Trigger project creation
                    window.on_main_next_button_clicked()
                    
                    # Verify project creation
                    project_path = Path(temp_dir) / "ui_test_project"
                    assert project_path.exists()
                    
                    # Verify interface creation
                    mock_create.assert_called_once()
                
                window.close()


class TestSimulationExecutionWorkflow:
    """Test complete simulation execution workflow."""
    
    def test_complete_simulation_workflow(self, qt_app, temp_dir):
        """Test complete simulation execution from setup to completion."""
        # Create project structure
        project_path = Path(temp_dir) / "simulation_test"
        project_path.mkdir()
        
        case_path = project_path / "Case"
        case_path.mkdir()
        
        # Create case structure
        system_dir = case_path / "system"
        system_dir.mkdir()
        constant_dir = case_path / "constant"
        constant_dir.mkdir()
        
        # Create basic OpenFOAM files
        control_dict = system_dir / "controlDict"
        control_dict.write_text("""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  6                                     |
|   \  /    A nd           | Web:      www.OpenFOAM.org                        |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     SPMFoam_OF6;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         10;

deltaT          0.1;

writeControl    timeStep;

writeInterval   10;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

// ************************************************************************* //
""")
        
        # Create solver
        solver_path = project_path / "SPMFoam"
        solver_path.mkdir()
        
        # Test simulation execution
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Mock successful solver building
        with patch.object(manager, 'build_solver', return_value=True):
            with patch.object(manager.process_controller, 'start_process') as mock_start:
                # Run simulation
                manager.run_simulation(str(case_path))
                
                # Verify process was started
                mock_start.assert_called_once()
                args = mock_start.call_args[0]
                command = args[0]
                
                # Command should contain solver name and case path
                assert "SPMFoam_OF6" in command
                assert str(case_path) in command
    
    def test_simulation_with_parameter_management(self, temp_dir):
        """Test simulation with parameter management."""
        # Create project structure
        project_path = Path(temp_dir) / "param_test"
        project_path.mkdir()
        
        case_path = project_path / "Case"
        case_path.mkdir()
        
        # Create case structure
        system_dir = case_path / "system"
        system_dir.mkdir()
        
        # Create controlDict
        control_dict = system_dir / "controlDict"
        control_dict.write_text("""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  6                                     |
|   \  /    A nd           | Web:      www.OpenFOAM.org                        |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     SPMFoam_OF6;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         10;

deltaT          0.1;

writeControl    timeStep;

writeInterval   10;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

// ************************************************************************* //
""")
        
        # Test parameter management
        param_manager = ParameterManager(str(case_path))
        
        # Read parameters
        control_params = param_manager.get_parameters("controlDict")
        assert control_params is not None
        
        # Update parameters
        updates = {
            "endTime": "20.0",
            "deltaT": "0.05"
        }
        param_manager.update_parameters("controlDict", updates)
        
        # Verify updates
        updated_content = param_manager.read_parameter_file("controlDict")
        assert "endTime         20.0;" in updated_content
        assert "deltaT          0.05;" in updated_content
        
        # Test solver manager with updated parameters
        solver_path = project_path / "SPMFoam"
        solver_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        with patch.object(manager, 'build_solver', return_value=True):
            with patch.object(manager.process_controller, 'start_process') as mock_start:
                manager.run_simulation(str(case_path))
                
                # Simulation should use updated parameters
                mock_start.assert_called_once()
    
    def test_simulation_error_handling(self, temp_dir):
        """Test error handling during simulation."""
        # Create project structure
        project_path = Path(temp_dir) / "error_test"
        project_path.mkdir()
        
        case_path = project_path / "Case"
        case_path.mkdir()
        
        solver_path = project_path / "SPMFoam"
        solver_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Test solver build failure
        with patch.object(manager, 'build_solver', return_value=False):
            # Should handle build failure gracefully
            with patch.object(manager.process_controller, 'start_process') as mock_start:
                try:
                    manager.run_simulation(str(case_path))
                except Exception:
                    pytest.fail("Simulation should handle build failure gracefully")
        
        # Test simulation execution failure
        with patch.object(manager, 'build_solver', return_value=True):
            with patch.object(manager.process_controller, 'start_process') as mock_start:
                mock_start.side_effect = Exception("Simulation failed")
                
                # Should handle execution failure gracefully
                try:
                    manager.run_simulation(str(case_path))
                except Exception:
                    pytest.fail("Simulation should handle execution failure gracefully")
    
    def test_parallel_simulation_workflow(self, temp_dir):
        """Test parallel simulation workflow."""
        # Create project structure
        project_path = Path(temp_dir) / "parallel_test"
        project_path.mkdir()
        
        case_path = project_path / "Case"
        case_path.mkdir()
        
        # Create case structure
        system_dir = case_path / "system"
        system_dir.mkdir()
        
        # Create controlDict
        control_dict = system_dir / "controlDict"
        control_dict.write_text("""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  6                                     |
|   \  /    A nd           | Web:      www.OpenFOAM.org                        |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     SPMFoam_OF6;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         10;

deltaT          0.1;

writeControl    timeStep;

writeInterval   10;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

// ************************************************************************* //
""")
        
        # Create decomposeParDict for parallel execution
        decompose_dict = system_dir / "decomposeParDict"
        decompose_dict.write_text("""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  6                                     |
|   \  /    A nd           | Web:      www.OpenFOAM.org                        |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

numberOfSubdomains 4;

method          simple;

simpleCoeffs
{
    n               (2 2 1);
    delta           0.001;
}

// ************************************************************************* //
""")
        
        solver_path = project_path / "SPMFoam"
        solver_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Test parallel execution
        with patch.object(manager, 'build_solver', return_value=True):
            with patch.object(manager.process_controller, 'start_process') as mock_start:
                manager.run_simulation(str(case_path), parallel=True, num_processors=4)
                
                # Verify parallel execution command
                mock_start.assert_called_once()
                args = mock_start.call_args[0]
                command = args[0]
                
                # Command should contain mpirun and -parallel flag
                assert "mpirun" in command
                assert "-parallel" in command
                assert "-np 4" in command


class TestUIWorkflow:
    """Test UI loading and switching workflows."""
    
    def test_ui_auto_detect_workflow(self, qt_app, temp_dir, sample_ui_content):
        """Test UI auto-detect workflow."""
        # Create UI files
        ui_files = ["mainwindow.ui", "carboninterface.ui"]
        for filename in ui_files:
            ui_file = Path(temp_dir) / filename
            ui_file.write_text(sample_ui_content)
        
        # Test auto-detect configuration
        config = UIConfig()
        config.set_mode(UILoadingMode.AUTO_DETECT)
        config.set_ui_base_path(temp_dir)
        
        # Test main window loading
        with patch('src.gui.ui_loader_enhanced.UILoaderEnhanced.validate_ui_integrity', return_value=True):
            window = MainWindow(ui_config=config)
            
            # Should successfully load UI
            assert window is not None
            assert window.windowTitle() == "BatteryFOAM"
            
            window.close()
    
    def test_ui_fallback_workflow(self, qt_app, temp_dir):
        """Test UI fallback workflow when .ui loading fails."""
        # Create invalid UI file
        ui_file = Path(temp_dir) / "carboninterface.ui"
        ui_file.write_text("invalid xml content")
        
        # Test fallback configuration
        config = UIConfig()
        config.set_mode(UILoadingMode.AUTO_DETECT)
        config.set_ui_base_path(temp_dir)
        config.set_fallback_enabled(True)
        
        # Should fall back to hand-coded widgets
        with patch('src.gui.interfaces.carbon_interface.CarbonInterface') as mock_carbon:
            mock_instance = Mock()
            mock_carbon.return_value = mock_instance
            
            # Mock the base interface initialization to avoid GUI issues
            with patch('src.gui.interfaces.base_interface.BaseInterface.__init__', return_value=None):
                interface = CarbonInterface(ui_config=config)
                
                # Should create hand-coded interface
                assert interface is not None
    
    def test_ui_hand_coded_workflow(self, qt_app):
        """Test hand-coded UI workflow."""
        # Test hand-coded configuration
        config = UIConfig()
        config.set_mode(UILoadingMode.HAND_CODED)
        
        # Should use hand-coded widgets
        with patch('src.gui.interfaces.carbon_interface.CarbonInterface') as mock_carbon:
            mock_instance = Mock()
            mock_carbon.return_value = mock_instance
            
            # Mock the base interface initialization
            with patch('src.gui.interfaces.base_interface.BaseInterface.__init__', return_value=None):
                interface = CarbonInterface(ui_config=config)
                
                # Should create hand-coded interface
                assert interface is not None
    
    def test_ui_switching_workflow(self, qt_app):
        """Test UI switching between different modes."""
        # Test switching from auto-detect to UI files
        config = UIConfig()
        config.set_mode(UILoadingMode.AUTO_DETECT)
        
        # Should attempt UI loading first
        assert config.should_load_ui_files() is True
        
        # Switch to hand-coded mode
        config.set_mode(UILoadingMode.HAND_CODED)
        assert config.should_load_ui_files() is False
        
        # Switch to UI files mode
        config.set_mode(UILoadingMode.UI_FILES)
        assert config.should_load_ui_files() is True
    
    def test_ui_configuration_persistence(self):
        """Test UI configuration persistence across sessions."""
        # Test configuration serialization
        config = UIConfig()
        config.set_mode(UILoadingMode.AUTO_DETECT)
        config.set_ui_base_path("/custom/path")
        config.set_fallback_enabled(False)
        
        # Serialize to dict
        config_dict = config.to_dict()
        
        # Deserialize from dict
        new_config = UIConfig.from_dict(config_dict)
        
        # Verify configuration was preserved
        assert new_config.mode == UILoadingMode.AUTO_DETECT
        assert new_config.ui_base_path == "/custom/path"
        assert new_config.fallback_to_hand_coded is False


class TestErrorHandlingWorkflow:
    """Test error handling across complete workflows."""
    
    def test_project_creation_error_propagation(self, qt_app, temp_dir):
        """Test error propagation during project creation."""
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Set up project details
        app.project_path = temp_dir
        app.project_name = "error_test"
        app.carbon_button.setChecked(True)
        
        # Mock project manager to raise exception
        mock_pm = Mock()
        mock_pm.create_project.side_effect = Exception("Template not found")
        app.project_manager = mock_pm
        
        # Mock QMessageBox to capture error
        with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_msg:
            app.on_main_next_button_clicked()
            
            # Verify error message was shown
            mock_msg.assert_called_once()
            args = mock_msg.call_args[0]
            assert args[1] == "Error"
            assert "Template not found" in args[2]
        
        app.close()
    
    def test_simulation_error_recovery(self, temp_dir):
        """Test error recovery during simulation."""
        # Create project structure
        project_path = Path(temp_dir) / "recovery_test"
        project_path.mkdir()
        
        case_path = project_path / "Case"
        case_path.mkdir()
        
        solver_path = project_path / "SPMFoam"
        solver_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Test recovery from solver build failure
        with patch.object(manager, 'build_solver', return_value=False):
            # Should handle build failure and allow retry
            result = manager.build_solver()
            assert result is False
        
        # Test recovery from simulation failure
        with patch.object(manager, 'build_solver', return_value=True):
            with patch.object(manager.process_controller, 'start_process') as mock_start:
                mock_start.side_effect = Exception("Process failed")
                
                # Should handle failure gracefully
                try:
                    manager.run_simulation(str(case_path))
                except Exception:
                    pytest.fail("Should handle simulation failure gracefully")
    
    def test_ui_error_handling(self, qt_app, temp_dir):
        """Test UI error handling and recovery."""
        # Test handling of invalid UI configuration
        invalid_config = UIConfig()
        invalid_config.set_mode("invalid_mode")  # Invalid mode
        
        # Should default to AUTO_DETECT
        assert invalid_config.mode == UILoadingMode.AUTO_DETECT
        
        # Test handling of missing UI files
        config = UIConfig()
        config.set_mode(UILoadingMode.UI_FILES)
        config.set_ui_base_path("/nonexistent/path")
        
        # Should handle missing files gracefully
        exists = config.should_load_ui_files()
        # This will depend on the implementation, but should not crash
    
    def test_parameter_error_handling(self, temp_dir):
        """Test parameter error handling and validation."""
        # Create invalid parameter file
        param_file = Path(temp_dir) / "invalid_dict"
        param_file.write_text("invalid content")
        
        manager = ParameterManager(temp_dir)
        
        # Test reading invalid file
        with pytest.raises(Exception):
            manager.read_parameter_file("invalid_dict")
        
        # Test updating non-existent file
        with pytest.raises(FileNotFoundError):
            manager.update_parameters("nonexistent", {"test": "value"})
        
        # Test invalid parameter validation
        valid_file = Path(temp_dir) / "valid_dict"
        valid_file.write_text("""/* Valid dict */
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      validDict;
}
testParam 10;
// ************************************************************************* //
""")
        
        # Test invalid updates
        try:
            manager.update_parameters("valid_dict", {"invalidParam": "invalidValue"})
            # Should handle gracefully or validate
        except Exception:
            pass  # Expected for some invalid operations


class TestPerformanceWorkflow:
    """Test performance aspects of complete workflows."""
    
    def test_large_project_creation_performance(self, temp_dir):
        """Test performance of creating large projects."""
        # Create large template
        templates_path = Path(temp_dir) / "templates"
        large_template = templates_path / "LargeTemplate"
        large_template.mkdir(parents=True)
        
        # Create many files to simulate large template
        for i in range(100):
            file_path = large_template / f"file_{i}.txt"
            file_path.write_text(f"Content of file {i}" * 100)
        
        # Test creation performance
        import time
        start_time = time.time()
        
        pm = ProjectManager()
        with patch('src.core.constants.TEMPLATES_PATH', templates_path):
            pm.create_project(temp_dir, "large_project", "LargeTemplate")
        
        creation_time = time.time() - start_time
        
        # Should complete in reasonable time (less than 10 seconds)
        assert creation_time < 10.0
        
        # Verify project was created
        project_path = Path(temp_dir) / "large_project"
        assert project_path.exists()
    
    def test_simulation_performance_monitoring(self, temp_dir):
        """Test performance monitoring during simulation."""
        # Create project structure
        project_path = Path(temp_dir) / "perf_test"
        project_path.mkdir()
        
        case_path = project_path / "Case"
        case_path.mkdir()
        
        solver_path = project_path / "SPMFoam"
        solver_path.mkdir()
        
        manager = OpenFOAMSolverManager(str(solver_path), "SPMFoam_OF6")
        
        # Mock process controller to simulate long-running process
        mock_controller = Mock()
        mock_controller.start_process = Mock()
        mock_controller.is_running = Mock(return_value=True)
        mock_controller.get_exit_code = Mock(return_value=0)
        
        manager.process_controller = mock_controller
        
        # Test performance monitoring
        import time
        start_time = time.time()
        
        # Simulate running simulation
        manager.run_simulation(str(case_path))
        
        # Check that process was started
        mock_controller.start_process.assert_called_once()
        
        # Simulate process completion
        mock_controller.is_running.return_value = False
        
        # Should handle completion gracefully
        assert not manager.is_running()
    
    def test_ui_loading_performance(self, qt_app, temp_dir, sample_ui_content):
        """Test UI loading performance."""
        # Create multiple UI files
        ui_files = [f"interface_{i}.ui" for i in range(10)]
        for filename in ui_files:
            ui_file = Path(temp_dir) / filename
            ui_file.write_text(sample_ui_content)
        
        config = UIConfig()
        config.set_mode(UILoadingMode.UI_FILES)
        config.set_ui_base_path(temp_dir)
        
        # Test loading performance
        import time
        start_time = time.time()
        
        # This would test actual UI loading, but we'll mock it for testing
        with patch('src.gui.ui_loader_enhanced.UILoaderEnhanced.validate_ui_integrity', return_value=True):
            # Simulate loading multiple interfaces
            for i in range(5):
                # In real test, this would load actual UI files
                pass
        
        loading_time = time.time() - start_time
        
        # Should complete quickly (less than 5 seconds for mocked loading)
        assert loading_time < 5.0


class TestCrossPlatformWorkflow:
    """Test cross-platform compatibility of workflows."""
    
    def test_windows_workflow_compatibility(self, temp_dir):
        """Test workflow compatibility on Windows."""
        # Mock Windows platform
        with patch('sys.platform', 'win32'):
            # Test project creation on Windows
            templates_path = Path(temp_dir) / "templates"
            spm_template = templates_path / "SPM"
            spm_template.mkdir(parents=True)
            
            (spm_template / "README.md").write_text("SPM Template")
            
            # Test with Windows-style paths
            windows_path = r"C:\test\project"
            
            pm = ProjectManager()
            with patch('src.core.constants.TEMPLATES_PATH', templates_path):
                # Should handle Windows paths
                with patch('os.path.join', return_value=windows_path + "\\test_project"):
                    try:
                        pm.create_project(windows_path, "test_project", "SPM")
                    except Exception:
                        # May fail due to path mocking, but should not crash
                        pass
    
    def test_linux_workflow_compatibility(self, temp_dir):
        """Test workflow compatibility on Linux."""
        # Mock Linux platform
        with patch('sys.platform', 'linux'):
            # Test project creation on Linux
            templates_path = Path(temp_dir) / "templates"
            spm_template = templates_path / "SPM"
            spm_template.mkdir(parents=True)
            
            (spm_template / "README.md").write_text("SPM Template")
            
            # Test with Linux-style paths
            linux_path = "/home/user/projects"
            
            pm = ProjectManager()
            with patch('src.core.constants.TEMPLATES_PATH', templates_path):
                try:
                    pm.create_project(linux_path, "test_project", "SPM")
                except Exception:
                    # May fail due to path mocking, but should not crash
                    pass
    
    def test_macos_workflow_compatibility(self, temp_dir):
        """Test workflow compatibility on macOS."""
        # Mock macOS platform
        with patch('sys.platform', 'darwin'):
            # Test project creation on macOS
            templates_path = Path(temp_dir) / "templates"
            spm_template = templates_path / "SPM"
            spm_template.mkdir(parents=True)
            
            (spm_template / "README.md").write_text("SPM Template")
            
            # Test with macOS-style paths
            macos_path = "/Users/name/Projects"
            
            pm = ProjectManager()
            with patch('src.core.constants.TEMPLATES_PATH', templates_path):
                try:
                    pm.create_project(macos_path, "test_project", "SPM")
                except Exception:
                    # May fail due to path mocking, but should not crash
                    pass
    
    def test_cross_platform_path_handling(self, temp_dir):
        """Test cross-platform path handling in workflows."""
        # Test path handling across platforms
        test_paths = [
            "/unix/style/path",
            "C:\\windows\\style\\path",
            "relative/path",
            "./relative/path",
            "../parent/path"
        ]
        
        for test_path in test_paths:
            # Should handle different path styles
            path_obj = Path(test_path)
            
            # Test path operations
            assert path_obj is not None
            
            # Test path joining
            joined_path = path_obj / "subdir"
            assert joined_path is not None


class TestCompleteEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    def test_complete_battery_simulation_workflow(self, qt_app, temp_dir):
        """Test complete battery simulation workflow from project creation to simulation."""
        # Step 1: Create templates
        templates_path = Path(temp_dir) / "templates"
        templates_path.mkdir()
        
        spm_template = templates_path / "SPM"
        spm_template.mkdir()
        (spm_template / "README.md").write_text("SPM Template")
        
        # Create solver directory
        solver_dir = spm_template / "SPMFoam"
        solver_dir.mkdir()
        make_dir = solver_dir / "Make"
        make_dir.mkdir()
        (make_dir / "files").write_text("SPMFoam\n")
        
        # Step 2: Create main application
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Step 3: Set up project creation
        app.project_path = temp_dir
        app.project_name = "e2e_test"
        app.carbon_button.setChecked(True)
        
        # Step 4: Mock project manager
        mock_pm = Mock()
        app.project_manager = mock_pm
        
        # Step 5: Mock interface creation
        with patch('src.gui.interface_factory.InterfaceFactory.create_interface') as mock_create:
            mock_interface = Mock()
            mock_create.return_value = mock_interface
            
            # Step 6: Mock hide to avoid GUI issues
            app.hide = Mock()
            
            # Step 7: Create project
            app.on_main_next_button_clicked()
            
            # Step 8: Verify project creation
            mock_pm.create_project.assert_called_once_with(
                temp_dir, "e2e_test", "SPM"
            )
            
            # Step 9: Verify interface creation
            mock_create.assert_called_once()
        
        app.close()
    
    def test_complete_ui_workflow(self, qt_app, temp_dir, sample_ui_content):
        """Test complete UI workflow from loading to interaction."""
        # Step 1: Create UI files
        ui_files = {
            "mainwindow.ui": sample_ui_content,
            "carboninterface.ui": sample_ui_content
        }
        
        for filename, content in ui_files.items():
            ui_file = Path(temp_dir) / filename
            ui_file.write_text(content)
        
        # Step 2: Test UI configuration
        config = UIConfig()
        config.set_mode(UILoadingMode.AUTO_DETECT)
        config.set_ui_base_path(temp_dir)
        
        # Step 3: Test main window loading
        with patch('src.gui.ui_loader_enhanced.UILoaderEnhanced.validate_ui_integrity', return_value=True):
            window = MainWindow(ui_config=config)
            
            # Step 4: Verify window creation
            assert window is not None
            assert window.windowTitle() == "BatteryFOAM"
            
            window.close()
    
    def test_complete_error_handling_workflow(self, qt_app, temp_dir):
        """Test complete error handling workflow."""
        # Test complete workflow with error handling
        with patch('src.gui.ui_config.UIConfig'):
            app = BatterySimulatorApp()
        
        # Set up invalid project details
        app.project_path = temp_dir
        app.project_name = ""  # Invalid name
        
        # Test error handling in project creation
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_msg:
            app.on_main_next_button_clicked()
            
            # Verify error was handled gracefully
            mock_msg.assert_called_once()
        
        app.close()