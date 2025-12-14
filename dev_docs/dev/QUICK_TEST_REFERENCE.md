# 🎯 QUICK REFERENCE - What to Test Manually

## ⚡ CRITICAL TESTS (Test These First!)

### 1. Application Startup (30 seconds)
```bash
cd Battery_OpenFoam_Simulator
python src/main.py
```
**Expected:** Window opens, no crashes, two tabs visible

**If fails:** Check Python environment, PyQt6 installed

---

### 2. OpenFOAM-MSYS2 Verification (1 minute)
```bash
# In Command Prompt
OpenFOAM-MSYS2.bat -c "which blockMesh"
```
**Expected:** Path to blockMesh printed (e.g., `/opt/OpenFOAM/...`)

**If fails:** OpenFOAM-MSYS2 not installed or not in PATH

---

### 3. MSYS2 Path Conversion (2 minutes)
```python
# In Python console (from project root)
import sys
sys.path.insert(0, 'src')
from openfoam.msys2_executor import get_executor

executor = get_executor()
print(executor.verify_msys2())  # Should be True
print(executor.convert_windows_path_to_msys2(r"C:\Test\Path"))  
# Should print: /c/Test/Path
```

**If fails:** Check msys2_executor.py for errors

---

### 4. Project Creation (5 minutes)
1. Run application
2. Click "New" tab
3. Select "SPM" radio button
4. Enter project name: `test_001`
5. Click "Choose" and select folder
6. Click "Next"

**Expected:** 
- Project folder created at `selected_path/test_001/`
- Contains `Case/` and `SPMFoam/` directories
- Interface window opens (may be incomplete)

**If fails:** 
- Check logs: `battery_simulator.log`
- Verify main_window.py integration done
- Check template path exists

---

## 🔧 INTEGRATION TESTS (After Phase 1 Integration)

### 5. Exception Handling Works (2 minutes)
1. Open application
2. Click any button without setting up project
3. **Expected:** Error dialog appears (not crash)
4. **Expected:** Error logged to `battery_simulator.log`

---

### 6. Terminal Output (3 minutes)
1. Create SPM project
2. Go to Terminal tab
3. Enter command: `ls` (or `dir` on Windows)
4. Click "Execute"

**Expected:** Command output appears in terminal area

**If fails:** Process controller not working

---

### 7. Interface Navigation (2 minutes)
1. Create SPM project (interface opens)
2. Look for "Back" or "Home" button
3. Click it

**Expected:** Returns to main window

**If fails:** Signal/slot connection missing

---

## 📊 PHASE 2 READINESS TESTS

### 8. Geometry Tab Exists (1 minute)
1. Create SPM project
2. Check for "Geometry" tab
3. Check for input fields: Length, Width, Height, Radius

**Expected:** All fields present and editable

---

### 9. Parameter Files Exist (2 minutes)
Navigate to project: `test_001/Case/`

Check files exist:
- `system/blockMeshDict` ✓
- `system/topoSetDict` ✓
- `system/controlDict` ✓
- `system/fvSchemes` ✓
- `system/fvSolution` ✓
- `constant/LiProperties` ✓

**If missing:** Template copy failed

---

### 10. Manual OpenFOAM Test (3 minutes)
```bash
cd test_001/Case
OpenFOAM-MSYS2.bat -c "blockMesh"
```

**Expected:** Mesh creation output, no errors

**If fails:** OpenFOAM setup issue, not Python code

---

## 🚦 GO/NO-GO DECISION

### ✅ READY FOR PHASE 2 IF:
- [x] All Critical Tests (1-4) pass
- [x] Application starts and creates projects
- [x] OpenFOAM-MSYS2 verified working
- [x] Logs show no critical errors
- [x] Template files copied correctly

### ⚠️ FIX BEFORE PHASE 2 IF:
- [ ] Application crashes on startup
- [ ] OpenFOAM-MSYS2 not working
- [ ] Project creation fails
- [ ] Critical errors in logs
- [ ] Templates not copying

---

## 📝 QUICK ISSUE RESOLUTION

| Issue | Likely Cause | Quick Fix |
|-------|-------------|-----------|
| App won't start | Import error | Check all `__init__.py` files exist |
| OpenFOAM not found | PATH issue | Add OpenFOAM-MSYS2.bat to PATH |
| Project creation fails | Permission | Run as admin or change target folder |
| No terminal output | Process controller | Check logs, verify threading |
| Interface won't open | Import error | Check interface file imports |

---

## 🔍 LOG LOCATIONS

**Application Log:** `battery_simulator.log` (project root)

**Look for:**
- `ERROR` lines - critical issues
- `WARNING` lines - potential problems  
- `INFO` lines - normal operations
- Stack traces after errors

**Common Log Searches:**
```bash
# On Windows (PowerShell)
Select-String -Path battery_simulator.log -Pattern "ERROR"

# On Linux/Mac
grep "ERROR" battery_simulator.log
```

---

## 📞 WHEN TO ASK FOR HELP

### Before Asking:
1. Check logs
2. Try manual OpenFOAM command
3. Verify Python environment
4. Read error message carefully
5. Check this reference card

### When Asking, Provide:
- Exact error message
- Relevant log entries
- What you were doing
- What you expected
- What actually happened
- OS and Python version

---

## ⏱️ TIME ESTIMATES

| Task | Expected Time |
|------|--------------|
| Critical Tests (1-4) | 5-10 minutes |
| Integration Tests (5-7) | 10 minutes |
| Phase 2 Readiness (8-10) | 10 minutes |
| **Total Initial Testing** | **~30 minutes** |

---

## 🎯 SUCCESS METRICS

After Phase 1 testing, you should have:
- ✅ App launches successfully
- ✅ OpenFOAM integration verified
- ✅ Project creation works (even if incomplete)
- ✅ No critical errors in logs
- ✅ Basic UI navigation functional

This confirms Phase 1 is solid and Phase 2 can begin.

---

## 📚 QUICK LINKS

- **Full Testing:** `MANUAL_TESTING_CHECKLIST.md`
- **Implementation Guide:** `PHASE_2_3_IMPLEMENTATION_GUIDE.md`
- **AI Prompt:** `AI_IMPLEMENTATION_PROMPT.md`
- **Summary:** `PHASE1_IMPLEMENTATION_SUMMARY.md`

---

## 🚀 NEXT STEPS

1. Run Critical Tests 1-4
2. Fix any failures
3. Run Integration Tests 5-7
4. Run Phase 2 Readiness Tests 8-10
5. If all pass → Integrate main_window.py
6. Begin Phase 2 implementation

**Remember:** Test incrementally, fix issues immediately, don't accumulate problems!
