"""
UI Configuration for Battery Simulator - Full UI Loading Support.

This module provides configuration classes for UI loading modes,
allowing users to choose between .ui file loading and hand-coded
widget approaches. Supports all three loading modes.
"""

from enum import Enum
from typing import Optional


class UILoadingMode(Enum):
    """
    UI loading modes for the Battery Simulator.
    
    Defines different ways the application can load its user interface:
    - AUTO_DETECT: Try .ui files first, fallback to hand-coded widgets
    - UI_FILES: Force .ui file loading
    - HAND_CODED: Force hand-coded widgets
    """
    AUTO_DETECT = "auto_detect"     # Try .ui files, fallback to hand-coded
    UI_FILES = "ui_files"           # Load from .ui files
    HAND_CODED = "hand_coded"       # Use hand-coded widgets


class UIConfig:
    """
    Configuration for UI loading behavior.
    
    This class manages the configuration settings for how the application
    should load its user interface. Supports all three loading modes.
    """
    
    def __init__(self):
        """
        Initialize UI configuration with default settings.
        """
        self.mode = UILoadingMode.AUTO_DETECT  # Default to auto-detect
        self.ui_base_path: Optional[str] = None
    
    @classmethod
    def from_environment(cls) -> 'UIConfig':
        """
        Create configuration from environment variables.
        
        This method reads environment variables to configure the UI loading
        behavior, allowing users to override the default settings.
        
        Environment Variables:
            - BATTERY_SIM_UI_PATH: Custom path to .ui files
        
        Returns:
            UIConfig: Configured instance
        """
        config = cls()
        
        # Check custom UI path
        import os
        custom_path = os.environ.get("BATTERY_SIM_UI_PATH")
        if custom_path:
            config.ui_base_path = custom_path
            
        return config
    
    @classmethod
    def from_command_line(cls, args) -> 'UIConfig':
        """
        Create configuration from command line arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            UIConfig: Configured instance
        """
        config = cls()
        
        if hasattr(args, 'ui_path') and args.ui_path:
            config.ui_base_path = args.ui_path
            
        return config
    
    def should_load_ui_files(self) -> bool:
        """
        Determine if the application should try loading from .ui files.
        
        Returns:
            bool: True if .ui files should be used
        """
        return self.mode in (UILoadingMode.AUTO_DETECT, UILoadingMode.UI_FILES)
    
    def should_load_hand_coded(self) -> bool:
        """
        Determine if the application should use hand-coded widgets.
        
        Returns:
            bool: True if hand-coded widgets should be used
        """
        return self.mode in (UILoadingMode.AUTO_DETECT, UILoadingMode.HAND_CODED)
    
    def get_ui_base_path(self) -> Optional[str]:
        """
        Get the base path for .ui files.
        
        Returns:
            str or None: Base path if set, None for default
        """
        return self.ui_base_path
    
    def set_ui_base_path(self, path: Optional[str]):
        """
        Set the custom base path for .ui files.
        
        Args:
            path: Custom path or None for default
        """
        self.ui_base_path = path
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.
        
        Returns:
            dict: Configuration as dictionary
        """
        return {
            'mode': self.mode.value,
            'ui_base_path': self.ui_base_path
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'UIConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            UIConfig: Configured instance
        """
        config = cls()
        
        if 'mode' in config_dict:
            try:
                config.mode = UILoadingMode(config_dict['mode'])
            except ValueError:
                config.mode = UILoadingMode.AUTO_DETECT  # Default to auto-detect
        
        if 'ui_base_path' in config_dict:
            config.ui_base_path = config_dict['ui_base_path']
            
        return config
    
    def __str__(self) -> str:
        """
        String representation of the configuration.
        
        Returns:
            str: Human-readable configuration description
        """
        return (f"UIConfig(mode={self.mode.value}, "
                f"ui_base_path={self.ui_base_path})")
    
    def __repr__(self) -> str:
        """
        Detailed string representation of the configuration.
        
        Returns:
            str: Detailed configuration description
        """
        return self.__str__()
