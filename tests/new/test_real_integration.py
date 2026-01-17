"""
Integration test for complete workflow: ProjectManager → Interface → MSYS2 → OpenFOAM
Tests the actual integration without mocking critical components.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from src.core.project_manager import ProjectManager
from src.gui.interfaces.carbon_interface import CarbonInterface
from src.gui.interfaces.halfcell_interface import HalfCellInterface
from src.gui.interfaces.fullcell_interface import FullCellInterface


@pytest.fixture(scope="session")
def qapp():
    """Qt application."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestRealIntegration:
    """Test real integration without heavy mocking."""
    
    def test_spm_template_path_correct(self):
        """Test SPM template copies to correct location."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectManager(temp_dir)
            success = pm.create_project('test_spm', 'SPM')
            
            assert success, "Project creation failed"
            
            project_path = Path(temp_dir) / 'test_spm'
            assert project_path.exists(), "Project dir doesn't exist"
            
            # Check OpenFOAM structure at root
            assert (project_path / 'system').exists(), "system/ missing"
            assert (project_path / 'constant').exists(), "constant/ missing"
            assert (project_path / '0').exists(), "0/ missing"
            
            # Check key files
            assert (project_path / 'system' / 'blockMeshDict').exists()
            assert (project_path / 'system' / 'controlDict').exists()
    
    def test_halfcell_template_path_correct(self):
        """Test HalfCell template copies correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectManager(temp_dir)
            success = pm.create_project('test_hc', 'halfCell')
            
            assert success
            project_path = Path(temp_dir) / 'test_hc'
            assert (project_path / 'system').exists()
    
    def test_fullcell_template_path_correct(self):
        """Test FullCell template copies correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectManager(temp_dir)
            success = pm.create_project('test_fc', 'fullCell')
            
            assert success
            project_path = Path(temp_dir) / 'test_fc'
            assert (project_path / 'system').exists()
    
    def test_carbon_interface_receives_correct_path(self, qapp):
        """Test CarbonInterface gets correct case_path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectManager(temp_dir)
            pm.create_project('test_spm', 'SPM')
            
            project_path = str(Path(temp_dir) / 'test_spm')
            
            interface = CarbonInterface()
            interface.set_project_paths(project_path, 'test_spm')
            
            # case_path should be project root (where OpenFOAM files are)
            assert interface.case_path == project_path
            assert Path(interface.case_path).exists()
            assert (Path(interface.case_path) / 'system').exists()
    
    def test_solver_manager_validates_case(self, qapp):
        """Test SolverManager can validate case structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectManager(temp_dir)
            pm.create_project('test_spm', 'SPM')
            
            project_path = str(Path(temp_dir) / 'test_spm')
            
            interface = CarbonInterface()
            interface.set_project_paths(project_path, 'test_spm')
            
            # Validate case structure
            is_valid = interface.solver_manager.validate_case()
            assert is_valid, "Case validation failed"
    
    def test_process_controller_has_msys2(self, qapp):
        """Test ProcessController has MSYS2Executor."""
        interface = CarbonInterface()
        
        assert hasattr(interface.process_controller, 'msys2_executor')
        assert interface.process_controller.msys2_executor is not None
    
    def test_commands_are_simple_strings(self, qapp):
        """Test commands are simple strings (no 'cd' prefix)."""
        interface = CarbonInterface()
        interface.set_project_paths('/tmp/test', 'test')
        
        # Commands should be simple
        cmd1 = interface.solver_manager.get_block_mesh_command()
        cmd2 = interface.solver_manager.get_topo_set_command()
        
        assert cmd1 == "blockMesh"
        assert cmd2 == "topoSet"
        assert not cmd1.startswith("cd")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
