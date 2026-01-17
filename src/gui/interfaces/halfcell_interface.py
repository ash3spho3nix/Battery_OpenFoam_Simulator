"""
HalfCell Interface - Simplified.
"""

import logging
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal

from src.gui.ui_loader import UILoader
from src.openfoam.process_controller import ProcessController
from src.openfoam.solver_manager import OpenFOAMSolverManager

logger = logging.getLogger(__name__)


class HalfCellInterface(QDialog):
    """HalfCell interface with MSYS2 execution."""
    
    exit_signal = pyqtSignal()
    
    def __init__(self, parent=None, ui_config=None):
        super().__init__(parent)
        
        ui_loader = UILoader()
        ui_loader.load_ui("halfcellinterface", self)
        
        self.process_controller = ProcessController()
        self.solver_manager = OpenFOAMSolverManager()
        
        self.project_path = None
        self.project_name = None
        self.case_path = None
        
        self._set_defaults()
        self._connect_signals()
        logger.info("HalfCellInterface initialized")
    
    def set_project_paths(self, project_path: str, project_name: str):
        self.project_path = project_path
        self.project_name = project_name
        self.case_path = project_path
        
        self.solver_manager.set_case_path(self.case_path)
        self.solver_manager.set_solver("halfCellFoam")
        logger.info(f"Project paths set: {self.case_path}")
    
    def _set_defaults(self):
        """Set default values for interface widgets."""
        from src.core.constants import UI_DEFAULT_VALUES
        
        defaults = UI_DEFAULT_VALUES.get("halfcell_interface", {})
        
        # Set combo box defaults
        if hasattr(self, 'unit_select_box'):
            self.unit_select_box.setCurrentIndex(defaults.get("unit_index", 0))
        
        # Set line edit defaults
        if hasattr(self, 'length_lineEdit'):
            self.length_lineEdit.setText(str(defaults.get("length", "100")))
        if hasattr(self, 'width_lineEdit'):
            self.width_lineEdit.setText(str(defaults.get("width", "100")))
        if hasattr(self, 'height_lineEdit'):
            self.height_lineEdit.setText(str(defaults.get("height", "100")))
        if hasattr(self, 'length2_lineEdit'):
            self.length2_lineEdit.setText(str(defaults.get("length2", "100")))
        if hasattr(self, 'x_divide_lineEdit'):
            self.x_divide_lineEdit.setText(str(defaults.get("x_divide", "20")))
        if hasattr(self, 'y_divide_lineEdit'):
            self.y_divide_lineEdit.setText(str(defaults.get("y_divide", "20")))
        if hasattr(self, 'z_divide_lineEdit'):
            self.z_divide_lineEdit.setText(str(defaults.get("z_divide", "20")))
        if hasattr(self, 'x2_divide_lineEdit'):
            self.x2_divide_lineEdit.setText(str(defaults.get("x2_divide", "20")))
        if hasattr(self, 'CeWE_lineEdit'):
            self.CeWE_lineEdit.setText(str(defaults.get("CeWE", "1000")))
        if hasattr(self, 'Cesp_lineEdit'):
            self.Cesp_lineEdit.setText(str(defaults.get("Cesp", "1000")))
        if hasattr(self, 'fWE_lineEdit'):
            self.fWE_lineEdit.setText(str(defaults.get("fWE", "0.5")))
        if hasattr(self, 'maxWE_lineEdit'):
            self.maxWE_lineEdit.setText(str(defaults.get("maxWE", "30000")))
        if hasattr(self, 'R_lineEdit'):
            self.R_lineEdit.setText(str(defaults.get("R", "8.314")))
        if hasattr(self, 'brugg_lineEdit'):
            self.brugg_lineEdit.setText(str(defaults.get("brugg", "1.5")))
        if hasattr(self, 'D0Ce_lineEdit'):
            self.D0Ce_lineEdit.setText(str(defaults.get("D0Ce", "1e-10")))
        if hasattr(self, 'faisWE_lineEdit'):
            self.faisWE_lineEdit.setText(str(defaults.get("faisWE", "0.5")))
        if hasattr(self, 'tNo_lineEdit'):
            self.tNo_lineEdit.setText(str(defaults.get("tNo", "0.5")))
    
    def _connect_signals(self):
        # Basic connections - adjust based on actual .ui file
        self.process_controller.output_received.connect(self._on_output)
        self.process_controller.error_received.connect(self._on_error)
        self.process_controller.process_finished.connect(self._on_finished)
        logger.info("Signals connected")
    
    def _on_output(self, text: str):
        # Output to terminal widget if exists
        pass
    
    def _on_error(self, text: str):
        logger.error(f"Process error: {text}")
    
    def _on_finished(self, exit_code: int):
        logger.info(f"Process finished: {exit_code}")
