# OpenFOAM Templates

This directory contains OpenFOAM solver templates for different simulation modules:

## Template Structure

Each template directory should contain:
- Solver source code
- Make directory with compilation files
- Case directory with example configuration
- Template parameter files

## Available Templates

### SPM (Single Particle Model)
- Template for single particle battery simulations
- Contains SPMFoam solver

### halfCell (P2D Half Cell)
- Template for pseudo-2D half-cell simulations
- Contains halfCellFoam solver

### fullCell (P2D Full Cell)
- Template for pseudo-2D full-cell simulations  
- Contains fullCellFoam solver

## Note

This is a placeholder directory. The actual templates should be copied from the
C++ version's GUI/OpenfoamModule directory structure.