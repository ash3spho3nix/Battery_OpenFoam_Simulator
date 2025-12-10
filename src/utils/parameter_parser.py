"""
Parameter parser for OpenFOAM configuration files.

This module provides utilities for parsing and modifying OpenFOAM
configuration files like blockMeshDict, topoSetDict, LiProperties,
fvSchemes, fvSolution, and controlDict.
"""

import re
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging

logger = logging.getLogger(__name__)


class ParameterManager:
    """
    Manager for OpenFOAM parameter files.
    
    Handles parsing, modification, and validation of OpenFOAM
    configuration files.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the parameter manager.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path)
        self.parameters = {}
        
    def load_parameters(self, case_name: str = "Case") -> bool:
        """
        Load parameters from OpenFOAM configuration files.
        
        Args:
            case_name: Name of the case directory
            
        Returns:
            bool: True if successful
        """
        case_path = self.project_path / case_name
        
        if not case_path.exists():
            logger.error(f"Case directory does not exist: {case_path}")
            return False
            
        # Load different parameter files
        success = True
        
        success &= self._load_block_mesh_dict(case_path)
        success &= self._load_topo_set_dict(case_path)
        success &= self._load_li_properties(case_path)
        success &= self._load_fv_schemes(case_path)
        success &= self._load_fv_solution(case_path)
        success &= self._load_control_dict(case_path)
        
        if success:
            logger.debug("Successfully loaded all parameter files")
        else:
            logger.error("Failed to load some parameter files")
            
        return success
        
    def save_parameters(self, case_name: str = "Case") -> bool:
        """
        Save parameters to OpenFOAM configuration files.
        
        Args:
            case_name: Name of the case directory
            
        Returns:
            bool: True if successful
        """
        case_path = self.project_path / case_name
        
        # Ensure case directory exists
        case_path.mkdir(parents=True, exist_ok=True)
        
        # Save different parameter files
        success = True
        
        success &= self._save_block_mesh_dict(case_path)
        success &= self._save_topo_set_dict(case_path)
        success &= self._save_li_properties(case_path)
        success &= self._save_fv_schemes(case_path)
        success &= self._save_fv_solution(case_path)
        success &= self._save_control_dict(case_path)
        
        if success:
            logger.debug("Successfully saved all parameter files")
        else:
            logger.error("Failed to save some parameter files")
            
        return success
        
    def get_parameter(self, file_type: str, parameter_name: str) -> Optional[Any]:
        """
        Get a parameter value.
        
        Args:
            file_type: Type of parameter file
            parameter_name: Name of the parameter
            
        Returns:
            Parameter value or None if not found
        """
        key = f"{file_type}.{parameter_name}"
        return self.parameters.get(key)
        
    def set_parameter(self, file_type: str, parameter_name: str, value: Any):
        """
        Set a parameter value.
        
        Args:
            file_type: Type of parameter file
            parameter_name: Name of the parameter
            value: Parameter value
        """
        key = f"{file_type}.{parameter_name}"
        self.parameters[key] = value
        
    def get_all_parameters(self) -> Dict[str, Any]:
        """
        Get all parameters.
        
        Returns:
            Dict[str, Any]: All parameters
        """
        return self.parameters.copy()
        
    def _load_block_mesh_dict(self, case_path: Path) -> bool:
        """Load blockMeshDict parameters."""
        file_path = case_path / "system" / "blockMeshDict"
        
        if not file_path.exists():
            logger.warning(f"blockMeshDict not found: {file_path}")
            return False
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Extract vertices
            vertices_match = re.search(r'vertices\s*\((.*?)\);', content, re.DOTALL)
            if vertices_match:
                vertices_text = vertices_match.group(1)
                vertices = self._parse_vertices(vertices_text)
                self.parameters['blockMeshDict.vertices'] = vertices
                
            # Extract blocks
            blocks_match = re.search(r'blocks\s*\((.*?)\);', content, re.DOTALL)
            if blocks_match:
                blocks_text = blocks_match.group(1)
                blocks = self._parse_blocks(blocks_text)
                self.parameters['blockMeshDict.blocks'] = blocks
                
            logger.debug("Loaded blockMeshDict parameters")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load blockMeshDict: {e}")
            return False
            
    def _save_block_mesh_dict(self, case_path: Path) -> bool:
        """Save blockMeshDict parameters."""
        file_path = case_path / "system" / "blockMeshDict"
        
        try:
            # Generate content
            content = self._generate_block_mesh_dict()
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w') as f:
                f.write(content)
                
            logger.debug("Saved blockMeshDict parameters")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save blockMeshDict: {e}")
            return False
            
    def _load_li_properties(self, case_path: Path) -> bool:
        """Load LiProperties parameters."""
        file_path = case_path / "constant" / "LiProperties"
        
        if not file_path.exists():
            logger.warning(f"LiProperties not found: {file_path}")
            return False
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Extract properties
            properties = {}
            
            # DS value
            ds_match = re.search(r'DS\s*\[.*?\]\s*([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)', content)
            if ds_match:
                properties['DS'] = float(ds_match.group(1))
                
            # CS_max value
            cs_max_match = re.search(r'CS_max\s*\[.*?\]\s*([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)', content)
            if cs_max_match:
                properties['CS_max'] = float(cs_max_match.group(1))
                
            # kReact value
            kreact_match = re.search(r'kReact\s*\[.*?\]\s*([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)', content)
            if kreact_match:
                properties['kReact'] = float(kreact_match.group(1))
                
            # Store properties
            self.parameters['LiProperties'] = properties
            
            logger.debug("Loaded LiProperties parameters")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load LiProperties: {e}")
            return False
            
    def _save_li_properties(self, case_path: Path) -> bool:
        """Save LiProperties parameters."""
        file_path = case_path / "constant" / "LiProperties"
        
        try:
            # Generate content
            content = self._generate_li_properties()
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w') as f:
                f.write(content)
                
            logger.debug("Saved LiProperties parameters")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save LiProperties: {e}")
            return False
            
    def _load_control_dict(self, case_path: Path) -> bool:
        """Load controlDict parameters."""
        file_path = case_path / "system" / "controlDict"
        
        if not file_path.exists():
            logger.warning(f"controlDict not found: {file_path}")
            return False
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Extract parameters
            parameters = {}
            
            # endTime
            end_time_match = re.search(r'endTime\s+([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)', content)
            if end_time_match:
                parameters['endTime'] = float(end_time_match.group(1))
                
            # deltaT
            delta_t_match = re.search(r'deltaT\s+([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)', content)
            if delta_t_match:
                parameters['deltaT'] = float(delta_t_match.group(1))
                
            # writeInterval
            write_interval_match = re.search(r'writeInterval\s+([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)', content)
            if write_interval_match:
                parameters['writeInterval'] = float(write_interval_match.group(1))
                
            # Store parameters
            self.parameters['controlDict'] = parameters
            
            logger.debug("Loaded controlDict parameters")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load controlDict: {e}")
            return False
            
    def _save_control_dict(self, case_path: Path) -> bool:
        """Save controlDict parameters."""
        file_path = case_path / "system" / "controlDict"
        
        try:
            # Generate content
            content = self._generate_control_dict()
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w') as f:
                f.write(content)
                
            logger.debug("Saved controlDict parameters")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save controlDict: {e}")
            return False
            
    def _parse_vertices(self, vertices_text: str) -> List[List[float]]:
        """Parse vertices from blockMeshDict."""
        vertices = []
        
        # Find all vertex definitions
        vertex_pattern = r'\(([-+]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s+([-+]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s+([-+]?\d*\.?\d+(?:[eE][+-]?\d+)?)\)'
        
        matches = re.findall(vertex_pattern, vertices_text)
        for match in matches:
            vertex = [float(coord) for coord in match]
            vertices.append(vertex)
            
        return vertices
        
    def _parse_blocks(self, blocks_text: str) -> Dict:
        """Parse blocks from blockMeshDict."""
        # Extract hex block definition
        hex_match = re.search(r'hex\s*\((.*?)\)\s*\((\d+)\s+(\d+)\s+(\d+)\)', blocks_text)
        
        if hex_match:
            vertices = hex_match.group(1).strip()
            x_div = int(hex_match.group(2))
            y_div = int(hex_match.group(3))
            z_div = int(hex_match.group(4))
            
            return {
                'vertices': vertices,
                'divisions': (x_div, y_div, z_div),
                'grading': 'simpleGrading (1 1 1)'
            }
            
        return {}
        
    def _generate_block_mesh_dict(self) -> str:
        """Generate blockMeshDict content."""
        vertices = self.parameters.get('blockMeshDict.vertices', [
            [0, 0, 0],
            [100, 0, 0],
            [100, 100, 0],
            [0, 100, 0],
            [0, 0, 100],
            [100, 0, 100],
            [100, 100, 100],
            [0, 100, 100]
        ])
        
        blocks = self.parameters.get('blockMeshDict.blocks', {
            'vertices': '0 1 2 3 4 5 6 7',
            'divisions': (20, 20, 20),
            'grading': 'simpleGrading (1 1 1)'
        })
        
        content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
=========                 |
\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
 \\    /   O peration     | Website:  https://openfoam.org
  \\  /    A nd           | Version:  6
   \\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1e-6;

vertices
(
    ({vertices[0][0]} {vertices[0][1]} {vertices[0][2]})
    ({vertices[1][0]} {vertices[1][1]} {vertices[1][2]})
    ({vertices[2][0]} {vertices[2][1]} {vertices[2][2]})
    ({vertices[3][0]} {vertices[3][1]} {vertices[3][2]})
    ({vertices[4][0]} {vertices[4][1]} {vertices[4][2]})
    ({vertices[5][0]} {vertices[5][1]} {vertices[5][2]})
    ({vertices[6][0]} {vertices[6][1]} {vertices[6][2]})
    ({vertices[7][0]} {vertices[7][1]} {vertices[7][2]})
);

blocks
(
    hex ({blocks['vertices']}) ({blocks['divisions'][0]} {blocks['divisions'][1]} {blocks['divisions'][2]}) {blocks['grading']}
);

edges
(
);

boundary
(
    inlet
    {{
        type patch;
        faces
        (
            (0 4 7 3)
            (4 5 6 7)
            (0 1 5 4)
            (1 2 6 5)
            (2 3 7 6)
        );
    }}
    outlet
    {{
        type patch;
        faces
        (
            (0 3 2 1)
        );
    }}
    walls
    {{
        type wall;
        faces
        (
            (0 1 2 3)
        );
    }}
);

mergePatchPairs
(
);

// ************************************************************************* //
"""
        return content
        
    def _generate_li_properties(self) -> str:
        """Generate LiProperties content."""
        properties = self.parameters.get('LiProperties', {
            'DS': 1e-14,
            'CS_max': 30000,
            'kReact': 1e-11,
            'R': 8.314,
            'F': 96485,
            'Ce': 1000,
            'alphaA': 0.5,
            'alphaC': 0.5,
            'T_temp': 298.15,
            'I_app': 0.0
        })
        
        content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
=========                 |
\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
 \\    /   O peration     | Website:  https://openfoam.org
  \\  /    A nd           | Version:  6
   \\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      LiProperties;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

LiProperties
{{
    DS          [0 2 -1 0 0 0 0] {properties['DS']};
    CS_max      [0 0 -3 0 0 0 0] {properties['CS_max']};
    kReact      [0 0 0 0 0 0 0] {properties['kReact']};
    R           [0 2 -2 -1 0 0 0] {properties['R']};
    F           [0 0 1 0 0 0 0] {properties['F']};
    Ce          [0 0 -3 0 0 0 0] {properties['Ce']};
    alphaA      [0 0 0 0 0 0 0] {properties['alphaA']};
    alphaC      [0 0 0 0 0 0 0] {properties['alphaC']};
    T_temp      [0 0 0 1 0 0 0] {properties['T_temp']};
    I_app       [0 0 0 0 0 0 0] {properties['I_app']};
}}

// ************************************************************************* //
"""
        return content
        
    def _generate_control_dict(self) -> str:
        """Generate controlDict content."""
        parameters = self.parameters.get('controlDict', {
            'endTime': 10.0,
            'deltaT': 0.1,
            'writeInterval': 1.0
        })
        
        content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
=========                 |
\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
 \\    /   O peration     | Website:  https://openfoam.org
  \\  /    A nd           | Version:  6
   \\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     SPMFoam_OF6;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         {parameters['endTime']};

deltaT          {parameters['deltaT']};

writeControl    time;

writeInterval   {parameters['writeInterval']};

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

functions
{{
    probes
    {{
        type            probes;
        functionObjectLibs ("libsampling.so");
        outputControl   time;
        outputInterval  1;
        probeLocations
        (
            (0 0 0)
        );
        fields
        (
            cs
        );
    }}
}}

// ************************************************************************* //
"""
        return content
        
    def validate_parameters(self) -> List[str]:
        """
        Validate all parameters.
        
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate blockMeshDict parameters
        vertices = self.parameters.get('blockMeshDict.vertices', [])
        if len(vertices) != 8:
            errors.append("blockMeshDict: Invalid number of vertices")
            
        # Validate LiProperties parameters
        li_props = self.parameters.get('LiProperties', {})
        required_li_props = ['DS', 'CS_max', 'kReact']
        for prop in required_li_props:
            if prop not in li_props:
                errors.append(f"LiProperties: Missing {prop}")
            elif li_props[prop] <= 0:
                errors.append(f"LiProperties: {prop} must be positive")
                
        # Validate controlDict parameters
        control_dict = self.parameters.get('controlDict', {})
        required_control = ['endTime', 'deltaT', 'writeInterval']
        for param in required_control:
            if param not in control_dict:
                errors.append(f"controlDict: Missing {param}")
            elif control_dict[param] <= 0:
                errors.append(f"controlDict: {param} must be positive")
                
        return errors
