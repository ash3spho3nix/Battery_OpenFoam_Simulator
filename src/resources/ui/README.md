# UI Files

This directory contains Qt Designer UI files (.ui) that define the graphical
user interface layouts. These files are used with PyQt6/PySide6 to create
the application interfaces.

## UI Files

The following UI files should be present (copied from the C++ version):

- mainwindow.ui - Main application window
- carboninterface.ui - Single Particle Model interface
- halfcellinterface.ui - P2D Half Cell interface
- fullcellfoam.ui - P2D Full Cell interface
- resultinterface.ui - Results visualization interface

## Usage

UI files can be converted to Python code using:

```bash
pyuic6 filename.ui -o filename_ui.py
```

## Note

This is a placeholder directory. The actual .ui files should be copied from the
C++ version's SourceCode directory.