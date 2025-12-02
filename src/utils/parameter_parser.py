"""
Parameter parsing utilities for Battery Simulator.

This module provides the ParameterManager class for parsing and managing
simulation parameters from various OpenFOAM configuration files.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List


class ParameterManager:
    """
    Manager for parameter file operations.
    
    Handles loading and saving of parameters from OpenFOAM configuration files.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the parameter manager.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        
    def load_geometry_parameters(self) -> Dict[str, Any]:
        """
        Load geometry parameters from blockMeshDict and topoSetDict.
        
        Returns:
            Dict containing geometry parameters
        """
        params = {}
        
        # Load from blockMeshDict
        blockmesh_path = os.path.join(self.project_path, self._get_parameter_file("blockMeshDict"))
        if os.path.exists(blockmesh_path):
            params.update(self._parse_blockmesh_dict(blockmesh_path))
            
        # Load from topoSetDict
        topo_path = os.path.join(self.project_path, self._get_parameter_file("topoSetDict"))
        if os.path.exists(topo_path):
            params.update(self._parse_topo_set_dict(topo_path))
            
        return params
        
    def _parse_blockmesh_dict(self, file_path: str) -> Dict[str, Any]:
        """
        Parse blockMeshDict file for geometry parameters.
        
        Args:
            file_path: Path to blockMeshDict file
            
        Returns:
            Dict containing parsed parameters
        """
        params = {}
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Extract dimensions from vertices
            # Pattern: (-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)
            vertices_pattern = r'\((-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\)'
            matches = re.findall(vertices_pattern, content)
            
            if len(matches) >= 8:
                # Get min and max coordinates from vertices
                x_coords = [float(m[0]) for m in matches]
                y_coords = [float(m[1]) for m in matches]
                z_coords = [float(m[2]) for m in matches]
                
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                z_min, z_max = min(z_coords), max(z_coords)
                
                # Calculate dimensions (assuming symmetric around origin)
                params['length'] = abs(x_max - x_min)
                params['width'] = abs(y_max - y_min)
                params['height'] = abs(z_max - z_min)
                
            # Extract division counts
            division_pattern = r'\((\d+)\s+(\d+)\s+(\d+)\)\s+simpleGrading'
            division_match = re.search(division_pattern, content)
            if division_match:
                params['x_division'] = int(division_match.group(1))
                params['y_division'] = int(division_match.group(2))
                params['z_division'] = int(division_match.group(3))
                
            # Extract unit conversion
            unit_pattern = r'convertToMeters\s+([0-9.e-]+)'
            unit_match = re.search(unit_pattern, content)
            if unit_match:
                unit_value = float(unit_match.group(1))
                if unit_value == 1e-6:
                    params['unit'] = 'micrometer'
                elif unit_value == 1e-3:
                    params['unit'] = 'millimeter'
                elif unit_value == 1e-0:
                    params['unit'] = 'meter'
                    
        except Exception as e:
            print(f"Error parsing blockMeshDict: {e}")
            
        return params
        
    def _parse_topo_set_dict(self, file_path: str) -> Dict[str, Any]:
        """
        Parse topoSetDict file for radius parameter.
        
        Args:
            file_path: Path to topoSetDict file
            
        Returns:
            Dict containing parsed parameters
        """
        params = {}
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Extract radius
            radius_pattern = r'radius\s+([0-9.e-]+)'
            radius_match = re.search(radius_pattern, content)
            if radius_match:
                params['radius'] = float(radius_match.group(1))
                
        except Exception as e:
            print(f"Error parsing topoSetDict: {e}")
            
        return params
        
    def load_material_parameters(self) -> Dict[str, Any]:
        """
        Load material parameters from LiProperties file.
        
        Returns:
            Dict containing material parameters
        """
        params = {}
        
        li_properties_path = os.path.join(self.project_path, self._get_parameter_file("LiProperties"))
        if os.path.exists(li_properties_path):
            params.update(self._parse_li_properties(li_properties_path))
            
        return params
        
    def _parse_li_properties(self, file_path: str) -> Dict[str, Any]:
        """
        Parse LiProperties file for material parameters.
        
        Args:
            file_path: Path to LiProperties file
            
        Returns:
            Dict containing parsed parameters
        """
        params = {}
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Extract various parameters
            parameter_patterns = {
                'Ds_value': r'Ds_value\s+\[.*?\]\s+([0-9.e-]+)',
                'CS_max': r'Cs_max\s+\[.*?\]\s+([0-9.e-]+)',
                'kReact': r'kReact\s+\[.*?\]\s+([0-9.e-]+)',
                'R': r'R\s+\[.*?\]\s+([0-9.e-]+)',
                'F': r'F\s+\[.*?\]\s+([0-9.e-]+)',
                'Ce': r'Ce\s+\[.*?\]\s+([0-9.e-]+)',
                'alphaA': r'alphaA\s+\[.*?\]\s+([0-9.e-]+)',
                'alphaC': r'alphaC\s+\[.*?\]\s+([0-9.e-]+)',
                'T_temp': r'T_temp\s+\[.*?\]\s+([0-9.e-]+)',
                'I_app': r'I_app\s+\[.*?\]\s+([0-9.e-]+)'
            }
            
            for param, pattern in parameter_patterns.items():
                match = re.search(pattern, content)
                if match:
                    params[param] = float(match.group(1))
                    
        except Exception as e:
            print(f"Error parsing LiProperties: {e}")
            
        return params
        
    def load_solver_parameters(self) -> Dict[str, Any]:
        """
        Load solver parameters from fvSchemes and fvSolution.
        
        Returns:
            Dict containing solver parameters
        """
        params = {}
        
        # Load from fvSchemes
        fv_schemes_path = os.path.join(self.project_path, self._get_parameter_file("fvSchemes"))
        if os.path.exists(fv_schemes_path):
            params.update(self._parse_fv_schemes(fv_schemes_path))
            
        # Load from fvSolution
        fv_solution_path = os.path.join(self.project_path, self._get_parameter_file("fvSolution"))
        if os.path.exists(fv_solution_path):
            params.update(self._parse_fv_solution(fv_solution_path))
            
        return params
        
    def _parse_fv_schemes(self, file_path: str) -> Dict[str, Any]:
        """
        Parse fvSchemes file for solver scheme parameters.
        
        Args:
            file_path: Path to fvSchemes file
            
        Returns:
            Dict containing parsed parameters
        """
        params = {}
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Extract scheme selections
            scheme_patterns = {
                'ddtSchemes': r'ddtSchemes\s*{[^}]*default\s+([^;]+)',
                'gradSchemes': r'gradSchemes\s*{[^}]*default\s+([^;]+)',
                'divSchemes': r'divSchemes\s*{[^}]*default\s+([^;]+)',
                'laplacianSchemes': r'laplacianSchemes\s*{[^}]*default\s+([^;]+)',
                'interpolationSchemes': r'interpolationSchemes\s*{[^}]*default\s+([^;]+)'
            }
            
            for scheme, pattern in scheme_patterns.items():
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    params[scheme] = match.group(1).strip()
                    
        except Exception as e:
            print(f"Error parsing fvSchemes: {e}")
            
        return params
        
    def _parse_fv_solution(self, file_path: str) -> Dict[str, Any]:
        """
        Parse fvSolution file for solver tolerance parameters.
        
        Args:
            file_path: Path to fvSolution file
            
        Returns:
            Dict containing parsed parameters
        """
        params = {}
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Extract tolerance
            tolerance_pattern = r'tolerance\s+([0-9.e-]+)'
            tolerance_match = re.search(tolerance_pattern, content)
            if tolerance_match:
                params['tolerance'] = float(tolerance_match.group(1))
                
        except Exception as e:
            print(f"Error parsing fvSolution: {e}")
            
        return params
        
    def load_control_parameters(self) -> Dict[str, Any]:
        """
        Load control parameters from controlDict.
        
        Returns:
            Dict containing control parameters
        """
        params = {}
        
        control_dict_path = os.path.join(self.project_path, self._get_parameter_file("controlDict"))
        if os.path.exists(control_dict_path):
            params.update(self._parse_control_dict(control_dict_path))
            
        return params
        
    def _parse_control_dict(self, file_path: str) -> Dict[str, Any]:
        """
        Parse controlDict file for simulation control parameters.
        
        Args:
            file_path: Path to controlDict file
            
        Returns:
            Dict containing parsed parameters
        """
        params = {}
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Extract control parameters
            control_patterns = {
                'endTime': r'endTime\s+([0-9.e-]+)',
                'deltaT': r'deltaT\s+([0-9.e-]+)',
                'writeInterval': r'writeInterval\s+([0-9.e-]+)'
            }
            
            for param, pattern in control_patterns.items():
                match = re.search(pattern, content)
                if match:
                    params[param] = float(match.group(1))
                    
        except Exception as e:
            print(f"Error parsing controlDict: {e}")
            
        return params
        
    def save_geometry_parameters(self, params: Dict[str, Any]):
        """
        Save geometry parameters to configuration files.
        
        Args:
            params: Dictionary of parameters to save
        """
        # Update blockMeshDict
        blockmesh_path = os.path.join(self.project_path, self._get_parameter_file("blockMeshDict"))
        if os.path.exists(blockmesh_path):
            self._update_blockmesh_dict(blockmesh_path, params)
            
        # Update topoSetDict
        topo_path = os.path.join(self.project_path, self._get_parameter_file("topoSetDict"))
        if os.path.exists(topo_path):
            self._update_topo_set_dict(topo_path, params)
            
    def _update_blockmesh_dict(self, file_path: str, params: Dict[str, Any]):
        """
        Update blockMeshDict with new geometry parameters.
        
        Args:
            file_path: Path to blockMeshDict file
            params: Dictionary of parameters to update
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Update dimensions if provided
            if 'length' in params and 'width' in params and 'height' in params:
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
                
        except Exception as e:
            print(f"Error updating blockMeshDict: {e}")
            
    def _update_topo_set_dict(self, file_path: str, params: Dict[str, Any]):
        """
        Update topoSetDict with new radius parameter.
        
        Args:
            file_path: Path to topoSetDict file
            params: Dictionary of parameters to update
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Update radius if provided
            if 'radius' in params:
                content = re.sub(r'radius\s+[0-9.e-]+', f'radius {params["radius"]}', content)
                
            with open(file_path, 'w') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Error updating topoSetDict: {e}")
            
    def load_all_parameters(self) -> Dict[str, Any]:
        """
        Load all parameters from configuration files.
        
        Returns:
            Dict containing all parameters
        """
        all_params = {}
        all_params.update(self.load_geometry_parameters())
        all_params.update(self.load_material_parameters())
        all_params.update(self.load_solver_parameters())
        all_params.update(self.load_control_parameters())
        return all_params
        
    def save_all_parameters(self, params: Dict[str, Any]):
        """
        Save all parameters to configuration files.
        
        Args:
            params: Dictionary of all parameters to save
        """
        self.save_geometry_parameters(params)
        # Additional save methods can be added here for other parameter types
        
    def _get_parameter_file(self, file_type: str) -> str:
        """Get the path to a parameter file."""
        from src.core.constants import PARAMETER_FILES
        return PARAMETER_FILES[file_type]