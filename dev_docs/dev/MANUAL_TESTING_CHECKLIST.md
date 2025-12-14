# Manual Testing Checklist

## Phase 1: Foundation Stability (CRITICAL - Test First)

### 1.1 Application Startup
- [ ] Run `python src/main.py` - Application window should open without errors
- [ ] Check console for any error messages
- [ ] Verify main window displays with "New" and "Open" tabs
- [ ] Close application cleanly (no hanging processes)

### 1.2 OpenFOAM-MSYS2 Integration (MOST CRITICAL)
- [ ] Open Command Prompt
- [ ] Navigate to project root
- [ ] Run: `OpenFOAM-MSYS2.bat` - Should open MSYS2 terminal
- [ ] In MSYS2, run: `which blockMesh` - Should return path to OpenFOAM commands
- [ ] Test subprocess execution:
  - Open Python console in project
  - Run: `import subprocess; subprocess.run(['OpenFOAM-MSYS2.bat', '-c', 'echo test'], shell=True)`
  - Should print "test" without errors

### 1.3 Project Creation Workflow
**For SPM (Carbon):**
- [ ] Click "New" tab
- [ ] Select "SPM" radio button
- [ ] Enter project name: `test_spm_001`
- [ ] Click "Browse" to select project path
- [ ] Click "Next" - Should navigate to Carbon interface
- [ ] Check that test_projects/test_spm_001 folder is created
- [ ] Verify folder structure:
  ```
  test_spm_001/
    ├── Case/
    │   ├── 0/
    │   ├── constant/
    │   └── system/
    └── SPMFoam/
  ```

**For HalfCell:**
- [ ] Repeat above with "halfCell" selection
- [ ] Verify folder structure contains WE and sep subdirectories

**For FullCell:**
- [ ] Repeat above with "fullCell" selection
- [ ] Verify folder structure contains anode, cathode, sep subdirectories

### 1.4 Windows Path Handling
- [ ] Create project with path containing spaces: `C:\My Projects\test`
- [ ] Verify no path errors
- [ ] Create project on different drive (if available): `D:\test`

---

## Phase 2: SPM/Carbon Complete Workflow

### 2.1 Geometry Tab
- [ ] Open SPM project created above
- [ ] Navigate to Geometry tab
- [ ] Modify values:
  - Length: `150` μm
  - Width: `150` μm
  - Height: `150` μm
  - Radius: `70` μm
  - X divisions: `30`
  - Y divisions: `30`
  - Z divisions: `30`
- [ ] Click "Change Geometry" - Should see success message in terminal
- [ ] Check `system/blockMeshDict` file was updated with new values
- [ ] Click "Run Geometry" - Should execute:
  - `blockMesh` - Creates mesh
  - `topoSet` - Creates cell sets
  - `splitMeshRegions` - Splits regions
- [ ] Watch terminal output for errors
- [ ] Check that `constant/ele/` and `constant/solidPhase/` folders are created

### 2.2 Constants Tab
- [ ] Navigate to Constants tab
- [ ] Modify parameters:
  - DS_value: `2e-14`
  - CS_max: `31000`
  - Temperature: `300`
- [ ] Select material: Carbon (Gr) / Silicon (Si)
- [ ] Click "Change Constants"
- [ ] Verify `constant/LiProperties` file is updated
- [ ] Click "Run Constants" - Should compile solver:
  - `wclean` - Clean previous compilation
  - `wmake` - Compile SPMFoam

### 2.3 Boundary Tab
- [ ] Navigate to Boundary tab
- [ ] Set initial conditions:
  - Initial Cs: `15000`
- [ ] Select Charge/Discharge mode
- [ ] Click "Change Boundary"
- [ ] Verify `0/` files are updated

### 2.4 Functions Tab
- [ ] Navigate to Functions tab
- [ ] Select discretization schemes:
  - Derivative: `Euler`
  - Gradient: `Gauss linear`
  - Divergence: `bounded Gauss upwind`
  - Laplacian: `Gauss linear uncorrected`
  - Interpolation: `linear`
- [ ] Click "Change Functions"
- [ ] Verify `system/fvSchemes` and `system/fvSolution` are updated

### 2.5 Control Tab
- [ ] Navigate to Control tab
- [ ] Set simulation parameters:
  - End time: `3000`
  - Delta T: `0.1`
  - Write interval: `600`
  - Tolerance: `1e-6`
- [ ] Click "Change Control"
- [ ] Verify `system/controlDict` is updated
- [ ] Click "Run" button
- [ ] Monitor Terminal tab for:
  - Simulation starting message
  - Real-time solver output
  - Convergence information
  - Time step progression
- [ ] Test "Pause/Resume" button during simulation
- [ ] Test "Stop" button

### 2.6 Terminal Tab
- [ ] Navigate to Terminal tab
- [ ] Enter manual command: `ls` (or `dir` on Windows)
- [ ] Press Enter or click "Execute"
- [ ] Verify command output appears
- [ ] Try OpenFOAM command: `checkMesh`
- [ ] Verify output is captured

---

## Phase 3: HalfCell & FullCell Workflows

### 3.1 HalfCell Geometry
- [ ] Create new HalfCell project: `test_halfcell_001`
- [ ] Geometry tab - Set dimensions:
  - WE thickness: `50` μm
  - Separator thickness: `25` μm
  - Width/Height: `100` μm each
- [ ] Click "Change Geometry"
- [ ] Click "Run Geometry"
- [ ] Verify mesh created for both WE and separator regions

### 3.2 HalfCell Constants
- [ ] Constants tab - Set WE parameters:
  - Active material fraction: `0.5`
  - Porosity: `0.3`
- [ ] Set separator parameters:
  - Porosity: `0.5`
- [ ] Click "Change Constants"
- [ ] Verify both `constant/WE/LiProperties` and `constant/sep/LiProperties`

### 3.3 HalfCell Simulation
- [ ] Complete boundary, functions, control tabs similar to SPM
- [ ] Run simulation
- [ ] Monitor for region-specific output (WE and sep)

### 3.4 FullCell Geometry
- [ ] Create new FullCell project: `test_fullcell_001`
- [ ] Geometry tab - Set three regions:
  - Anode thickness: `70` μm
  - Separator thickness: `25` μm
  - Cathode thickness: `50` μm
- [ ] Click "Change Geometry"
- [ ] Click "Run Geometry"
- [ ] Verify three regions created: anode, separator, cathode

### 3.5 FullCell Constants
- [ ] Set anode material properties (e.g., Graphite)
- [ ] Set cathode material properties (e.g., NCA/NMC)
- [ ] Set separator properties
- [ ] Verify all three `LiProperties` files updated

### 3.6 FullCell Simulation
- [ ] Complete all tabs
- [ ] Run full cell simulation
- [ ] Monitor terminal for three-region coupling

---

## Error Scenarios to Test

### E.1 Invalid Input Handling
- [ ] Enter negative values for dimensions - Should show error
- [ ] Enter radius larger than dimensions - Should show error
- [ ] Leave required fields empty - Should show validation error
- [ ] Enter non-numeric values - Should reject or show error

### E.2 Missing OpenFOAM
- [ ] Temporarily rename OpenFOAM-MSYS2.bat
- [ ] Try to run geometry - Should show clear error message
- [ ] Restore file name

### E.3 Project Path Issues
- [ ] Try to create project in read-only location - Should show permission error
- [ ] Try to create project with existing name - Should warn about overwrite
- [ ] Create project with special characters in name - Should validate

### E.4 Simulation Failures
- [ ] Set invalid parameters (e.g., tolerance = 0)
- [ ] Run simulation - Should fail gracefully
- [ ] Check that error message is displayed in terminal
- [ ] Verify application doesn't crash

### E.5 Process Control
- [ ] Start simulation
- [ ] Close application during simulation - Processes should be terminated
- [ ] Start simulation
- [ ] Crash simulation (e.g., delete mesh files mid-run)
- [ ] Verify error is caught and reported

---

## Performance Tests

### P.1 Large Mesh
- [ ] Create SPM project with divisions: 50x50x50
- [ ] Run geometry - Should complete (may take time)
- [ ] Monitor memory usage

### P.2 Long Simulation
- [ ] Set end time: 10000s
- [ ] Start simulation
- [ ] Monitor for memory leaks in terminal output
- [ ] Test pause/resume after 100+ timesteps

### P.3 Multiple Projects
- [ ] Open 3 different projects in sequence
- [ ] Verify no resource conflicts
- [ ] Close and reopen application
- [ ] Recent projects should be accessible

---

## UI Responsiveness Tests

### U.1 Button States
- [ ] Before project creation - Most buttons should be disabled
- [ ] After project creation - Geometry buttons enabled
- [ ] During simulation - Run button disabled, Pause/Stop enabled
- [ ] After simulation - Run button re-enabled

### U.2 Tab Navigation
- [ ] Navigate through all tabs in order
- [ ] Return to previous tabs
- [ ] Verify data persistence (values don't reset)

### U.3 Window Operations
- [ ] Minimize/Maximize window
- [ ] Resize window
- [ ] Move window to different screen (if multi-monitor)

---

## Integration Tests

### I.1 Complete SPM Workflow
- [ ] Create project → Modify geometry → Run geometry
- [ ] Modify constants → Compile solver
- [ ] Set boundary conditions
- [ ] Configure functions and control
- [ ] Run full simulation to completion
- [ ] Check output files exist in case directory

### I.2 Complete HalfCell Workflow
- [ ] Same as SPM but for HalfCell
- [ ] Verify two-region output

### I.3 Complete FullCell Workflow
- [ ] Same as SPM but for FullCell  
- [ ] Verify three-region output

---

## Critical Issues to Watch For

### ⚠️ HIGH PRIORITY
1. **Application crashes on button click** - Check exception handling
2. **OpenFOAM commands not found** - Path/environment issue
3. **Files not being updated** - Permission or path issue
4. **Simulation runs but no output** - Check case directory setup
5. **Process hangs indefinitely** - Timeout not working

### ⚠️ MEDIUM PRIORITY
6. Widget values not saving between tabs
7. Terminal output not appearing
8. Slow UI response
9. Memory usage growing continuously
10. Can't stop simulation once started

### ⚠️ LOW PRIORITY
11. UI layout issues
12. Button text unclear
13. Missing tooltips
14. Inconsistent styling

---

## Success Criteria

### Minimum Viable (MVP)
- ✅ Application starts without crash
- ✅ Can create all 3 project types
- ✅ SPM simulation runs to completion
- ✅ Terminal shows output
- ✅ Can stop/pause simulation

### Full Success
- ✅ All above MVP criteria
- ✅ HalfCell simulation works
- ✅ FullCell simulation works
- ✅ All parameter modifications work
- ✅ Error handling graceful
- ✅ No crashes under normal use

---

## Test Log Template

```
Test Date: YYYY-MM-DD
Tester: [Name]
OS: Windows 10/11
OpenFOAM Version: [version]

Test Case: [e.g., 2.1 Geometry Tab]
Status: PASS / FAIL / PARTIAL
Notes: [Any observations]
Errors: [Error messages if any]
Screenshots: [Attach if relevant]
```

---

## Quick Smoke Test (5 minutes)

If time is limited, run this quick test:

1. [ ] Start application
2. [ ] Create SPM project "quick_test"
3. [ ] Click through all tabs (don't modify)
4. [ ] Run geometry (blockMesh only)
5. [ ] Check terminal for errors
6. [ ] Close application

If this passes, proceed with full testing.
If this fails, fix critical issues first.
