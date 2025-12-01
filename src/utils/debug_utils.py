"""
Debug utilities for Battery Simulator OpenFOAM integration.

This module provides comprehensive debugging tools for validating and troubleshooting
OpenFOAM integration, including path resolution, solver execution, and template validation.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class OpenFOAMDebugger:
    """
    Comprehensive debugger for OpenFOAM integration.
    
    Provides tools for validating OpenFOAM installation, solver compilation,
    template files, and simulation execution.
    """
    
    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize the OpenFOAM debugger.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        self.openfoam_env = {}
        self.validation_results = {}
        
    def validate_openfoam_environment(self) -> Dict[str, Any]:
        """
        Validate OpenFOAM installation and environment.
        
        Returns:
            Dict containing validation results
        """
        logger.info("Starting OpenFOAM environment validation...")
        results = {}
        
        # Check OpenFOAM environment variables
        env_vars = ['FOAM_INST_DIR', 'FOAM_APPBIN', 'FOAM_RUN', 'FOAM_SOLVERS']
        for var in env_vars:
            value = os.environ.get(var)
            results[f'env_{var}'] = {
                'exists': value is not None,
                'value': value or 'Not set'
            }
            logger.info(f"{var}: {value or 'Not set'}")
        
        # Check OpenFOAM commands
        commands_to_check = ['foamInfoExec', 'blockMesh', 'topoSet', 'decomposePar', 'reconstructPar']
        for cmd in commands_to_check:
            try:
                result = subprocess.run([cmd, '--help'], capture_output=True, text=True, timeout=10)
                results[f'cmd_{cmd}'] = {
                    'available': result.returncode == 0,
                    'output': result.stdout[:200] if result.returncode == 0 else result.stderr[:200]
                }
                logger.info(f"Command {cmd}: {'Available' if result.returncode == 0 else 'Not available'}")
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                results[f'cmd_{cmd}'] = {
                    'available': False,
                    'error': str(e)
                }
                logger.error(f"Command {cmd} failed: {e}")
        
        # Check solver compilation
        if self.project_path:
            solver_path = Path(self.project_path) / "solvers"
            if solver_path.exists():
                results['solver_compilation'] = self._check_solver_compilation(solver_path)
            else:
                results['solver_compilation'] = {'available': False, 'error': 'Solver path not found'}
                logger.warning("Solver path not found")
        
        self.validation_results['openfoam_env'] = results
        return results
    
    def _check_solver_compilation(self, solver_path: Path) -> Dict[str, Any]:
        """Check if solvers are compiled and available."""
        results = {}
        solver_names = ['SPMFoam', 'halfCellFoam', 'fullCellFoam']
        
        for solver in solver_names:
            solver_bin = Path(os.environ.get('FOAM_APPBIN', '')) / solver
            results[solver] = {
                'compiled': solver_bin.exists(),
                'path': str(solver_bin)
            }
            logger.info(f"{solver}: {'Compiled' if solver_bin.exists() else 'Not compiled'}")
        
        return results
    
    def validate_template_files(self, template_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate template files for OpenFOAM cases.
        
        Args:
            template_path: Path to template directory
            
        Returns:
            Dict containing validation results
        """
        logger.info("Starting template file validation...")
        results = {}
        
        if not template_path:
            # Default template path
            template_path = Path(__file__).parent.parent.parent / "resources" / "templates"
        else:
            template_path = Path(template_path)
        
        if not template_path.exists():
            results['template_path'] = {'exists': False, 'error': 'Template path not found'}
            logger.error(f"Template path not found: {template_path}")
            return results
        
        results['template_path'] = {'exists': True, 'path': str(template_path)}
        
        # Check required template files
        required_files = [
            'system/blockMeshDict',
            'system/topoSetDict',
            'system/controlDict',
            'system/fvSchemes',
            'system/fvSolution',
            'constant/LiProperties'
        ]
        
        for file_path in required_files:
            full_path = template_path / file_path
            results[f'template_{file_path}'] = {
                'exists': full_path.exists(),
                'path': str(full_path)
            }
            logger.info(f"Template {file_path}: {'Found' if full_path.exists() else 'Not found'}")
        
        self.validation_results['templates'] = results
        return results
    
    def validate_case_structure(self, case_path: str) -> Dict[str, Any]:
        """
        Validate OpenFOAM case structure and files.
        
        Args:
            case_path: Path to the OpenFOAM case directory
            
        Returns:
            Dict containing validation results
        """
        logger.info(f"Starting case structure validation for: {case_path}")
        results = {}
        case_path = Path(case_path)
        
        if not case_path.exists():
            results['case_path'] = {'exists': False, 'error': 'Case path not found'}
            logger.error(f"Case path not found: {case_path}")
            return results
        
        results['case_path'] = {'exists': True, 'path': str(case_path)}
        
        # Check required directories
        required_dirs = ['0', 'constant', 'system']
        for dir_name in required_dirs:
            dir_path = case_path / dir_name
            results[f'dir_{dir_name}'] = {
                'exists': dir_path.exists(),
                'path': str(dir_path)
            }
            logger.info(f"Directory {dir_name}: {'Found' if dir_path.exists() else 'Not found'}")
        
        # Check required files
        required_files = [
            'system/blockMeshDict',
            'system/topoSetDict',
            'system/controlDict',
            'system/fvSchemes',
            'system/fvSolution',
            'constant/LiProperties'
        ]
        
        for file_path in required_files:
            full_path = case_path / file_path
            results[f'file_{file_path}'] = {
                'exists': full_path.exists(),
                'path': str(full_path),
                'size': full_path.stat().st_size if full_path.exists() else 0
            }
            logger.info(f"File {file_path}: {'Found' if full_path.exists() else 'Not found'}")
        
        self.validation_results['case_structure'] = results
        return results
    
    def monitor_solver_execution(self, solver_cmd: List[str], case_path: str) -> Dict[str, Any]:
        """
        Monitor OpenFOAM solver execution and capture output.
        
        Args:
            solver_cmd: Command to run the solver
            case_path: Path to the case directory
            
        Returns:
            Dict containing execution results
        """
        logger.info(f"Starting solver execution monitoring: {' '.join(solver_cmd)}")
        results = {}
        
        try:
            # Change to case directory
            original_cwd = os.getcwd()
            os.chdir(case_path)
            
            # Run solver with real-time output capture
            process = subprocess.Popen(
                solver_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            output_lines = []
            start_time = datetime.now()
            
            # Monitor output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_lines.append(output.strip())
                    logger.debug(f"Solver output: {output.strip()}")
            
            end_time = datetime.now()
            exit_code = process.poll()
            
            # Restore working directory
            os.chdir(original_cwd)
            
            results = {
                'exit_code': exit_code,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration': str(end_time - start_time),
                'output_lines': len(output_lines),
                'output_sample': output_lines[-10:] if output_lines else [],
                'success': exit_code == 0
            }
            
            logger.info(f"Solver execution completed with exit code: {exit_code}")
            logger.info(f"Execution time: {results['duration']}")
            
        except Exception as e:
            logger.error(f"Solver execution failed: {e}")
            results = {
                'exit_code': -1,
                'error': str(e),
                'success': False
            }
        
        self.validation_results['solver_execution'] = results
        return results
    
    def generate_debug_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive debug report.
        
        Args:
            output_path: Path to save the debug report
            
        Returns:
            Path to the generated report
        """
        if not output_path:
            output_path = Path(self.project_path) / "debug_report.txt" if self.project_path else Path("debug_report.txt")
        else:
            output_path = Path(output_path)
        
        with open(output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("Battery Simulator OpenFOAM Integration Debug Report\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            # Environment validation
            f.write("OPENFOAM ENVIRONMENT VALIDATION\n")
            f.write("-" * 40 + "\n")
            env_results = self.validation_results.get('openfoam_env', {})
            for key, value in env_results.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # Template validation
            f.write("TEMPLATE FILE VALIDATION\n")
            f.write("-" * 40 + "\n")
            template_results = self.validation_results.get('templates', {})
            for key, value in template_results.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # Case structure validation
            f.write("CASE STRUCTURE VALIDATION\n")
            f.write("-" * 40 + "\n")
            case_results = self.validation_results.get('case_structure', {})
            for key, value in case_results.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # Solver execution results
            f.write("SOLVER EXECUTION RESULTS\n")
            f.write("-" * 40 + "\n")
            solver_results = self.validation_results.get('solver_execution', {})
            for key, value in solver_results.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
        
        logger.info(f"Debug report generated: {output_path}")
        return str(output_path)


def debug_openfoam_integration(project_path: Optional[str] = None, case_path: Optional[str] = None) -> OpenFOAMDebugger:
    """
    Perform comprehensive OpenFOAM integration debugging.
    
    Args:
        project_path: Path to the project directory
        case_path: Path to the OpenFOAM case directory
        
    Returns:
        OpenFOAMDebugger instance with validation results
    """
    debugger = OpenFOAMDebugger(project_path)
    
    # Validate OpenFOAM environment
    debugger.validate_openfoam_environment()
    
    # Validate template files
    debugger.validate_template_files()
    
    # Validate case structure if case_path provided
    if case_path:
        debugger.validate_case_structure(case_path)
    
    return debugger


def check_solver_availability() -> Dict[str, bool]:
    """
    Check availability of required OpenFOAM solvers.
    
    Returns:
        Dict mapping solver names to availability status
    """
    solvers = ['SPMFoam', 'halfCellFoam', 'fullCellFoam']
    results = {}
    
    foam_appbin = os.environ.get('FOAM_APPBIN', '')
    if not foam_appbin or not os.path.exists(foam_appbin):
        logger.warning(f"FOAM_APPBIN not set or not found: {foam_appbin}")
        return {solver: False for solver in solvers}
    
    for solver in solvers:
        solver_path = Path(foam_appbin) / solver
        results[solver] = solver_path.exists()
        logger.info(f"{solver}: {'Available' if results[solver] else 'Not available'}")
    
    return results


def validate_openfoam_installation() -> bool:
    """
    Validate basic OpenFOAM installation.
    
    Returns:
        True if OpenFOAM appears to be properly installed, False otherwise
    """
    try:
        # Check if foamInfoExec is available
        result = subprocess.run(['foamInfoExec'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logger.error("foamInfoExec command failed")
            return False
        
        # Check for required environment variables
        required_vars = ['FOAM_INST_DIR', 'FOAM_APPBIN']
        for var in required_vars:
            if not os.environ.get(var):
                logger.error(f"Required environment variable {var} not set")
                return False
        
        logger.info("OpenFOAM installation appears to be valid")
        return True
        
    except Exception as e:
        logger.error(f"OpenFOAM installation validation failed: {e}")
        return False
