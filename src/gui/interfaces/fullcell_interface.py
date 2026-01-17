"""
FullCell Interface - Simplified.
"""

import logging
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal

from src.gui.ui_loader import UILoader
from src.openfoam.process_controller import ProcessController
from src.openfoam.solver_manager import OpenFOAMSolverManager

logger = logging.getLogger(__name__)


class FullCellInterface(QDialog):
    """FullCell interface with MSYS2 execution."""
    
    exit_signal = pyqtSignal()
    
    def __init__(self, parent=None, ui_config=None):
        super().__init__(parent)
        
        ui_loader = UILoader()
        ui_loader.load_ui("fullcellfoam", self)
        
        self.process_controller = ProcessController()
        self.solver_manager = OpenFOAMSolverManager()
        
        self.project_path = None
        self.project_name = None
        self.case_path = None
        
        self._set_defaults()
        self._connect_signals()
        logger.info("FullCellInterface initialized")
    
    def set_project_paths(self, project_path: str, project_name: str):
        self.project_path = project_path
        self.project_name = project_name
        self.case_path = project_path
        
        self.solver_manager.set_case_path(self.case_path)
        self.solver_manager.set_solver("fullCellFoam")
        logger.info(f"Project paths set: {self.case_path}")
    
    def _set_defaults(self):
        """Set default values for interface widgets."""
        from src.core.constants import UI_DEFAULT_VALUES
        
        defaults = UI_DEFAULT_VALUES.get("fullcell_interface", {})
        
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
        if hasattr(self, 'length3_lineEdit'):
            self.length3_lineEdit.setText(str(defaults.get("length3", "100")))
        if hasattr(self, 'x_divide_lineEdit'):
            self.x_divide_lineEdit.setText(str(defaults.get("x_divide", "20")))
        if hasattr(self, 'y_divide_lineEdit'):
            self.y_divide_lineEdit.setText(str(defaults.get("y_divide", "20")))
        if hasattr(self, 'z_divide_lineEdit'):
            self.z_divide_lineEdit.setText(str(defaults.get("z_divide", "20")))
        if hasattr(self, 'x2_divide_lineEdit'):
            self.x2_divide_lineEdit.setText(str(defaults.get("x2_divide", "20")))
        if hasattr(self, 'x3_divide_lineEdit'):
            self.x3_divide_lineEdit.setText(str(defaults.get("x3_divide", "20")))
        if hasattr(self, 'csmaxa_lineEdit'):
            self.csmaxa_lineEdit.setText(str(defaults.get("csmaxa", "30000")))
        if hasattr(self, 'csmaxc_lineEdit'):
            self.csmaxc_lineEdit.setText(str(defaults.get("csmaxc", "30000")))
        if hasattr(self, 'kreacta_lineEdit'):
            self.kreacta_lineEdit.setText(str(defaults.get("kreacta", "1e-11")))
        if hasattr(self, 'kreactc_lineEdit'):
            self.kreactc_lineEdit.setText(str(defaults.get("kreactc", "1e-11")))
        if hasattr(self, 'alphaca_lineEdit'):
            self.alphaca_lineEdit.setText(str(defaults.get("alphaca", "0.5")))
        if hasattr(self, 'alphaaa_lineEdit'):
            self.alphaaa_lineEdit.setText(str(defaults.get("alphaaa", "0.5")))
        if hasattr(self, 'alphacc_lineEdit'):
            self.alphacc_lineEdit.setText(str(defaults.get("alphacc", "0.5")))
        if hasattr(self, 'alphaac_lineEdit'):
            self.alphaac_lineEdit.setText(str(defaults.get("alphaac", "0.5")))
        if hasattr(self, 'porcea_lineEdit'):
            self.porcea_lineEdit.setText(str(defaults.get("porcea", "0.3")))
        if hasattr(self, 'porcec_lineEdit'):
            self.porcec_lineEdit.setText(str(defaults.get("porcec", "0.3")))
        if hasattr(self, 'f_lineEdit'):
            self.f_lineEdit.setText(str(defaults.get("f", "96485")))
        if hasattr(self, 'R_lineEdit'):
            self.R_lineEdit.setText(str(defaults.get("R", "8.314")))
        if hasattr(self, 'brugg_lineEdit'):
            self.brugg_lineEdit.setText(str(defaults.get("brugg", "1.5")))
        if hasattr(self, 'D0Ce_lineEdit'):
            self.D0Ce_lineEdit.setText(str(defaults.get("D0Ce", "1e-10")))
        if hasattr(self, 'tNo_lineEdit'):
            self.tNo_lineEdit.setText(str(defaults.get("tNo", "0.5")))
    
    def _connect_signals(self):
        self.process_controller.output_received.connect(self._on_output)
        self.process_controller.error_received.connect(self._on_error)
        self.process_controller.process_finished.connect(self._on_finished)
        logger.info("Signals connected")
    
    def _on_output(self, text: str):
        pass
    
    def _on_error(self, text: str):
        logger.error(f"Process error: {text}")
    
    def _on_finished(self, exit_code: int):
        logger.info(f"Process finished: {exit_code}")
