"""
OpenFOAM Solver Manager.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class OpenFOAMSolverManager:
    """Manager for OpenFOAM solver operations."""
    
    def __init__(self, case_path: str = None):
        self.case_path = Path(case_path) if case_path else None
        self.solver_name = None
        logger.info(f"SolverManager initialized: {case_path}")
    
    def set_case_path(self, case_path: str):
        """Set case directory path."""
        self.case_path = Path(case_path)
        logger.info(f"Case path set: {case_path}")
    
    def set_solver(self, solver_name: str):
        """Set solver name."""
        self.solver_name = solver_name
        logger.info(f"Solver set: {solver_name}")
    
    def validate_case(self) -> bool:
        """Validate case has required structure."""
        if not self.case_path or not self.case_path.exists():
            return False
        
        required_dirs = ['system', 'constant', '0']
        for dir_name in required_dirs:
            if not (self.case_path / dir_name).exists():
                logger.warning(f"Missing directory: {dir_name}")
                return False
        
        return True
    
    def get_block_mesh_command(self) -> str:
        """Get blockMesh command."""
        return "blockMesh"
    
    def get_topo_set_command(self) -> str:
        """Get topoSet command."""
        return "topoSet"
    
    def get_split_mesh_command(self) -> str:
        """Get splitMeshRegions command."""
        return "splitMeshRegions -cellZones -overwrite"
    
    def get_solver_command(self) -> str:
        """Get solver execution command."""
        if not self.solver_name:
            raise ValueError("Solver name not set")
        return self.solver_name
    
    def get_paraview_command(self) -> str:
        """Get ParaView command."""
        return "paraview"
