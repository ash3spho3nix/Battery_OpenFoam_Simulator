# Battery Simulator – Autonomous Multi-Agent Workflow
# Mode: 🏗️ Project Architect

## Workflow
This workflow runs a complete multi-agent pipeline with minimal user input:

1. 🏗️ Project Architect  
   - Analyze the full repository  
   - Produce an ordered task plan to fix the bugs in the project and to have end result as full working project
   - Summaries stored in memory for the next steps  
   - Can use other modes/agents also to make necessary changes

2. 💻 Core App Developer  
   - Implement missing Python modules  
   - Fix broken imports, UI loaders, OpenFOAM interface issues  
   - Apply patches step-by-step using Architect plan
   - Can use other modes also to make necessary changes
   - Proceed to next agent.  

3. 🎨 Interface Specialist  
   - Repair/finish all UI creation (PyQt6 hand-coded + .ui hybrid)  
   - Ensure navigation works (Next/Back signals)  
   - Fix circular import triggers  
   - Can use other modes also to make necessary changes
   - Proceed to next agent.  

4. ⚙️ OpenFOAM Integration Expert  
   - Validate solver invocation  
   - Fix subprocess, path resolution, template usage  
   - Replace blocking calls with safe non-blocking patterns
   - Can use other modes also to make necessary changes
   - Proceed to next agent  

5. 📁 Template Manager  
   - Rebuild template directories  
   - Ensure all simulation configs exist (SPM, HalfCell, FullCell)  
   - Normalize paths to cross-platform
   - Can use other modes also to make necessary changes
   - Proceed to next agent    

6. 🎭 UI Loading Specialist  
   - Validate UI loading modes: HAND_CODED, UI_FILES, AUTO  
   - Fix any failure modes  
   - Proceed to next agent

7. 🧪 Testing Engineer  
   - Generate pytest suite  
   - Add mocks for OpenFOAM & subprocess  
   - Target >80% coverage  
   - Run and repair until green
   - Proceed to next agent

8. 🐛 Battery Sim Debugger  
   - Detect final defects  
   - Run smoke tests  
   - Fix integration issues
   - Proceed to next agent 

9. 📚 Documentation Specialist  
   - Generate/update README and DEV_GUIDE  
   - Produce onboarding guide for new devs  

## Autonomous Execution Rules

- Each mode must produce a summary for the next mode.  
- Each mode must confirm progress before moving to next.  
- Failures roll back to the Debugger mode.  
- Only small, safe patches are allowed unless explicitly approved.  
- Testing Engineer must approve code health before documentation begins.  

## Start Command

Begin by running the Architect step:

