# Project Analysis: Battery OpenFoam Simulator

## Overview
The Battery OpenFoam Simulator is a Python-based application designed to simulate battery behavior (SPM, Half Cell, Full Cell models) using OpenFOAM as the computational backend. It features a GUI, project management, and cross-platform execution capabilities, specifically targeting Windows via MSYS2 integration.

## File Index & Analysis

### OpenFOAM Execution
**File**: `src/openfoam/msys2_executor.py`
- **Role**: Handles the interface between the Python application and the OpenFOAM installation on Windows.
- **Mechanism**: Uses `subprocess` to invoke MSYS2's `bash.exe` to execute OpenFOAM commands.
- **Key Features**:
  - Path conversion between Windows (`C:\...`) and MSYS2 (`/c/...`) formats.
  - Verification of OpenFOAM availability.
  - Real-time output capturing via callbacks.

### Core Configuration
**Files**: `src/core/config.py`, `src/core/constants.py`
- **Role**: Centralizes application settings, simulation parameters, and file paths.
- **Key Data**:
  - **Simulation Modules**: SPM, Half Cell, Full Cell.
  - **Solver Names**: `SPMFoam_OF6`, `halfCellFoam_OF6`, `fullCellFoam_OF6`.
  - **Default Parameters**: Geometry dimensions, electrochemical properties (Li diffusion, reaction rates).
  - **UI/Template Paths**: Resource locations for the GUI and OpenFOAM case templates.

### Documentation
**File**: `docs/DEPLOYMENT_GUIDE.md`
- **Role**: Detailed instructions for deployment, including prerequisites (Python, OpenFOAM), installation methods, and troubleshooting.

### Testing
**File**: `tests/unit/test_openfoam/test_openfoam_integration.py`
- **Role**: Unit tests for the OpenFOAM integration layer.
- **Coverage**:
  - Process controller logic.
  - Solver manager functionality.
  - Case structure validation.
  - MSYS2 executor path handling.

## Current Focus
The primary focus is on `src/openfoam/msys2_executor.py`, which contains the logic for executing OpenFOAM commands on Windows systems.
