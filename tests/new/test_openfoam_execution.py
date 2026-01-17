import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from src.core.project_manager import ProjectManager

print('Testing OpenFOAM execution with generated project files (Direct Bash Approach)...')

# MSYS2 bash path - direct executable approach
bash_path = 'C:\\Users\\vsharma.A123SYSTEMSEU\\Documents\\OpenFoam\\v2312\\msys64\\usr\\bin\\bash.exe'

# Create temporary directory for project
temp_dir = tempfile.mkdtemp()
print(f'Created temp dir: {temp_dir}')

try:
    # Create project
    pm = ProjectManager(temp_dir)
    project_name = 'openfoam_test_run'
    success = pm.create_project(project_name, 'SPM')
    print(f'Project creation: {"SUCCESS" if success else "FAILED"}')

    if not success:
        exit(1)

    project_path = Path(temp_dir) / project_name
    case_path = project_path / 'SPMFoam' / 'Case'
    print(f'Case path: {case_path}')

    # Convert Windows path to MSYS2 path for reference (not used by executor)
    msys2_case_path = str(case_path).replace('C:\\', '/c/').replace('\\', '/')
    print(f'MSYS2 case path: {msys2_case_path}')

    # Test OpenFOAM environment setup with direct bash
    print('\nTesting OpenFOAM environment...')
    # Skip environment sourcing for now - test if commands work directly
    print('Skipping environment sourcing - testing direct command execution...')
    env_cmd = f'echo "Testing basic bash functionality" && pwd'
    result = subprocess.run([bash_path, '-c', env_cmd],
                          capture_output=True, text=True, timeout=30)
    print(f'Basic test return code: {result.returncode}')
    print(f'stdout: {result.stdout}')
    if result.stderr:
        print(f'stderr: {result.stderr}')

    if result.returncode != 0:
        print('Failed basic bash test')
        exit(1)

    print('\nTesting blockMesh...')
    blockmesh_cmd = f'cd "{msys2_case_path}" && blockMesh'
    result = subprocess.run([bash_path, '-c', blockmesh_cmd],
                          capture_output=True, text=True, timeout=60)
    print(f'blockMesh return code: {result.returncode}')
    print(f'stdout: {result.stdout}')
    if result.stderr:
        print(f'stderr: {result.stderr}')

    # Check if mesh was created
    constant_mesh = case_path / 'constant' / 'polyMesh'
    if constant_mesh.exists():
        print('✅ Mesh files created successfully')
        mesh_files = list(constant_mesh.glob('*'))
        print(f'Created {len(mesh_files)} mesh files: {[f.name for f in mesh_files]}')
    else:
        print('❌ Mesh files not created')

    # Test topoSet if mesh was created
    if constant_mesh.exists():
        print('\nTesting topoSet...')
        toposet_cmd = f'cd "{msys2_case_path}" && topoSet -dict system/topoSetDict'
        result = subprocess.run([bash_path, '-c', toposet_cmd],
                              capture_output=True, text=True, timeout=60)
        print(f'topoSet return code: {result.returncode}')
        print(f'stdout: {result.stdout}')
        if result.stderr:
            print(f'stderr: {result.stderr}')

        # Check if cell zones were created
        cell_zones = constant_mesh / 'cellZones'
        if cell_zones.exists():
            print('✅ Cell zones created successfully')
        else:
            print('❌ Cell zones not created')

    # Test splitMeshRegions if topoSet worked
    if constant_mesh.exists() and (constant_mesh / 'cellZones').exists():
        print('\nTesting splitMeshRegions...')
        split_cmd = f'cd "{msys2_case_path}" && splitMeshRegions -cellZones -overwrite'
        result = subprocess.run([bash_path, '-c', split_cmd],
                              capture_output=True, text=True, timeout=120)
        print(f'splitMeshRegions return code: {result.returncode}')
        print(f'stdout: {result.stdout}')
        if result.stderr:
            print(f'stderr: {result.stderr}')

        # Check if regions were created
        ele_region = case_path / 'constant' / 'ele'
        solid_region = case_path / 'constant' / 'solidPhase'
        if ele_region.exists() and solid_region.exists():
            print('✅ Mesh regions split successfully')
            print(f'Created regions: ele, solidPhase')
        else:
            print('❌ Mesh regions not split properly')

finally:
    # Clean up
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)