"""
Pytest configuration and shared fixtures for Battery Simulator tests.

This module provides:
- Shared fixtures for all test modules
- Test configuration
- Mock utilities
- Test data generation
- Cleanup utilities
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys
from typing import Generator, Dict, Any

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import PyQt6 and create application instance for all tests
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtTest import QTest
    
    # Create a single QApplication instance for all tests
    qt_app = QApplication.instance()
    if qt_app is None:
        qt_app = QApplication([])
        qt_app.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi, True)
    
    HAS_QT = True
except ImportError:
    HAS_QT = False
    qt_app = None


# Test data and fixtures
@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp(prefix="battery_sim_test_")
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_ui_content() -> str:
    """Sample UI file content for testing."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>TestWidget</class>
 <widget class="QWidget" name="TestWidget">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>400</width>
    <height>300</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Test Widget</string>
  </property>
  <widget class="QPushButton" name="testButton">
   <property name="geometry">
    <rect>
     <x>10</x>
     <y>10</y>
     <width>80</width>
     <height>25</height>
    </rect>
   </property>
   <property name="text">
    <string>Test Button</string>
   </property>
  </widget>
  <widget class="QLineEdit" name="testLineEdit">
   <property name="geometry">
    <rect>
     <x>10</x>
     <y>50</y>
     <width>200</width>
     <height>25</height>
    </rect>
   </property>
  </widget>
 </widget>
</ui>'''


@pytest.fixture
def sample_parameter_files() -> Dict[str, str]:
    """Sample OpenFOAM parameter files for testing."""
    return {
        'blockMeshDict': '''/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  6                                     |
|   \  /    A nd           | Web:      www.OpenFOAM.org                        |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1e-6;

vertices
(
    (0 0 0)
    (200 0 0)
    (200 200 0)
    (0 200 0)
    (0 0 200)
    (200 0 200)
    (200 200 200)
    (0 200 200)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 20) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    inlet
    {
        type patch;
        faces
        (
            (0 4 7 3)
        );
    }
    outlet
    {
        type patch;
        faces
        (
            (1 2 6 5)
        );
    }
    walls
    {
        type wall;
        faces
        (
            (0 1 5 4)
            (2 3 7 6)
            (0 3 2 1)
            (4 5 6 7)
        );
    }
);

mergePatchPairs
(
);

// ************************************************************************* //
''',
        
        'topoSetDict': '''/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  6                                     |
|   \  /    A nd           | Web:      www.OpenFOAM.org                        |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

actions
(
    {
        name    cellSet;
        type    cellSet;
        action  new;
        source  boxToCell;
        sourceInfo
        {
            box (0 0 0) (100 100 100);
        }
    }
);

// ************************************************************************* //
''',
        
        'LiProperties': '''/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  6                                     |
|   \  /    A nd           | Web:      www.OpenFOAM.org                        |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      LiProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

Li
{
    DS              [0 2 -1 0 0 0 0]     1e-14;
    CS_max          [0 0 -3 0 0 0 0]    30000;
    kReact          [0 3 1 -1 0 0 0]    1e-11;
    OCV_Gr.H
    {
        value           table
        (
            (0.0 1.0)
            (0.5 0.5)
            (1.0 0.0)
        );
    }
    OCV_Si.H
    {
        value           table
        (
            (0.0 1.0)
            (0.5 0.5)
            (1.0 0.0)
        );
    }
}

// ************************************************************************* //
''',
        
        'fvSchemes': '''/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  6                                     |
|   \  /    A nd           | Web:      www.OpenFOAM.org                        |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,cs)     bounded Gauss upwind;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

fluxRequired
{
    default         no;
    p_rgh;
    pcorr;
}

// ************************************************************************* //
''',
        
        'fvSolution': '''/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  6                                     |
|   \  /    A nd           | Web:      www.OpenFOAM.org                        |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    cs
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0.1;
    }
}

PISO
{
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}

// ************************************************************************* //
''',
        
        'controlDict': '''/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  6                                     |
|   \  /    A nd           | Web:      www.OpenFOAM.org                        |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     SPMFoam_OF6;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         10;

deltaT          0.1;

writeControl    timeStep;

writeInterval   10;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

// ************************************************************************* //
'''}


@pytest.fixture
def mock_openfoam_environment(temp_dir) -> Dict[str, str]:
    """Mock OpenFOAM environment variables."""
    env_vars = {
        'WM_PROJECT_DIR': temp_dir,
        'FOAM_APP': temp_dir + '/applications',
        'FOAM_RUN': temp_dir + '/run',
        'PATH': temp_dir + '/bin:' + os.environ.get('PATH', ''),
        'LD_LIBRARY_PATH': temp_dir + '/lib:' + os.environ.get('LD_LIBRARY_PATH', '')
    }
    
    # Create mock OpenFOAM directory structure
    for key, path in env_vars.items():
        if key != 'PATH' and key != 'LD_LIBRARY_PATH':
            Path(path).mkdir(parents=True, exist_ok=True)
    
    return env_vars


@pytest.fixture
def mock_templates(temp_dir) -> Path:
    """Create mock template structure."""
    templates_path = Path(temp_dir) / "templates"
    
    # Create templates for all supported modules
    modules = ["SPM", "halfCell", "fullCell"]
    
    for module in modules:
        module_dir = templates_path / module
        module_dir.mkdir(parents=True)
        
        # Create README
        (module_dir / "README.md").write_text(f"{module} Template")
        
        # Create solver directory
        solver_dir = module_dir / f"{module}Foam"
        solver_dir.mkdir()
        
        # Create Make directory and files
        make_dir = solver_dir / "Make"
        make_dir.mkdir()
        
        make_files = make_dir / "files"
        make_files.write_text(f"""{module}Foam.C

EXE = \$(FOAM_APPBIN)/{module}Foam_OF6
""")
        
        make_options = make_dir / "options"
        make_options.write_text("""EXE_INC = \\
    -I\$(LIB_SRC)/finiteVolume/lnInclude \\
    -I\$(LIB_SRC)/meshTools/lnInclude

EXE_LIBS = \\
    -lfiniteVolume \\
    -lmeshTools
""")
        
        # Create source file
        source_file = solver_dir / f"{module}Foam.C"
        source_file.write_text(f"""/* {module}Foam solver */
#include "fvCFD.H"

int main(int argc, char *argv[])
{{
    Info<< "Starting {module}Foam solver" << endl;
    return 0;
}}
""")
    
    return templates_path


@pytest.fixture
def mock_project(temp_dir, mock_templates) -> Dict[str, Path]:
    """Create a mock project structure."""
    from src.core.project_manager import ProjectManager
    
    # Mock the templates path
    with patch('src.core.constants.TEMPLATES_PATH', mock_templates):
        pm = ProjectManager()
        pm.create_project(temp_dir, "test_project", "SPM")
    
    project_path = Path(temp_dir) / "test_project"
    
    return {
        'project_path': project_path,
        'solver_path': project_path / "SPMFoam",
        'case_path': project_path / "Case",
        'system_path': project_path / "Case" / "system",
        'constant_path': project_path / "Case" / "constant"
    }


@pytest.fixture
def mock_ui_files(temp_dir) -> Dict[str, Path]:
    """Create mock UI files."""
    ui_files = {
        'mainwindow.ui': '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>BatteryFOAM</string>
  </property>
 </widget>
</ui>''',
        
        'carboninterface.ui': '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>CarbonInterface</class>
 <widget class="QWidget" name="CarbonInterface">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1000</width>
    <height>700</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>SPM Interface</string>
  </property>
 </widget>
</ui>''',
        
        'halfcellinterface.ui': '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>HalfCellInterface</class>
 <widget class="QWidget" name="HalfCellInterface">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1000</width>
    <height>700</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Half-Cell Interface</string>
  </property>
 </widget>
</ui>''',
        
        'fullcellfoam.ui': '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>FullCellInterface</class>
 <widget class="QWidget" name="FullCellInterface">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1000</width>
    <height>700</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Full-Cell Interface</string>
  </property>
 </widget>
</ui>''',
        
        'resultinterface.ui': '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>ResultInterface</class>
 <widget class="QWidget" name="ResultInterface">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1000</width>
    <height>700</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Results Interface</string>
  </property>
 </widget>
</ui>''',
    }
    
    created_files = {}
    for filename, content in ui_files.items():
        file_path = Path(temp_dir) / filename
        file_path.write_text(content)
        created_files[filename] = file_path
    
    return created_files


# Pytest markers for test categorization
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
pytest.mark.ui = pytest.mark.ui
pytest.mark.openfoam = pytest.mark.openfoam
pytest.mark.slow = pytest.mark.slow


# Conditional fixtures based on availability
@pytest.fixture
def qt_app():
    """PyQt6 application fixture (skipped if PyQt6 not available)."""
    if not HAS_QT:
        pytest.skip("PyQt6 not available")
    return qt_app


# Mock utilities
def create_mock_process(returncode=0, stdout_lines=None, stderr_lines=None):
    """Create a mock process for testing."""
    mock_process = Mock()
    mock_process.returncode = returncode
    mock_process.stdout = iter(stdout_lines or [])
    mock_process.stderr = iter(stderr_lines or [])
    mock_process.poll.return_value = returncode
    mock_process.wait.return_value = returncode
    return mock_process


def create_mock_widget():
    """Create a mock widget for testing."""
    if not HAS_QT:
        return None
    
    from PyQt6.QtWidgets import QWidget
    widget = QWidget()
    widget.setObjectName("MockWidget")
    return widget


# Test utilities
class TestTimer:
    """Simple timer for performance testing."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        import time
        self.start_time = time.perf_counter()
    
    def stop(self):
        import time
        self.end_time = time.perf_counter()
    
    def elapsed(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class TestError(Exception):
    """Custom exception for test errors."""
    pass


# Cleanup utilities
def cleanup_temp_files(directory: Path, pattern: str = "*.tmp"):
    """Clean up temporary files matching pattern."""
    for file_path in directory.glob(pattern):
        try:
            file_path.unlink()
        except OSError:
            pass  # Ignore errors during cleanup


# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "ui: mark test as UI test"
    )
    config.addinivalue_line(
        "markers", "openfoam: mark test as OpenFOAM integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file names
        if "test_unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        
        # Add slow marker for performance tests
        if "performance" in item.nodeid or "benchmark" in item.nodeid:
            item.add_marker(pytest.mark.slow)


def pytest_runtest_setup(item):
    """Setup hook for each test."""
    # Skip UI tests if PyQt6 is not available
    if "qt_app" in item.fixturenames and not HAS_QT:
        pytest.skip("PyQt6 not available")
    
    # Skip slow tests if --fast flag is used
    if item.get_closest_marker("slow") and item.config.getoption("--fast"):
        pytest.skip("skipped slow test")


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--fast", action="store_true", default=False,
        help="run tests faster by skipping slow tests"
    )
    parser.addoption(
        "--performance", action="store_true", default=False,
        help="run performance tests"
    )


# Test data generators
def generate_large_parameter_content(size_mb: int = 1) -> str:
    """Generate large parameter file content."""
    content = "/* Large parameter file */\n"
    line_count = int(size_mb * 1024 * 1024 / 100)  # Approximate
    
    for i in range(line_count):
        content += f"vertex {i} ({i} {i} {i});\n"
    
    return content


def generate_complex_ui_content(widget_count: int = 100) -> str:
    """Generate complex UI file content."""
    ui_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>ComplexWidget</class>
 <widget class="QWidget" name="ComplexWidget">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Complex Widget</string>
  </property>
'''
    
    for i in range(widget_count):
        ui_content += f'''  <widget class="QPushButton" name="button_{i}">
   <property name="geometry">
    <rect>
     <x>{i % 20 * 40}</x>
     <y>{i // 20 * 30}</y>
     <width>30</width>
     <height>20</height>
    </rect>
   </property>
   <property name="text">
    <string>Button {i}</string>
   </property>
  </widget>
'''
    
    ui_content += ''' </widget>
</ui>'''
    
    return ui_content