import tempfile
import os
from pathlib import Path
from src.core.project_manager import ProjectManager

print('Testing OpenFOAM project file sufficiency...')

# Create temporary directory for project
temp_dir = tempfile.mkdtemp()
try:
    # Create project
    pm = ProjectManager(temp_dir)
    project_name = 'test_openfoam_project'
    success = pm.create_project(project_name, 'SPM')
    print('Project creation: SUCCESS' if success else 'Project creation: FAILED')

    if not success:
        exit(1)

    project_path = Path(temp_dir) / project_name
    case_path = project_path / 'SPMFoam' / 'Case'

    # Check that case directory exists
    if not case_path.exists():
        print(f'Case directory not found: {case_path}')
        exit(1)
    print(f'Case directory found: {case_path}')

    # Check required OpenFOAM directories
    required_dirs = ['system', 'constant', '0']
    for dir_name in required_dirs:
        dir_path = case_path / dir_name
        if not dir_path.exists():
            print(f'Required directory {dir_name} not found')
            exit(1)
        if not dir_path.is_dir():
            print(f'{dir_name} is not a directory')
            exit(1)
    print('All required directories present')

    # Check required system files
    system_files = [
        'controlDict', 'fvSchemes', 'fvSolution', 'blockMeshDict',
        'topoSetDict', 'setFieldsDict', 'decomposeParDict'
    ]
    for file_name in system_files:
        file_path = case_path / 'system' / file_name
        if not file_path.exists():
            print(f'Required system file {file_name} not found')
            exit(1)
        if not file_path.is_file():
            print(f'{file_name} is not a file')
            exit(1)
    print('All required system files present')

    # Check controlDict content
    control_dict_path = case_path / 'system' / 'controlDict'
    with open(control_dict_path, 'r') as f:
        content = f.read()
        checks = [
            ('application', 'controlDict missing application'),
            ('chtMultiRegionFoam', 'controlDict should use chtMultiRegionFoam'),
            ('startTime', 'controlDict missing startTime'),
            ('endTime', 'controlDict missing endTime'),
            ('deltaT', 'controlDict missing deltaT')
        ]
        for check, error in checks:
            if check not in content:
                print(f'{error}')
                exit(1)
    print('controlDict validation passed')

    # Check fvSchemes content
    fv_schemes_path = case_path / 'system' / 'fvSchemes'
    with open(fv_schemes_path, 'r') as f:
        content = f.read()
        checks = [
            ('ddtSchemes', 'fvSchemes missing ddtSchemes'),
            ('gradSchemes', 'fvSchemes missing gradSchemes'),
            ('divSchemes', 'fvSchemes missing divSchemes'),
            ('laplacianSchemes', 'fvSchemes missing laplacianSchemes')
        ]
        for check, error in checks:
            if check not in content:
                print(f'{error}')
                exit(1)
    print('fvSchemes validation passed')

    # Check fvSolution content
    fv_solution_path = case_path / 'system' / 'fvSolution'
    with open(fv_solution_path, 'r') as f:
        content = f.read()
        if 'solvers' not in content:
            print('fvSolution missing solvers')
            exit(1)
        if 'PIMPLE' not in content:
            print('fvSolution missing PIMPLE settings')
            exit(1)
    print('fvSolution validation passed')

    # Check blockMeshDict content
    block_mesh_path = case_path / 'system' / 'blockMeshDict'
    with open(block_mesh_path, 'r') as f:
        content = f.read()
        checks = [
            ('vertices', 'blockMeshDict missing vertices'),
            ('blocks', 'blockMeshDict missing blocks'),
            ('boundary', 'blockMeshDict missing boundary')
        ]
        for check, error in checks:
            if check not in content:
                print(f'{error}')
                exit(1)
    print('blockMeshDict validation passed')

    # Check constant directory structure
    constant_path = case_path / 'constant'
    if not (constant_path / 'regionProperties').exists():
        print('regionProperties not found')
        exit(1)
    if not (constant_path / 'polyMesh').exists():
        print('Main polyMesh not found')
        exit(1)

    # Check that region directories exist
    if not (constant_path / 'ele').exists():
        print('ele region not found')
        exit(1)
    if not (constant_path / 'solidPhase').exists():
        print('solidPhase region not found')
        exit(1)
    print('Constant directory structure validated')

    # Check initial conditions in 0 directory
    zero_path = case_path / '0'
    if not (zero_path / 'ele').exists():
        print('ele initial conditions not found')
        exit(1)
    if not (zero_path / 'solidPhase').exists():
        print('solidPhase initial conditions not found')
        exit(1)
    print('Initial conditions validated')

    # Check Allrun and Allclean scripts
    allrun_path = case_path / 'Allrun'
    allclean_path = case_path / 'Allclean'
    if not allrun_path.exists():
        print('Allrun script not found')
        exit(1)
    if not allclean_path.exists():
        print('Allclean script not found')
        exit(1)

    # Check Allrun content
    with open(allrun_path, 'r') as f:
        content = f.read()
        checks = [
            ('blockMesh', 'Allrun should run blockMesh'),
            ('topoSet', 'Allrun should run topoSet'),
            ('splitMeshRegions', 'Allrun should run splitMeshRegions')
        ]
        for check, error in checks:
            if check not in content:
                print(f'{error}')
                exit(1)
    print('Allrun script validated')

    print(f'OpenFOAM project validation PASSED for: {project_path}')
    print('The generated project files are sufficient for running OpenFOAM simulations!')

finally:
    # Clean up
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)