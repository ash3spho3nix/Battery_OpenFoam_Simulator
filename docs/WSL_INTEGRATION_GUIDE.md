# WSL Integration Guide for OpenFOAM Execution

This guide documents the changes made to enable running OpenFOAM in WSL from Python, using generated case files, while capturing the WSL paths for template case files.

## Overview

The OpenFOAM execution layer has been updated to support running OpenFOAM commands in WSL (Windows Subsystem for Linux) from Python. This allows users to leverage OpenFOAM installed in WSL while using the Python-based GUI and file generation tools on Windows.

## Changes Made

### 1. WSL Path Capture

A script [`scripts/capture_wsl_paths.py`](scripts/capture_wsl_paths.py) has been created to identify and capture the WSL paths for OpenFOAM template files. This script:

- Identifies the template directories in the project.
- Converts Windows paths to WSL paths using the `convert_to_wsl_path` method.
- Saves the mapping between Windows paths and WSL paths to a file (`wsl_path_mapping.txt`).

Example WSL path mapping:
```
C:\Users\vsharma.A123SYSTEMSEU\Documents\BatterySimulator\BatteryOpenFoamSimulator\Battery_OpenFoam_Simulator\src\resources\templates\fullCell
/mnt/c/Users/vsharma.A123SYSTEMSEU/Documents/BatterySimulator/BatteryOpenFoamSimulator/Battery_OpenFoam_Simulator/src/resources/templates/fullCell
```

### 2. WSL Execution Test

A minimal test script [`scripts/test_wsl_execution.py`](scripts/test_wsl_execution.py) has been created to verify WSL execution of OpenFOAM commands. This script:

- Verifies that WSL is accessible and OpenFOAM is installed.
- Uses one of the template directories for testing.
- Executes a simple OpenFOAM command (e.g., `blockMesh`) in WSL.
- Captures stdout, stderr, and the exit code for debugging.

### 3. Refactored Simulate/Run Function

The `ProcessController` class in [`src/openfoam/process_controller.py`](src/openfoam/process_controller.py) has been updated to use the `WSLExecutor` instead of the `MSYS2Executor`. This change enables:

- Spawning the OpenFOAM process in WSL.
- Using the confirmed WSL template paths for generated cases.
- Capturing stdout/stderr for logging.
- Running asynchronously without blocking the GUI.

### 4. WSL Executor

The `WSLExecutor` class in [`src/openfoam/wsl_executor.py`](src/openfoam/wsl_executor.py) has been enhanced to support:

- Verification of WSL and OpenFOAM installation.
- Conversion of Windows paths to WSL paths.
- Execution of OpenFOAM commands in WSL with real-time output callbacks.
- Asynchronous execution to avoid blocking the GUI.

## How It Works

### Path Conversion

The `convert_to_wsl_path` method in `WSLExecutor` converts Windows paths to WSL paths. For example:

```python
windows_path = "C:\\Users\\name\\project"
wsl_path = executor.convert_to_wsl_path(windows_path)
# wsl_path = "/mnt/c/Users/name/project"
```

### Command Execution

The `execute_command` method in `WSLExecutor` executes OpenFOAM commands in WSL:

```python
command = "blockMesh"
working_dir = "C:\\Users\\name\\project"
return_code, stdout, stderr = executor.execute_command(command, working_dir)
```

### Asynchronous Execution

The `execute_command_with_callback` method in `WSLExecutor` executes OpenFOAM commands asynchronously with real-time output callbacks:

```python
def on_stdout(text):
    print(f"stdout: {text}")

def on_stderr(text):
    print(f"stderr: {text}")

def on_completion(exit_code):
    print(f"Process completed with exit code: {exit_code}")

executor.execute_command_with_callback(
    command,
    working_dir,
    on_stdout,
    on_stderr,
    on_completion
)
```

## Usage

### Running OpenFOAM in WSL

To run OpenFOAM commands in WSL from Python:

1. Ensure WSL is installed and OpenFOAM is accessible in WSL.
2. Use the `WSLExecutor` class to execute OpenFOAM commands:

```python
from src.openfoam.wsl_executor import WSLExecutor

executor = WSLExecutor()

# Verify WSL and OpenFOAM
if executor.verify_wsl():
    print("WSL and OpenFOAM are accessible.")
else:
    print("WSL or OpenFOAM is not accessible.")

# Execute a command
command = "blockMesh"
working_dir = "C:\\Users\\name\\project"
return_code, stdout, stderr = executor.execute_command(command, working_dir)

print(f"Return code: {return_code}")
print(f"stdout: {stdout}")
print(f"stderr: {stderr}")
```

### Using the ProcessController

To use the `ProcessController` for asynchronous execution:

```python
from src.openfoam.process_controller import ProcessController

controller = ProcessController()

# Connect signals
controller.output_received.connect(lambda text: print(f"stdout: {text}"))
controller.error_received.connect(lambda text: print(f"stderr: {text}"))
controller.process_finished.connect(lambda exit_code: print(f"Process finished with exit code: {exit_code}"))

# Start the process
command = "blockMesh"
working_dir = "C:\\Users\\name\\project"
controller.start_process(command, working_dir)
```

## Limitations and Caveats

1. **WSL Installation**: WSL must be installed and configured on the Windows system.
2. **OpenFOAM Installation**: OpenFOAM must be installed and accessible in WSL.
3. **Path Conversion**: The path conversion assumes that the Windows drive is mounted under `/mnt/<drive>` in WSL. This is the default behavior for WSL.
4. **Command Availability**: OpenFOAM commands must be in the PATH in WSL or explicitly sourced in the user's `.bashrc` file.

## Conclusion

The OpenFOAM execution layer has been successfully updated to support running OpenFOAM in WSL from Python. This enables users to leverage OpenFOAM installed in WSL while using the Python-based GUI and file generation tools on Windows. The changes are minimal and focused on the execution layer, preserving the existing GUI, generation, and test logic.