"""
UI Configuration for Battery Simulator.

This module provides configuration classes for UI loading modes,
allowing users to choose between .ui file loading and hand-coded
widget approaches.
"""

from enum import Enum
from typing import Optional


class UILoadingMode(Enum):
    """
    UI loading modes for the Battery Simulator.
    
    Defines different ways the application can load its user interface:
    - UI_FILES: Load from Qt Designer .ui files at runtime
    - HAND_CODED: Use hand-coded PyQt6 widgets
    - AUTO_DETECT: Automatically choose based on file availability
    """
    UI_FILES = "ui_files"           # Load from .ui files
    HAND_CODED = "hand_coded"       # Use hand-coded widgets
    AUTO_DETECT = "auto_detect"     # Auto-detect based on availability


class UIConfig:
    """
    Configuration for UI loading behavior.
    
    This class manages the configuration settings for how the application
    should load its user interface, including fallback options and
    environment-based configuration.
    """
    
    def __init__(self):
        """
        Initialize UI configuration with default settings.
        """
        self.mode = UILoadingMode.AUTO_DETECT
        self.prefer_ui_files = True
        self.fallback_to_hand_coded = True
        self.ui_base_path: Optional[str] = None
    
    @classmethod
    def from_environment(cls) -> 'UIConfig':
        """
        Create configuration from environment variables.
        
        This method reads environment variables to configure the UI loading
        behavior, allowing users to override the default settings.
        
        Environment Variables:
            - BATTERY_SIM_UI_MODE: ui_files, hand_coded, or auto
            - BATTERY_SIM_UI_PATH: Custom path to .ui files
        
        Returns:
            UIConfig: Configured instance
        """
        config = cls()
        
        # Check UI mode environment variable
        import os
        ui_mode = os.environ.get("BATTERY_SIM_UI_MODE", "").lower()
        
        if ui_mode == "ui_files":
            config.mode = UILoadingMode.UI_FILES
        elif ui_mode == "hand_coded":
            config.mode = UILoadingMode.HAND_CODED
        elif ui_mode == "auto":
            config.mode = UILoadingMode.AUTO_DETECT
        # Default remains AUTO_DETECT
        
        # Check custom UI path
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
        
        if hasattr(args, 'ui_mode') and args.ui_mode:
            if args.ui_mode == "ui_files":
                config.mode = UILoadingMode.UI_FILES
            elif args.ui_mode == "hand_coded":
                config.mode = UILoadingMode.HAND_CODED
            elif args.ui_mode == "auto":
                config.mode = UILoadingMode.AUTO_DETECT
        
        if hasattr(args, 'ui_path') and args.ui_path:
            config.ui_base_path = args.ui_path
            
        return config
    
    def should_load_ui_files(self) -> bool:
        """
        Determine if the application should try loading from .ui files.
        
        Returns:
            bool: True if .ui files should be used
        """
        if self.mode == UILoadingMode.UI_FILES:
            return True
        elif self.mode == UILoadingMode.HAND_CODED:
            return False
        elif self.mode == UILoadingMode.AUTO_DETECT:
            # In auto-detect mode, prefer .ui files if available
            return self.prefer_ui_files
        return False
    
    def should_fallback_to_hand_coded(self) -> bool:
        """
        Determine if the application should fallback to hand-coded widgets.
        
        Returns:
            bool: True if fallback is allowed
        """
        return self.fallback_to_hand_coded
    
    def get_ui_base_path(self) -> Optional[str]:
        """
        Get the base path for .ui files.
        
        Returns:
            str or None: Base path if set, None for default
        """
        return self.ui_base_path
    
    def set_mode(self, mode: UILoadingMode):
        """
        Set the UI loading mode.
        
        Args:
            mode: The loading mode to use
        """
        self.mode = mode
    
    def set_prefer_ui_files(self, prefer: bool):
        """
        Set whether to prefer .ui files in auto-detect mode.
        
        Args:
            prefer: True to prefer .ui files, False to prefer hand-coded
        """
        self.prefer_ui_files = prefer
    
    def set_fallback_enabled(self, enabled: bool):
        """
        Set whether fallback to hand-coded widgets is enabled.
        
        Args:
            enabled: True to enable fallback, False to disable
        """
        self.fallback_to_hand_coded = enabled
    
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
            'prefer_ui_files': self.prefer_ui_files,
            'fallback_to_hand_coded': self.fallback_to_hand_coded,
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
                config.mode = UILoadingMode.AUTO_DETECT
        
        if 'prefer_ui_files' in config_dict:
            config.prefer_ui_files = bool(config_dict['prefer_ui_files'])
        
        if 'fallback_to_hand_coded' in config_dict:
            config.fallback_to_hand_coded = bool(config_dict['fallback_to_hand_coded'])
        
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
                f"prefer_ui_files={self.prefer_ui_files}, "
                f"fallback_enabled={self.fallback_to_hand_coded}, "
                f"ui_base_path={self.ui_base_path})")
    
    def __repr__(self) -> str:
        """
        Detailed string representation of the configuration.
        
        Returns:
            str: Detailed configuration description
        """
        return self.__str__()
