#!/bin/bash
source /c/Users/vsharma.A123SYSTEMSEU/Documents/OpenFoam/v2312/msys64/home/ofuser/OpenFOAM/OpenFOAM-v2312/etc/bashrc
echo "Checking OpenFOAM commands..."
which blockMesh
which topoSet
which splitMeshRegions
echo "PATH: $PATH"
echo "WM_PROJECT_DIR: $WM_PROJECT_DIR"