"""
PHASE 1 — EXECUTION TEST (ISOLATED)
Test OpenFOAM execution via MSYS2Executor using OPENFOAM-MSYS2.bat

This test verifies that OpenFOAM can be executed from Python using the MSYS2Executor
class, which launches OPENFOAM-MSYS2.bat as a subprocess.

Test Requirements:
- Launch OPENFOAM-MSYS2.bat as subprocess via msys2_executor
- Execute simple OpenFOAM command in its environment
- Use existing or minimal valid case directory
- Verify process starts, environment initializes, command found/invoked
- Process exits with valid return code
- Capture stdout, stderr, exit code
- GUI-independent test
"""

import os
import subprocess
import tempfile
import shutil
import logging
from pathlib import Path
from src.core.project_manager import ProjectManager
from src.openfoam.msys2_executor import MSYS2Executor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_minimal_test_case():
    """Create a minimal valid OpenFOAM case for testing."""
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Created temp directory: {temp_dir}")

    try:
        # Create project using existing ProjectManager
        pm = ProjectManager(temp_dir)
        project_name = 'openfoam_test_case'
        success = pm.create_project(project_name, 'SPM')
        logger.info(f"Project creation: {'SUCCESS' if success else 'FAILED'}")

        if not success:
            raise Exception("Failed to create test project")

        project_path = Path(temp_dir) / project_name
        case_path = project_path / 'SPMFoam' / 'Case'

        if not case_path.exists():
            raise Exception(f"Case directory not found: {case_path}")

        logger.info(f"Test case created at: {case_path}")
        return temp_dir, str(case_path)

    except Exception as e:
        # Cleanup on failure
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise e

def test_openfoam_execution():
    """Test OpenFOAM execution via MSYS2Executor."""

    logger.info("=== PHASE 1: OpenFOAM Execution Test (Isolated) ===")

    temp_dir = None
    case_path = None

    try:
        # Step 1: Create minimal test case
        logger.info("Step 1: Creating minimal test case...")
        temp_dir, case_path = create_minimal_test_case()

        # Step 2: Initialize MSYS2Executor with correct OpenFOAM-MSYS2.bat path
        logger.info("Step 2: Initializing MSYS2Executor...")
        openfoam_bat_path = r'C:\Users\vsharma.A123SYSTEMSEU\Documents\OpenFoam\v2312\OpenFOAM-MSYS2.bat'
        executor = MSYS2Executor(openfoam_bat_path)

        # Step 3: Test basic OpenFOAM command execution
        logger.info("Step 3: Testing OpenFOAM command execution...")

        # Test a simple command first - just check if environment loads
        logger.info("Testing basic environment...")
        return_code, stdout, stderr = executor.execute_command('echo "OpenFOAM environment test"', case_path, timeout=30)

        logger.info(f"Return code: {return_code}")
        logger.info(f"STDOUT: {stdout}")
        logger.info(f"STDERR: {stderr}")

        # Step 4: Test actual OpenFOAM command
        if return_code == 0:
            logger.info("Basic environment test passed, testing blockMesh...")

            return_code, stdout, stderr = executor.execute_command('blockMesh', case_path, timeout=60)

            logger.info(f"blockMesh Return code: {return_code}")
            logger.info(f"blockMesh STDOUT: {stdout}")
            logger.info(f"blockMesh STDERR: {stderr}")

            # Check if mesh files were created (actual success indicator)
            constant_mesh = Path(case_path) / 'constant' / 'polyMesh'
            if constant_mesh.exists():
                mesh_files = list(constant_mesh.glob('*'))
                logger.info(f"✅ Mesh created successfully: {len(mesh_files)} files")

                # Test topoSet as well
                logger.info("Testing topoSet...")
                return_code2, stdout2, stderr2 = executor.execute_command('topoSet -dict system/topoSetDict', case_path, timeout=60)
                logger.info(f"topoSet Return code: {return_code2}")

                # Check if cell zones were created
                cell_zones = constant_mesh / 'cellZones'
                if cell_zones.exists():
                    logger.info("✅ Cell zones created successfully")
                    return True
                else:
                    logger.error("❌ Cell zones not created")
                    return False
            else:
                logger.error("❌ Mesh files not created")
                return False
        else:
            logger.error("❌ Basic environment test failed")
            return False

    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out: {e}")
        return False
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        return False
    finally:
        # Cleanup
        if temp_dir and os.path.exists(temp_dir):
            logger.info(f"Cleaning up temp directory: {temp_dir}")
            shutil.rmtree(temp_dir)

def main():
    """Main test execution."""
    logger.info("Starting OpenFOAM execution test via MSYS2Executor")

    success = test_openfoam_execution()

    if success:
        logger.info("✅ PHASE 1 TEST PASSED: OpenFOAM execution confirmed working")
        return 0
    else:
        logger.error("❌ PHASE 1 TEST FAILED: OpenFOAM execution issues detected")
        return 1

if __name__ == "__main__":
    exit(main())