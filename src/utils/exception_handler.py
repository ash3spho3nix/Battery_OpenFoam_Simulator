"""Global exception handling for Battery Simulator."""
import logging
import traceback
from functools import wraps
from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

def safe_slot(func):
    """Decorator to wrap slot handlers with exception handling."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Show user-friendly error
            try:
                QMessageBox.critical(
                    self if hasattr(self, 'show') else None,
                    "Error",
                    f"Operation failed: {str(e)}\n\nCheck battery_simulator.log for details."
                )
            except:
                # If even the error dialog fails, just log
                logger.error("Could not display error dialog")
            
            return None
    return wrapper
