"""
Enhanced Parameter Manager for Battery Simulator.

This module provides an advanced ParameterManager class with comprehensive
OpenFOAM-specific parameter parsing, validation, and management capabilities.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ParameterValidationError(Exception):
    """Exception raised when parameter validation fails."""
    pass


class OpenFOAMParseError(Exception):
    """Exception raised when OpenFOAM file parsing fails."""
    pass


class ParameterDefinition:
    """Definition of a parameter with validation rules."""
    
    def __init__(self, definition: Dict[str, Any]):
        self.name = definition.get('name', '')
        self.type = definition.get('type', 'string')
        self.description = definition.get('description', '')
        self.default_value = definition.get('default_value')
        self.min_value = definition.get('min_value')
        self.max_value = definition.get('max_value')
        self.allowed_values = definition.get('allowed_values', [])
        self.required = definition.get('required', False)
        self.pattern = definition.get('pattern')
        self.units = definition.get('units', '')
        self.category = definition.get('category', 'general')
        
    def validate(self, value: Any) -> bool:
        """Validate a value against this parameter definition."""
        if value is None and self.required:
            return False
            
        if value is None and not self.required:
            return True
            
        # Type validation
        if self.type == 'int':
            if not isinstance(value, int):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    return False
        elif self.type == 'float':
            if not isinstance(value, (int, float)):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    return False
        elif self.type == 'string':
            value = str(value)
        elif self.type == 'bool':
            if not isinstance(value, bool):
                value = bool(value)
                
        # Range validation for numeric types
        if self.type in ['int', 'float'] and value is not None:
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
                
        # Allowed values validation
        if self.allowed_values and value not in self.allowed_values:
            return False
            
        # Pattern validation for strings
        if self.pattern and isinstance(value, str):
            if not re.match(self.pattern, value):
                return False
                
        return True
        
    def get_default(self):
        """Get the default value for this parameter."""
        return self.default_value


class ParameterManager:
    """
    Enhanced parameter manager for OpenFOAM-specific operations.
    
    Provides comprehensive parameter parsing, validation, and management
    for OpenFOAM configuration files with advanced features.
    """
    
    # OpenFOAM file patterns
    OPENFOAM_PATTERNS = {
        'blockMeshDict': {
            'vertices': r'vertices\s*\((.*?)\);',
            'blocks': r'blocks\s*\((.*?)\);',
            'edges': r'edges\s*\((.*?)\);',
            'boundary': r'boundary\s*\{(.*?)\}',
            'convertToMeters': r'convertToMeters\s+([0-9.e-]+)'
        },
        'topoSetDict': {
            'actions': r'actions\s*\{(.*?)\}',
            'radius': r'radius\s+([0-9.e-]+)',
            'center': r'center\s*\(([-0-9.e\s]+)\)'
        },
        'LiProperties': {
            'properties': r'(\w+)\s*\[.*?\]\s+([0-9.e-]+)'
        },
        'fvSchemes': {
            'ddtSchemes': r'ddtSchemes\s*\{(.*?)\}',
            'gradSchemes': r'gradSchemes\s*\{(.*?)\}',
            'divSchemes': r'divSchemes\s*\{(.*?)\}',
            'laplacianSchemes': r'laplacianSchemes\s*\{(.*?)\}',
            'interpolationSchemes': r'interpolationSchemes\s*\{(.*?)\}'
        },
        'fvSolution': {
            'solvers': r'solvers\s*\{(.*?)\}',
            'tolerance': r'tolerance\s+([0-9.e-]+)',
            'relTol': r'relTol\s+([0-9.e-]+)'
        },
        'controlDict': {
            'endTime': r'endTime\s+([0-9.e-]+)',
            'deltaT': r'deltaT\s+([0-9.e-]+)',
            'writeInterval': r'writeInterval\s+([0-9.e-]+)',
            'writeControl': r'writeControl\s+(\w+)'
        }
    }
    
    # Parameter definitions for validation
    PARAMETER_DEFINITIONS = {
        # Geometry parameters
        'length': ParameterDefinition({
            'name': 'length', 'type': 'float', 'description': 'Geometry length',
            'min_value': 0.001, 'max_value': 1000.0, 'units': 'micrometers',
            'category': 'geometry'
        }),
        'width': ParameterDefinition({
            'name': 'width', 'type': 'float', 'description': 'Geometry width',
            'min_value': 0.001, 'max_value': 1000.0, 'units': 'micrometers',
            'category': 'geometry'
        }),
        'height': ParameterDefinition({
            'name': 'height', 'type': 'float', 'description': 'Geometry height',
            'min_value': 0.001, 'max_value': 1000.0, 'units': 'micrometers',
            'category': 'geometry'
        }),
        'radius': ParameterDefinition({
            'name': 'radius', 'type': 'float', 'description': 'Particle radius',
            'min_value': 0.001, 'max_value': 100.0, 'units': 'micrometers',
            'category': 'geometry'
        }),
        'x_division': ParameterDefinition({
            'name': 'x_division', 'type': 'int', 'description': 'X-axis divisions',
            'min_value': 1, 'max_value': 1000, 'category': 'geometry'
        }),
        'y_division': ParameterDefinition({
            'name': 'y_division', 'type': 'int', 'description': 'Y-axis divisions',
            'min_value': 1, 'max_value': 1000, 'category': 'geometry'
        }),
        'z_division': ParameterDefinition({
            'name': 'z_division', 'type': 'int', 'description': 'Z-axis divisions',
            'min_value': 1, 'max_value': 1000, 'category': 'geometry'
        }),
        'unit': ParameterDefinition({
            'name': 'unit', 'type': 'string', 'description': 'Length unit',
            'allowed_values': ['micrometer', 'millimeter', 'meter'],
            'category': 'geometry'
        }),
        
        # Material parameters
        'DS_value': ParameterDefinition({
            'name': 'DS_value', 'type': 'float', 'description': 'Li Intrinsic diffusivity',
            'min_value': 1e-20, 'max_value': 1e-6, 'category': 'material'
        }),
        'CS_max': ParameterDefinition({
            'name': 'CS_max', 'type': 'float', 'description': 'Maximum Li concentration',
            'min_value': 1000, 'max_value': 100000, 'category': 'material'
        }),
        'kReact': ParameterDefinition({
            'name': 'kReact', 'type': 'float', 'description': 'Reaction rate constant',
            'min_value': 1e-20, 'max_value': 1e-6, 'category': 'material'
        }),
        'R': ParameterDefinition({
            'name': 'R', 'type': 'float', 'description': 'Universal gas constant',
            'default_value': 8.314, 'category': 'material'
        }),
        'F': ParameterDefinition({
            'name': 'F', 'type': 'float', 'description': 'Faraday constant',
            'default_value': 96485, 'category': 'material'
        }),
        'Ce': ParameterDefinition({
            'name': 'Ce', 'type': 'float', 'description': 'Electrolyte concentration',
            'min_value': 0.1, 'max_value': 10000.0, 'category': 'material'
        }),
        'alphaA': ParameterDefinition({
            'name': 'alphaA', 'type': 'float', 'description': 'Anodic transfer coefficient',
            'min_value': 0.0, 'max_value': 1.0, 'category': 'material'
        }),
        'alphaC': ParameterDefinition({
            'name': 'alphaC', 'type': 'float', 'description': 'Cathodic transfer coefficient',
            'min_value': 0.0, 'max_value': 1.0, 'category': 'material'
        }),
        'T_temp': ParameterDefinition({
            'name': 'T_temp', 'type': 'float', 'description': 'Temperature',
            'min_value': 200.0, 'max_value': 400.0, 'units': 'K', 'category': 'material'
        }),
        'I_app': ParameterDefinition({
            'name': 'I_app', 'type': 'float', 'description': 'Applied current density',
            'min_value': -10000.0, 'max_value': 10000.0, 'category': 'material'
        }),
        'initial_cs': ParameterDefinition({
            'name': 'initial_cs', 'type': 'float', 'description': 'Initial Cs value',
            'min_value': 0.0, 'max_value': 100000.0, 'category': 'material'
        }),
        
        # Control parameters
        'endTime': ParameterDefinition({
            'name': 'endTime', 'type': 'float', 'description': 'Simulation end time',
            'min_value': 0.001, 'max_value': 1e6, 'category': 'control'
        }),
        'deltaT': ParameterDefinition({
            'name': 'deltaT', 'type': 'float', 'description': 'Time step',
            'min_value': 1e-6, 'max_value': 1e3, 'category': 'control'
        }),
        'writeInterval': ParameterDefinition({
            'name': 'writeInterval', 'type': 'float', 'description': 'Output write interval',
            'min_value': 1e-3, 'max_value': 1e6, 'category': 'control'
        }),
        'tolerance': ParameterDefinition({
            'name': 'tolerance', 'type': 'float', 'description': 'Solver tolerance',
            'min_value': 1e-12, 'max_value': 1e-3, 'category': 'control'
        }),
        
        # Scheme parameters
        'ddtSchemes': ParameterDefinition({
            'name': 'ddtSchemes', 'type': 'string', 'description': 'Time discretization scheme',
            'allowed_values': ['Euler', 'backward', 'localEuler', 'steadyState'],
            'category': 'scheme'
        }),
        'gradSchemes': ParameterDefinition({
            'name': 'gradSchemes', 'type': 'string', 'description': 'Gradient scheme',
            'allowed_values': ['Gauss linear', 'Gauss cubic', 'leastSquares'],
            'category': 'scheme'
        }),
        'divSchemes': ParameterDefinition({
            'name': 'divSchemes', 'type': 'string', 'description': 'Divergence scheme',
            'allowed_values': ['bounded Gauss upwind', 'Gauss linear'],
            'category': 'scheme'
        }),
        'laplacianSchemes': ParameterDefinition({
            'name': 'laplacianSchemes', 'type': 'string', 'description': 'Laplacian scheme',
            'allowed_values': ['Gauss linear uncorrected', 'Gauss linear corrected', 'Gauss linear orthogonal'],
            'category': 'scheme'
        }),
        'interpolationSchemes': ParameterDefinition({
            'name': 'interpolationSchemes', 'type': 'string', 'description': 'Interpolation scheme',
            'allowed_values': ['linear', 'cubic'],
            'category': 'scheme'
        })
    }
    
    def __init__(self, project_path: Union[str, Path]):
        """
        Initialize the enhanced parameter manager.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path)
        self._cache = {}
        self._validation_errors = []
        
    def load_all_parameters(self) -> Dict[str, Any]:
        """
        Load all parameters from OpenFOAM configuration files.
        
        Returns:
            Dict containing all parsed parameters
        """
        all_params = {}
        try:
            all_params.update(self.load_geometry_parameters())
            all_params.update(self.load_material_parameters())
            all_params.update(self.load_solver_parameters())
            all_params.update(self.load_control_parameters())
            
            # Validate all parameters
            self._validate_parameters(all_params)
            
            # Cache results
            self._cache['all_parameters'] = all_params
            self._cache['last_load'] = datetime.now().isoformat()
            
            return all_params
            
        except Exception as e:
            logger.error(f"Failed to load parameters: {e}", exc_info=True)
            raise OpenFOAMParseError(f"Parameter loading failed: {e}")
            
    def load_geometry_parameters(self) -> Dict[str, Any]:
        """Load geometry parameters from blockMeshDict and topoSetDict."""
        params = {}
        try:
            # Load from blockMeshDict
            blockmesh_path = self.project_path / "system" / "blockMeshDict"
            if blockmesh_path.exists():
                params.update(self._parse_blockmesh_dict(blockmesh_path))
                
            # Load from topoSetDict
            topo_path = self.project_path / "system" / "topoSetDict"
            if topo_path.exists():
                params.update(self._parse_topo_set_dict(topo_path))
                
        except Exception as e:
            logger.error(f"Failed to load geometry parameters: {e}", exc_info=True)
            raise OpenFOAMParseError(f"Geometry parameter parsing failed: {e}")
            
        return params
        
    def load_material_parameters(self) -> Dict[str, Any]:
        """Load material parameters from LiProperties."""
        params = {}
        try:
            li_properties_path = self.project_path / "constant" / "LiProperties"
            if li_properties_path.exists():
                params.update(self._parse_li_properties(li_properties_path))
                
        except Exception as e:
            logger.error(f"Failed to load material parameters: {e}", exc_info=True)
            raise OpenFOAMParseError(f"Material parameter parsing failed: {e}")
            
        return params
        
    def load_solver_parameters(self) -> Dict[str, Any]:
        """Load solver parameters from fvSchemes and fvSolution."""
        params = {}
        try:
            # Load from fvSchemes
            fv_schemes_path = self.project_path / "system" / "fvSchemes"
            if fv_schemes_path.exists():
                params.update(self._parse_fv_schemes(fv_schemes_path))
                
            # Load from fvSolution
            fv_solution_path = self.project_path / "system" / "fvSolution"
            if fv_solution_path.exists():
                params.update(self._parse_fv_solution(fv_solution_path))
                
        except Exception as e:
            logger.error(f"Failed to load solver parameters: {e}", exc_info=True)
            raise OpenFOAMParseError(f"Solver parameter parsing failed: {e}")
            
        return params
        
    def load_control_parameters(self) -> Dict[str, Any]:
        """Load control parameters from controlDict."""
        params = {}
        try:
            control_dict_path = self.project_path / "system" / "controlDict"
            if control_dict_path.exists():
                params.update(self._parse_control_dict(control_dict_path))
                
        except Exception as e:
            logger.error(f"Failed to load control parameters: {e}", exc_info=True)
            raise OpenFOAMParseError(f"Control parameter parsing failed: {e}")
            
        return params
        
    def _parse_blockmesh_dict(self, file_path: Path) -> Dict[str, Any]:
        """Parse blockMeshDict for geometry parameters."""
        params = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract vertices for dimensions
            vertices_match = re.search(self.OPENFOAM_PATTERNS['blockMeshDict']['vertices'], content, re.DOTALL)
            if vertices_match:
                vertices_text = vertices_match.group(1)
                # Extract vertex coordinates
                vertex_coords = re.findall(r'\(([-0-9.e\s]+)\)', vertices_text)
                if len(vertex_coords) >= 8:
                    # Get min and max coordinates from vertices
                    coords = []
                    for vertex in vertex_coords[:8]:
                        parts = vertex.strip().split()
                        if len(parts) == 3:
                            coords.append([float(p) for p in parts])
                            
                    if coords:
                        x_coords = [c[0] for c in coords]
                        y_coords = [c[1] for c in coords]
                        z_coords = [c[2] for c in coords]
                        
                        x_min, x_max = min(x_coords), max(x_coords)
                        y_min, y_max = min(y_coords), max(y_coords)
                        z_min, z_max = min(z_coords), max(z_coords)
                        
                        params['length'] = abs(x_max - x_min)
                        params['width'] = abs(y_max - y_min)
                        params['height'] = abs(z_max - z_min)
                        
            # Extract division counts
            blocks_match = re.search(self.OPENFOAM_PATTERNS['blockMeshDict']['blocks'], content, re.DOTALL)
            if blocks_match:
                blocks_text = blocks_match.group(1)
                # Look for simpleGrading pattern
                grading_match = re.search(r'\((\d+)\s+(\d+)\s+(\d+)\)\s+simpleGrading', blocks_text)
                if grading_match:
                    params['x_division'] = int(grading_match.group(1))
                    params['y_division'] = int(grading_match.group(2))
                    params['z_division'] = int(grading_match.group(3))
                    
            # Extract unit conversion
            unit_match = re.search(self.OPENFOAM_PATTERNS['blockMeshDict']['convertToMeters'], content)
            if unit_match:
                unit_value = float(unit_match.group(1))
                if unit_value == 1e-6:
                    params['unit'] = 'micrometer'
                elif unit_value == 1e-3:
                    params['unit'] = 'millimeter'
                elif unit_value == 1e-0:
                    params['unit'] = 'meter'
                    
        except Exception as e:
            logger.error(f"Failed to parse blockMeshDict: {e}", exc_info=True)
            raise
            
        return params
        
    def _parse_topo_set_dict(self, file_path: Path) -> Dict[str, Any]:
        """Parse topoSetDict for radius parameter."""
        params = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract radius
            radius_match = re.search(self.OPENFOAM_PATTERNS['topoSetDict']['radius'], content)
            if radius_match:
                params['radius'] = float(radius_match.group(1))
                
        except Exception as e:
            logger.error(f"Failed to parse topoSetDict: {e}", exc_info=True)
            raise
            
        return params
        
    def _parse_li_properties(self, file_path: Path) -> Dict[str, Any]:
        """Parse LiProperties for material parameters."""
        params = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract properties using pattern
            properties_matches = re.findall(self.OPENFOAM_PATTERNS['LiProperties']['properties'], content)
            for prop_name, prop_value in properties_matches:
                params[prop_name] = float(prop_value)
                
        except Exception as e:
            logger.error(f"Failed to parse LiProperties: {e}", exc_info=True)
            raise
            
        return params
        
    def _parse_fv_schemes(self, file_path: Path) -> Dict[str, Any]:
        """Parse fvSchemes for solver scheme parameters."""
        params = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract scheme selections
            scheme_types = ['ddtSchemes', 'gradSchemes', 'divSchemes', 'laplacianSchemes', 'interpolationSchemes']
            for scheme_type in scheme_types:
                pattern = self.OPENFOAM_PATTERNS['fvSchemes'][scheme_type]
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    scheme_content = match.group(1)
                    # Look for default scheme
                    default_match = re.search(r'default\s+([^;]+)', scheme_content)
                    if default_match:
                        params[scheme_type] = default_match.group(1).strip()
                        
        except Exception as e:
            logger.error(f"Failed to parse fvSchemes: {e}", exc_info=True)
            raise
            
        return params
        
    def _parse_fv_solution(self, file_path: Path) -> Dict[str, Any]:
        """Parse fvSolution for solver tolerance parameters."""
        params = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract tolerance
            tolerance_match = re.search(self.OPENFOAM_PATTERNS['fvSolution']['tolerance'], content)
            if tolerance_match:
                params['tolerance'] = float(tolerance_match.group(1))
                
            # Extract relTol
            rel_tol_match = re.search(self.OPENFOAM_PATTERNS['fvSolution']['relTol'], content)
            if rel_tol_match:
                params['relTol'] = float(rel_tol_match.group(1))
                
        except Exception as e:
            logger.error(f"Failed to parse fvSolution: {e}", exc_info=True)
            raise
            
        return params
        
    def _parse_control_dict(self, file_path: Path) -> Dict[str, Any]:
        """Parse controlDict for simulation control parameters."""
        params = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract control parameters
            control_params = ['endTime', 'deltaT', 'writeInterval', 'writeControl']
            for param in control_params:
                pattern = self.OPENFOAM_PATTERNS['controlDict'][param]
                match = re.search(pattern, content)
                if match:
                    if param in ['endTime', 'deltaT', 'writeInterval']:
                        params[param] = float(match.group(1))
                    else:
                        params[param] = match.group(1)
                        
        except Exception as e:
            logger.error(f"Failed to parse controlDict: {e}", exc_info=True)
            raise
            
        return params
        
    def _validate_parameters(self, params: Dict[str, Any]):
        """Validate parameters against definitions."""
        self._validation_errors = []
        
        for param_name, param_value in params.items():
            if param_name in self.PARAMETER_DEFINITIONS:
                definition = self.PARAMETER_DEFINITIONS[param_name]
                if not definition.validate(param_value):
                    error_msg = f"Invalid value for {param_name}: {param_value}"
                    self._validation_errors.append(error_msg)
                    logger.warning(error_msg)
                    
        if self._validation_errors:
            raise ParameterValidationError(f"Parameter validation failed: {self._validation_errors}")
            
    def save_all_parameters(self, params: Dict[str, Any]):
        """Save all parameters to configuration files."""
        try:
            self.save_geometry_parameters(params)
            self.save_material_parameters(params)
            self.save_solver_parameters(params)
            self.save_control_parameters(params)
            
            # Clear cache since parameters changed
            self._cache.clear()
            
        except Exception as e:
            logger.error(f"Failed to save parameters: {e}", exc_info=True)
            raise
            
    def save_geometry_parameters(self, params: Dict[str, Any]):
        """Save geometry parameters to configuration files."""
        try:
            # Update blockMeshDict
            blockmesh_path = self.project_path / "system" / "blockMeshDict"
            if blockmesh_path.exists():
                self._update_blockmesh_dict(blockmesh_path, params)
                
            # Update topoSetDict
            topo_path = self.project_path / "system" / "topoSetDict"
            if topo_path.exists():
                self._update_topo_set_dict(topo_path, params)
                
        except Exception as e:
            logger.error(f"Failed to save geometry parameters: {e}", exc_info=True)
            raise
            
    def save_material_parameters(self, params: Dict[str, Any]):
        """Save material parameters to LiProperties."""
        try:
            li_properties_path = self.project_path / "constant" / "LiProperties"
            if li_properties_path.exists():
                self._update_li_properties(li_properties_path, params)
                
        except Exception as e:
            logger.error(f"Failed to save material parameters: {e}", exc_info=True)
            raise
            
    def save_solver_parameters(self, params: Dict[str, Any]):
        """Save solver parameters to fvSchemes and fvSolution."""
        try:
            # Update fvSchemes
            fv_schemes_path = self.project_path / "system" / "fvSchemes"
            if fv_schemes_path.exists():
                self._update_fv_schemes(fv_schemes_path, params)
                
            # Update fvSolution
            fv_solution_path = self.project_path / "system" / "fvSolution"
            if fv_solution_path.exists():
                self._update_fv_solution(fv_solution_path, params)
                
        except Exception as e:
            logger.error(f"Failed to save solver parameters: {e}", exc_info=True)
            raise
            
    def save_control_parameters(self, params: Dict[str, Any]):
        """Save control parameters to controlDict."""
        try:
            control_dict_path = self.project_path / "system" / "controlDict"
            if control_dict_path.exists():
                self._update_control_dict(control_dict_path, params)
                
        except Exception as e:
            logger.error(f"Failed to save control parameters: {e}", exc_info=True)
            raise
            
    def _update_blockmesh_dict(self, file_path: Path, params: Dict[str, Any]):
        """Update blockMeshDict with new geometry parameters."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Update dimensions if provided
            if all(k in params for k in ['length', 'width', 'height']):
                length = params['length'] / 2
                width = params['width'] / 2
                height = params['height'] / 2
                
                # Replace vertex coordinates (simplified approach)
                # This would need more sophisticated parsing for complex geometries
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
                    
                    # Replace each vertex (simplified - would need more robust approach)
                    for i, new_vertex in enumerate(new_vertices):
                        if i < len(vertices):
                            old_vertex = vertices[i]
                            old_str = f"({old_vertex[0]} {old_vertex[1]} {old_vertex[2]})"
                            new_str = f"({new_vertex[0]} {new_vertex[1]} {new_vertex[2]})"
                            content = content.replace(old_str, new_str, 1)
                            
            # Update divisions if provided
            if all(k in params for k in ['x_division', 'y_division', 'z_division']):
                old_division = f"({params.get('x_division', 20)} {params.get('y_division', 20)} {params.get('z_division', 20)})"
                new_division = f"({params['x_division']} {params['y_division']} {params['z_division']})"
                content = re.sub(r'\(\d+\s+\d+\s+\d+\)\s+simpleGrading', new_division + ' simpleGrading', content)
                
            # Update unit if provided
            if 'unit' in params:
                unit_value = {'micrometer': '1e-6', 'millimeter': '1e-3', 'meter': '1e-0'}[params['unit']]
                content = re.sub(r'convertToMeters\s+[0-9.e-]+', f'convertToMeters {unit_value}', content)
                
            with open(file_path, 'w') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Failed to update blockMeshDict: {e}", exc_info=True)
            raise
            
    def _update_topo_set_dict(self, file_path: Path, params: Dict[str, Any]):
        """Update topoSetDict with new radius parameter."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Update radius if provided
            if 'radius' in params:
                content = re.sub(r'radius\s+[0-9.e-]+', f'radius {params["radius"]}', content)
                
            with open(file_path, 'w') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Failed to update topoSetDict: {e}", exc_info=True)
            raise
            
    def _update_li_properties(self, file_path: Path, params: Dict[str, Any]):
        """Update LiProperties with new material parameters."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Update material properties
            material_params = ['DS_value', 'CS_max', 'kReact', 'R', 'F', 'Ce', 'alphaA', 'alphaC', 'T_temp', 'I_app']
            for param in material_params:
                if param in params:
                    pattern = rf'{param}\s+\[.*?\]\s+[0-9.e-]+'
                    content = re.sub(pattern, f'{param} [0 0 0 0 0 0 0] {params[param]}', content)
                    
            with open(file_path, 'w') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Failed to update LiProperties: {e}", exc_info=True)
            raise
            
    def _update_fv_schemes(self, file_path: Path, params: Dict[str, Any]):
        """Update fvSchemes with new solver scheme parameters."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Update scheme selections
            scheme_types = ['ddtSchemes', 'gradSchemes', 'divSchemes', 'laplacianSchemes', 'interpolationSchemes']
            for scheme_type in scheme_types:
                if scheme_type in params:
                    pattern = rf'{scheme_type}\s*\{{[^}}]*default\s+[^;]+}}'
                    replacement = f'{scheme_type}\n{{\n    default         {params[scheme_type]};\n}}'
                    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                    
            with open(file_path, 'w') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Failed to update fvSchemes: {e}", exc_info=True)
            raise
            
    def _update_fv_solution(self, file_path: Path, params: Dict[str, Any]):
        """Update fvSolution with new solver tolerance parameters."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Update tolerance if provided
            if 'tolerance' in params:
                content = re.sub(r'tolerance\s+[0-9.e-]+', f'tolerance {params["tolerance"]}', content)
                
            # Update relTol if provided
            if 'relTol' in params:
                content = re.sub(r'relTol\s+[0-9.e-]+', f'relTol {params["relTol"]}', content)
                
            with open(file_path, 'w') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Failed to update fvSolution: {e}", exc_info=True)
            raise
            
    def _update_control_dict(self, file_path: Path, params: Dict[str, Any]):
        """Update controlDict with new control parameters."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Update control parameters
            control_params = ['endTime', 'deltaT', 'writeInterval']
            for param in control_params:
                if param in params:
                    content = re.sub(rf'{param}\s+[0-9.e-]+', f'{param} {params[param]}', content)
                    
            # Update writeControl if provided
            if 'writeControl' in params:
                content = re.sub(r'writeControl\s+\w+', f'writeControl {params["writeControl"]}', content)
                
            with open(file_path, 'w') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Failed to update controlDict: {e}", exc_info=True)
            raise
            
    def get_parameter_definitions(self, category: Optional[str] = None) -> Dict[str, ParameterDefinition]:
        """Get parameter definitions, optionally filtered by category."""
        if category:
            return {k: v for k, v in self.PARAMETER_DEFINITIONS.items() if v.category == category}
        return self.PARAMETER_DEFINITIONS.copy()
        
    def validate_parameter(self, param_name: str, value: Any) -> bool:
        """Validate a single parameter value."""
        if param_name not in self.PARAMETER_DEFINITIONS:
            return False
            
        definition = self.PARAMETER_DEFINITIONS[param_name]
        return definition.validate(value)
        
    def get_parameter_suggestions(self, param_name: str) -> List[Any]:
        """Get suggestions for a parameter (allowed values or common values)."""
        if param_name not in self.PARAMETER_DEFINITIONS:
            return []
            
        definition = self.PARAMETER_DEFINITIONS[param_name]
        if definition.allowed_values:
            return definition.allowed_values
            
        # Return common values based on parameter type and range
        if definition.type == 'int' or definition.type == 'float':
            if definition.min_value is not None and definition.max_value is not None:
                return [
                    definition.min_value,
                    (definition.min_value + definition.max_value) / 2,
                    definition.max_value
                ]
                
        return []
        
    def get_parameter_info(self, param_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a parameter."""
        if param_name not in self.PARAMETER_DEFINITIONS:
            return None
            
        definition = self.PARAMETER_DEFINITIONS[param_name]
        return {
            'name': definition.name,
            'type': definition.type,
            'description': definition.description,
            'default_value': definition.default_value,
            'min_value': definition.min_value,
            'max_value': definition.max_value,
            'allowed_values': definition.allowed_values,
            'required': definition.required,
            'pattern': definition.pattern,
            'units': definition.units,
            'category': definition.category
        }
