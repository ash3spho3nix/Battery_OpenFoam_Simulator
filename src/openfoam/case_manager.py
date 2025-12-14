"""
OpenFOAM case directory manager.

This module provides the OpenFOAMCaseManager class, which handles
OpenFOAM case directory setup, configuration, and management.
"""

import os
import shutil
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from PyQt6.QtCore import QObject, pyqtSignal

from ..utils.parameter_parser import ParameterManager
from ..core.constants import PARAMETER_FILES


class OpenFOAMCaseManager(QObject):
    """
    Manager for OpenFOAM case directories and configuration.
    
    Handles case setup, parameter file management, and directory operations.
    """
    
    # Signals for case operations
    case_created = pyqtSignal(str)  # case_path
    case_validated = pyqtSignal(bool)  # is_valid
    parameter_updated = pyqtSignal(str)  # parameter_name
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, case_path: str, parent=None):
        """
        Initialize the case manager.
        
        Args:
            case_path: Path to the OpenFOAM case directory
            parent: Parent QObject
        """
        super().__init__(parent)
        self.case_path = case_path
        self.parameter_manager = ParameterManager(case_path)
        self._case_structure = self._get_case_structure()
        
    def _get_case_structure(self) -> Dict[str, List[str]]:
        """Define the expected OpenFOAM case directory structure."""
        return {
            'system': [
                'blockMeshDict',
                'topoSetDict', 
                'controlDict',
                'fvSchemes',
                'fvSolution'
            ],
            'constant': [
                'LiProperties'
            ],
            '0': [
                'C',
                'Cs',
                'p'
            ]
        }
        
    def create_case_structure(self) -> bool:
        """
        Create the OpenFOAM case directory structure.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create main case directory
            os.makedirs(self.case_path, exist_ok=True)
            
            # Create required subdirectories
            for subdir in self._case_structure.keys():
                subdir_path = os.path.join(self.case_path, subdir)
                os.makedirs(subdir_path, exist_ok=True)
                
            # Create processor directories if needed (for parallel execution)
            self._create_processor_directories()
            
            self.case_created.emit(self.case_path)
            return True
            
        except Exception as e:
            error_msg = f"Failed to create case structure: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def _create_processor_directories(self):
        """Create processor directories for parallel execution."""
        # Check if decomposeParDict exists (indicating parallel setup needed)
        decompose_dict = os.path.join(self.case_path, 'system', 'decomposeParDict')
        if os.path.exists(decompose_dict):
            try:
                # Read number of subdomains from decomposeParDict
                with open(decompose_dict, 'r') as f:
                    content = f.read()
                    n_subdomains_match = re.search(r'n\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)', content)
                    if n_subdomains_match:
                        nx, ny, nz = map(int, n_subdomains_match.groups())
                        n_processors = nx * ny * nz
                        
                        # Create processor directories
                        for i in range(n_processors):
                            proc_dir = os.path.join(self.case_path, f'processor{i}')
                            os.makedirs(proc_dir, exist_ok=True)
                            
            except Exception as e:
                self.error_occurred.emit(f"Failed to create processor directories: {e}")
                
    def validate_case_structure(self) -> bool:
        """
        Validate the OpenFOAM case directory structure.
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            is_valid = True
            missing_files = []
            
            # Check required directories
            for subdir, files in self._case_structure.items():
                subdir_path = os.path.join(self.case_path, subdir)
                if not os.path.exists(subdir_path):
                    missing_files.append(f"Missing directory: {subdir}")
                    is_valid = False
                    continue
                    
                # Check required files in each directory
                for file_name in files:
                    file_path = os.path.join(subdir_path, file_name)
                    if not os.path.exists(file_path):
                        missing_files.append(f"Missing file: {subdir}/{file_name}")
                        is_valid = False
                        
            if not is_valid:
                error_msg = "Case structure validation failed:\n" + "\n".join(missing_files)
                self.error_occurred.emit(error_msg)
                
            self.case_validated.emit(is_valid)
            return is_valid
            
        except Exception as e:
            error_msg = f"Case validation error: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.case_validated.emit(False)
            return False
            
    def update_geometry_parameters(self, params: Dict[str, Any]) -> bool:
        """
        Update geometry parameters in blockMeshDict and topoSetDict.
        
        Args:
            params: Dictionary of geometry parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update blockMeshDict
            blockmesh_path = os.path.join(self.case_path, 'system', 'blockMeshDict')
            if os.path.exists(blockmesh_path):
                self._update_blockmesh_dict(blockmesh_path, params)
                self.parameter_updated.emit('geometry')
                
            # Update topoSetDict
            topo_path = os.path.join(self.case_path, 'system', 'topoSetDict')
            if os.path.exists(topo_path):
                self._update_topo_set_dict(topo_path, params)
                self.parameter_updated.emit('geometry')
                
            return True
            
        except Exception as e:
            error_msg = f"Failed to update geometry parameters: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def _update_blockmesh_dict(self, file_path: str, params: Dict[str, Any]):
        """
        Update blockMeshDict with new geometry parameters.
        
        Args:
            file_path: Path to blockMeshDict file
            params: Dictionary of parameters to update
        """
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Update dimensions if provided
        if all(k in params for k in ['length', 'width', 'height']):
            length = params['length'] / 2
            width = params['width'] / 2
            height = params['height'] / 2
            
            # Replace vertex coordinates
            vertex_pattern = r'\((-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\)'
            vertices = re.findall(vertex_pattern, content)
            
            if len(vertices) >= 8:
                # Update the 8 vertices with new dimensions
                new_vertices = [
                    (-length, -width, -height),
                    (-length, width, -height),
                    (-length, width, height),
                    (-length, -width, height),
                    (length, -width, -height),
                    (length, width, -height),
                    (length, width, height),
                    (length, -width, height)
                ]
                
                # Replace each vertex
                for i, new_vertex in enumerate(new_vertices):
                    old_vertex = vertices[i]
                    old_str = f"({old_vertex[0]} {old_vertex[1]} {old_vertex[2]})"
                    new_str = f"({new_vertex[0]} {new_vertex[1]} {new_vertex[2]})"
                    content = content.replace(old_str, new_str, 1)
                    
        # Update divisions if provided
        if all(k in params for k in ['x_division', 'y_division', 'z_division']):
            old_division = f"({params.get('x_division', 20)} {params.get('y_division', 20)} {params.get('z_division', 20)})"
            new_division = f"({params['x_division']} {params['y_division']} {params['z_division']})"
            content = content.replace(old_division, new_division)
            
        # Update unit if provided
        if 'unit' in params:
            unit_value = {'micrometer': '1e-6', 'millimeter': '1e-3', 'meter': '1e-0'}[params['unit']]
            content = re.sub(r'convertToMeters\s+[0-9.e-]+', f'convertToMeters {unit_value}', content)
            
        with open(file_path, 'w') as f:
            f.write(content)
            
    def _update_topo_set_dict(self, file_path: str, params: Dict[str, Any]):
        """
        Update topoSetDict with new radius parameter.
        
        Args:
            file_path: Path to topoSetDict file
            params: Dictionary of parameters to update
        """
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Update radius if provided
        if 'radius' in params:
            content = re.sub(r'radius\s+[0-9.e-]+', f'radius {params["radius"]}', content)
            
        with open(file_path, 'w') as f:
            f.write(content)
            
    def update_material_parameters(self, params: Dict[str, Any]) -> bool:
        """
        Update material parameters in LiProperties file.
        
        Args:
            params: Dictionary of material parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            li_properties_path = os.path.join(self.case_path, 'constant', 'LiProperties')
            if os.path.exists(li_properties_path):
                self._update_li_properties(li_properties_path, params)
                self.parameter_updated.emit('material')
                return True
            return False
            
        except Exception as e:
            error_msg = f"Failed to update material parameters: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def _update_li_properties(self, file_path: str, params: Dict[str, Any]):
        """
        Update LiProperties file with new material parameters.
        
        Args:
            file_path: Path to LiProperties file
            params: Dictionary of parameters to update
        """
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Update various parameters
        parameter_updates = {
            'Ds_value': 'Ds_value',
            'CS_max': 'Cs_max',
            'kReact': 'kReact',
            'R': 'R',
            'F': 'F',
            'Ce': 'Ce',
            'alphaA': 'alphaA',
            'alphaC': 'alphaC',
            'T_temp': 'T_temp',
            'I_app': 'I_app'
        }
        
        for param_key, file_key in parameter_updates.items():
            if param_key in params:
                pattern = rf'{file_key}\s+\[.*?\]\s+[0-9.e-]+'
                replacement = f'{file_key} [0 0 0 0 0 0 0] {params[param_key]}'
                content = re.sub(pattern, replacement, content)
                
        with open(file_path, 'w') as f:
            f.write(content)
            
    def update_solver_parameters(self, params: Dict[str, Any]) -> bool:
        """
        Update solver parameters in fvSchemes and fvSolution.
        
        Args:
            params: Dictionary of solver parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            success = True
            
            # Update fvSchemes
            fv_schemes_path = os.path.join(self.case_path, 'system', 'fvSchemes')
            if os.path.exists(fv_schemes_path):
                self._update_fv_schemes(fv_schemes_path, params)
                self.parameter_updated.emit('solver')
                
            # Update fvSolution
            fv_solution_path = os.path.join(self.case_path, 'system', 'fvSolution')
            if os.path.exists(fv_solution_path):
                self._update_fv_solution(fv_solution_path, params)
                self.parameter_updated.emit('solver')
                
            return success
            
        except Exception as e:
            error_msg = f"Failed to update solver parameters: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def _update_fv_schemes(self, file_path: str, params: Dict[str, Any]):
        """
        Update fvSchemes file with new solver scheme parameters.
        
        Args:
            file_path: Path to fvSchemes file
            params: Dictionary of parameters to update
        """
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Update scheme selections
        scheme_updates = {
            'ddtSchemes': 'ddtSchemes',
            'gradSchemes': 'gradSchemes',
            'divSchemes': 'divSchemes',
            'laplacianSchemes': 'laplacianSchemes',
            'interpolationSchemes': 'interpolationSchemes'
        }
        
        for param_key, file_key in scheme_updates.items():
            if param_key in params:
                pattern = rf'{file_key}\s*{{[^}}]*default\s+[^;]+}}'
                replacement = f'{file_key} {{ default {params[param_key]}; }}'
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                
        with open(file_path, 'w') as f:
            f.write(content)
            
    def _update_fv_solution(self, file_path: str, params: Dict[str, Any]):
        """
        Update fvSolution file with new solver tolerance parameters.
        
        Args:
            file_path: Path to fvSolution file
            params: Dictionary of parameters to update
        """
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Update tolerance if provided
        if 'tolerance' in params:
            content = re.sub(r'tolerance\s+[0-9.e-]+', f'tolerance {params["tolerance"]}', content)
            
        with open(file_path, 'w') as f:
            f.write(content)
            
    def update_control_parameters(self, params: Dict[str, Any]) -> bool:
        """
        Update control parameters in controlDict.
        
        Args:
            params: Dictionary of control parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            control_dict_path = os.path.join(self.case_path, 'system', 'controlDict')
            if os.path.exists(control_dict_path):
                self._update_control_dict(control_dict_path, params)
                self.parameter_updated.emit('control')
                return True
            return False
            
        except Exception as e:
            error_msg = f"Failed to update control parameters: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def _update_control_dict(self, file_path: str, params: Dict[str, Any]):
        """
        Update controlDict file with new control parameters.
        
        Args:
            file_path: Path to controlDict file
            params: Dictionary of parameters to update
        """
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Update control parameters
        control_updates = {
            'endTime': 'endTime',
            'deltaT': 'deltaT',
            'writeInterval': 'writeInterval'
        }
        
        for param_key, file_key in control_updates.items():
            if param_key in params:
                content = re.sub(rf'{file_key}\s+[0-9.e-]+', f'{file_key} {params[param_key]}', content)
                
        with open(file_path, 'w') as f:
            f.write(content)
            
    def setup_initial_conditions(self, initial_values: Dict[str, Any]) -> bool:
        """
        Set up initial conditions for the simulation.
        
        Args:
            initial_values: Dictionary of initial values
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create initial condition files in the '0' directory
            zero_dir = os.path.join(self.case_path, '0')
            os.makedirs(zero_dir, exist_ok=True)
            
            # Create C field file
            if 'C' in initial_values:
                self._create_field_file(os.path.join(zero_dir, 'C'), 'C', initial_values['C'])
                
            # Create Cs field file
            if 'Cs' in initial_values:
                self._create_field_file(os.path.join(zero_dir, 'Cs'), 'Cs', initial_values['Cs'])
                
            # Create pressure file
            if 'p' in initial_values:
                self._create_field_file(os.path.join(zero_dir, 'p'), 'p', initial_values['p'])
                
            return True
            
        except Exception as e:
            error_msg = f"Failed to setup initial conditions: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def _create_field_file(self, file_path: str, field_name: str, value: float):
        """
        Create an OpenFOAM field file.
        
        Args:
            file_path: Path to the field file
            field_name: Name of the field
            value: Initial value for the field
        """
        content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\    /   O peration     | Version:  6                                     |
|   \\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      {field_name};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 0 0 0 0];

internalField   uniform {value};

boundaryField
{{
    inlet
    {{
        type            zeroGradient;
    }}

    outlet
    {{
        type            zeroGradient;
    }}

    walls
    {{
        type            zeroGradient;
    }}

    defaultFaces
    {{
        type            empty;
    }}
}}


// ************************************************************************* //
"""
        with open(file_path, 'w') as f:
            f.write(content)
            
    def backup_case(self, backup_path: str) -> bool:
        """
        Create a backup of the case directory.
        
        Args:
            backup_path: Path where the backup should be created
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
                
            shutil.copytree(self.case_path, backup_path)
            return True
            
        except Exception as e:
            error_msg = f"Failed to backup case: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def restore_case(self, backup_path: str) -> bool:
        """
        Restore a case from backup.
        
        Args:
            backup_path: Path to the backup directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup not found: {backup_path}")
                
            # Remove current case and restore from backup
            if os.path.exists(self.case_path):
                shutil.rmtree(self.case_path)
                
            shutil.copytree(backup_path, self.case_path)
            return True
            
        except Exception as e:
            error_msg = f"Failed to restore case: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
            
    def get_case_info(self) -> Dict[str, Any]:
        """
        Get information about the current case.
        
        Returns:
            Dict containing case information
        """
        info = {
            'path': self.case_path,
            'exists': os.path.exists(self.case_path),
            'structure_valid': self.validate_case_structure(),
            'parameters': self.parameter_manager.load_all_parameters()
        }
        
        # Add file sizes and modification times
        file_info = {}
        for subdir, files in self._case_structure.items():
            subdir_path = os.path.join(self.case_path, subdir)
            if os.path.exists(subdir_path):
                for file_name in files:
                    file_path = os.path.join(subdir_path, file_name)
                    if os.path.exists(file_path):
                        stat = os.stat(file_path)
                        file_info[f"{subdir}/{file_name}"] = {
                            'size': stat.st_size,
                            'modified': stat.st_mtime
                        }
                        
        info['files'] = file_info
        return info
