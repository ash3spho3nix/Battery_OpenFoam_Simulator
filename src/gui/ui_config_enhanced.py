"""
Enhanced UI Configuration for Battery Simulator - Complete Configuration Management.

This module provides an enhanced configuration system that supports:
- Multiple configuration sources with priority ordering
- Environment variable support
- Command-line argument parsing
- Configuration validation and normalization
- Runtime configuration updates
- Comprehensive logging and error handling
"""

import os
import sys
import logging
import argparse
from enum import Enum
from typing import Optional, Dict, Any, Union, List
from dataclasses import dataclass, asdict
import json
import yaml
from pathlib import Path
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


class FallbackStrategy(Enum):
    """
    Fallback strategies for UI loading failures.
    
    Defines how the application should handle UI loading failures:
    - GRACEFUL: Show user notification and continue
    - STRICT: Raise exception on any failure
    - SILENT: Use fallback without notification
    """
    GRACEFUL = "graceful"   # Show notification and continue
    STRICT = "strict"       # Raise exception on failure
    SILENT = "silent"       # Silent fallback


@dataclass
class UIConfigSettings:
    """
    Configuration settings data structure.
    
    Contains all configuration parameters with proper typing and defaults.
    """
    # Core settings
    mode: UILoadingMode = UILoadingMode.AUTO_DETECT
    fallback_enabled: bool = True
    fallback_strategy: FallbackStrategy = FallbackStrategy.GRACEFUL
    
    # Path settings
    ui_base_path: Optional[str] = None
    custom_template_path: Optional[str] = None
    
    # Performance settings
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes
    
    # Validation settings
    validate_ui_files: bool = True
    validate_widgets: bool = True
    
    # Logging settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Advanced settings
    max_retries: int = 3
    timeout_seconds: int = 30
    enable_profiling: bool = False


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass


class ConfigurationValidationError(ConfigurationError):
    """Custom exception for configuration validation errors."""
    pass


class EnhancedUIConfig:
    """
    Enhanced configuration manager for UI loading.
    
    This class provides comprehensive configuration management with support for:
    - Multiple configuration sources (environment, CLI, defaults)
    - Configuration validation and normalization
    - Runtime configuration updates
    - Configuration persistence
    - Detailed logging and error reporting
    
    Configuration Priority (highest to lowest):
    1. Command-line arguments
    2. Environment variables
    3. Configuration file
    4. Default values
    """
    
    # Environment variable prefixes
    ENV_PREFIX = "BATTERY_SIM_"
    UI_ENV_PREFIX = f"{ENV_PREFIX}UI_"
    
    # Environment variable mappings
    ENV_VAR_MAPPINGS = {
        f"{UI_ENV_PREFIX}MODE": "mode",
        f"{UI_ENV_PREFIX}PATH": "ui_base_path",
        f"{UI_ENV_PREFIX}NO_FALLBACK": "fallback_enabled",
        f"{UI_ENV_PREFIX}FALLBACK_STRATEGY": "fallback_strategy",
        f"{UI_ENV_PREFIX}VALIDATE": "validate_ui_files",
        f"{UI_ENV_PREFIX}CACHE": "cache_enabled",
        f"{UI_ENV_PREFIX}LOG_LEVEL": "log_level",
        f"{UI_ENV_PREFIX}LOG_FILE": "log_file"
    }
    
    # Valid mode values
    VALID_MODES = [mode.value for mode in UILoadingMode]
    VALID_STRATEGIES = [strategy.value for strategy in FallbackStrategy]
    
    def __init__(self, settings: Optional[UIConfigSettings] = None):
        """
        Initialize enhanced UI configuration.
        
        Args:
            settings: Optional initial settings
        """
        self.logger = self._setup_logger()
        self.settings = settings or UIConfigSettings()
        self.source_priority = []
        
        self.logger.info("Initializing EnhancedUIConfig")
        
    def _setup_logger(self) -> logging.Logger:
        """Setup configuration logger."""
        logger = logging.getLogger(f"{__name__}.EnhancedUIConfig")
        if not logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)
            
            # File handler for configuration logs
            log_dir = Path(__file__).parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / "ui_config.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
            logger.setLevel(logging.DEBUG)
        
        return logger
    
    @classmethod
    def from_environment(cls) -> 'EnhancedUIConfig':
        """
        Create configuration from environment variables.
        
        Environment Variables:
            - BATTERY_SIM_UI_MODE: Loading mode (auto_detect, ui_files, hand_coded)
            - BATTERY_SIM_UI_PATH: Custom path to .ui files
            - BATTERY_SIM_UI_NO_FALLBACK: Disable fallback (true/false)
            - BATTERY_SIM_UI_FALLBACK_STRATEGY: Fallback strategy
            - BATTERY_SIM_UI_VALIDATE: Enable validation (true/false)
            - BATTERY_SIM_UI_CACHE: Enable caching (true/false)
            - BATTERY_SIM_UI_LOG_LEVEL: Log level (DEBUG, INFO, WARNING, ERROR)
            - BATTERY_SIM_UI_LOG_FILE: Custom log file path
        
        Returns:
            EnhancedUIConfig: Configured instance
        """
        config = cls()
        config.source_priority.append("environment")
        
        try:
            # Read environment variables
            env_values = {}
            for env_var, setting_name in cls.ENV_VAR_MAPPINGS.items():
                value = os.environ.get(env_var)
                if value:
                    env_values[setting_name] = value
                    config.logger.debug(f"Found environment variable: {env_var} = {value}")
            
            # Apply environment values
            config._apply_settings(env_values, "environment")
            
        except Exception as e:
            config.logger.error(f"Error reading environment variables: {e}")
            raise ConfigurationError(f"Environment variable error: {e}")
        
        return config
    
    @classmethod
    def from_command_line(cls, args: Optional[List[str]] = None) -> 'EnhancedUIConfig':
        """
        Create configuration from command line arguments.
        
        Args:
            args: Command line arguments (defaults to sys.argv)
            
        Returns:
            EnhancedUIConfig: Configured instance
        """
        config = cls()
        config.source_priority.append("command_line")
        
        try:
            # Parse command line arguments
            parsed_args = config._parse_command_line(args)
            
            # Apply command line values
            cli_values = {k: v for k, v in vars(parsed_args).items() if v is not None}
            config._apply_settings(cli_values, "command_line")
            
        except Exception as e:
            config.logger.error(f"Error parsing command line arguments: {e}")
            raise ConfigurationError(f"Command line argument error: {e}")
        
        return config
    
    @classmethod
    def from_file(cls, config_file: str) -> 'EnhancedUIConfig':
        """
        Create configuration from a configuration file.
        
        Supported formats: JSON, YAML
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            EnhancedUIConfig: Configured instance
        """
        config = cls()
        config.source_priority.append("file")
        
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise ConfigurationError(f"Configuration file not found: {config_file}")
            
            # Read configuration file
            if config_path.suffix.lower() in ['.json', '.js']:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
            elif config_path.suffix.lower() in ['.yaml', '.yml']:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_data = yaml.safe_load(f)
            else:
                raise ConfigurationError(f"Unsupported configuration file format: {config_path.suffix}")
            
            # Apply file values
            config._apply_settings(file_data, "file")
            config.logger.info(f"Loaded configuration from file: {config_file}")
            
        except Exception as e:
            config.logger.error(f"Error reading configuration file {config_file}: {e}")
            raise ConfigurationError(f"Configuration file error: {e}")
        
        return config
    
    @classmethod
    def from_multiple_sources(
        cls,
        config_file: Optional[str] = None,
        args: Optional[List[str]] = None
    ) -> 'EnhancedUIConfig':
        """
        Create configuration from multiple sources with proper priority.
        
        Priority order (highest to lowest):
        1. Command-line arguments
        2. Environment variables
        3. Configuration file
        4. Default values
        
        Args:
            config_file: Optional configuration file path
            args: Optional command line arguments
            
        Returns:
            EnhancedUIConfig: Configured instance with merged settings
        """
        # Start with defaults
        config = cls()
        config.source_priority.append("defaults")
        
        # Load from file (lowest priority)
        if config_file:
            try:
                file_config = cls.from_file(config_file)
                config._merge_settings(file_config.settings, "file")
                config.source_priority.append("file")
            except ConfigurationError as e:
                config.logger.warning(f"Failed to load configuration file: {e}")
        
        # Load from environment (medium priority)
        try:
            env_config = cls.from_environment()
            config._merge_settings(env_config.settings, "environment")
            config.source_priority.append("environment")
        except ConfigurationError as e:
            config.logger.warning(f"Failed to load environment variables: {e}")
        
        # Load from command line (highest priority)
        try:
            cli_config = cls.from_command_line(args)
            config._merge_settings(cli_config.settings, "command_line")
            config.source_priority.append("command_line")
        except ConfigurationError as e:
            config.logger.warning(f"Failed to parse command line arguments: {e}")
        
        # Validate final configuration
        config._validate_configuration()
        
        return config
    
    def _parse_command_line(self, args: Optional[List[str]]) -> argparse.Namespace:
        """
        Parse command line arguments.
        
        Args:
            args: Command line arguments
            
        Returns:
            argparse.Namespace: Parsed arguments
        """
        parser = argparse.ArgumentParser(
            description="Battery Simulator UI Configuration",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  --ui-mode auto_detect
  --ui-path /custom/ui/path
  --no-fallback
  --fallback-strategy strict
  --log-level DEBUG
            """
        )
        
        # UI loading mode
        parser.add_argument(
            '--ui-mode',
            choices=self.VALID_MODES,
            help='UI loading mode (auto_detect, ui_files, hand_coded)'
        )
        
        # UI path
        parser.add_argument(
            '--ui-path',
            help='Custom path to .ui files'
        )
        
        # Fallback options
        parser.add_argument(
            '--no-fallback',
            action='store_true',
            help='Disable fallback to hand-coded widgets'
        )
        
        parser.add_argument(
            '--fallback-strategy',
            choices=self.VALID_STRATEGIES,
            help='Fallback strategy (graceful, strict, silent)'
        )
        
        # Validation options
        parser.add_argument(
            '--no-validate',
            action='store_true',
            help='Disable UI file validation'
        )
        
        # Caching options
        parser.add_argument(
            '--no-cache',
            action='store_true',
            help='Disable UI caching'
        )
        
        # Logging options
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            help='Logging level'
        )
        
        parser.add_argument(
            '--log-file',
            help='Custom log file path'
        )
        
        # Performance options
        parser.add_argument(
            '--max-retries',
            type=int,
            help='Maximum retry attempts for UI loading'
        )
        
        parser.add_argument(
            '--timeout',
            type=int,
            help='Timeout in seconds for UI operations'
        )
        
        # Advanced options
        parser.add_argument(
            '--enable-profiling',
            action='store_true',
            help='Enable performance profiling'
        )
        
        return parser.parse_args(args)
    
    def _apply_settings(self, settings_dict: Dict[str, Any], source: str):
        """
        Apply settings from a dictionary.
        
        Args:
            settings_dict: Dictionary of settings
            source: Source of the settings (for logging)
        """
        for key, value in settings_dict.items():
            if hasattr(self.settings, key):
                try:
                    converted_value = self._convert_setting(key, value)
                    setattr(self.settings, key, converted_value)
                    self.logger.debug(f"Set {key} from {source}: {converted_value}")
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Invalid value for {key} from {source}: {value} - {e}")
            else:
                self.logger.warning(f"Unknown setting: {key} from {source}")
    
    def _convert_setting(self, key: str, value: Any) -> Any:
        """
        Convert setting value to appropriate type.
        
        Args:
            key: Setting name
            value: Raw value
            
        Returns:
            Converted value
        """
        # Handle boolean conversions
        if key in ['fallback_enabled', 'cache_enabled', 'validate_ui_files', 
                  'validate_widgets', 'enable_profiling', 'no_fallback', 'no_validate', 'no_cache']:
            if isinstance(value, str):
                return value.lower() in ['true', '1', 'yes', 'on']
            return bool(value)
        
        # Handle enum conversions
        if key == 'mode':
            return UILoadingMode(value)
        elif key == 'fallback_strategy':
            return FallbackStrategy(value)
        
        # Handle numeric conversions
        if key in ['cache_ttl', 'max_retries', 'timeout_seconds']:
            return int(value)
        
        # String values (including None)
        return str(value) if value is not None else None
    
    def _merge_settings(self, other_settings: UIConfigSettings, source: str):
        """
        Merge settings from another configuration.
        
        Args:
            other_settings: Settings to merge
            source: Source of the settings
        """
        for field in other_settings.__dataclass_fields__:
            value = getattr(other_settings, field)
            if value is not None:
                setattr(self.settings, field, value)
                self.logger.debug(f"Merged {field} from {source}: {value}")
    
    def _validate_configuration(self):
        """Validate the final configuration."""
        errors = []
        
        # Validate mode
        if self.settings.mode not in UILoadingMode:
            errors.append(f"Invalid mode: {self.settings.mode}")
        
        # Validate fallback strategy
        if self.settings.fallback_strategy not in FallbackStrategy:
            errors.append(f"Invalid fallback strategy: {self.settings.fallback_strategy}")
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.settings.log_level not in valid_log_levels:
            errors.append(f"Invalid log level: {self.settings.log_level}")
        
        # Validate numeric values
        if self.settings.max_retries < 0:
            errors.append(f"Invalid max_retries: {self.settings.max_retries}")
        
        if self.settings.timeout_seconds < 0:
            errors.append(f"Invalid timeout_seconds: {self.settings.timeout_seconds}")
        
        if self.settings.cache_ttl < 0:
            errors.append(f"Invalid cache_ttl: {self.settings.cache_ttl}")
        
        # Check for conflicting settings
        if self.settings.mode == UILoadingMode.HAND_CODED and self.settings.fallback_enabled:
            self.logger.warning("HAND_CODED mode with fallback enabled - fallback will have no effect")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(errors)
            self.logger.error(error_msg)
            raise ConfigurationValidationError(error_msg)
        
        self.logger.info("Configuration validation passed")
    
    def update_setting(self, key: str, value: Any, source: str = "runtime"):
        """
        Update a configuration setting at runtime.
        
        Args:
            key: Setting name
            value: New value
            source: Source of the update (for logging)
        """
        if not hasattr(self.settings, key):
            raise ConfigurationError(f"Unknown setting: {key}")
        
        try:
            converted_value = self._convert_setting(key, value)
            setattr(self.settings, key, converted_value)
            self.logger.info(f"Updated {key} from {source}: {converted_value}")
            
            # Re-validate configuration
            self._validate_configuration()
            
        except (ValueError, TypeError) as e:
            self.logger.error(f"Failed to update {key}: {e}")
            raise ConfigurationError(f"Invalid value for {key}: {e}")
    
    def get_setting(self, key: str) -> Any:
        """Get a configuration setting value."""
        if not hasattr(self.settings, key):
            raise ConfigurationError(f"Unknown setting: {key}")
        return getattr(self.settings, key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self.settings)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def save_to_file(self, file_path: str, format: str = 'json'):
        """
        Save configuration to file.
        
        Args:
            file_path: Path to save file
            format: Format ('json' or 'yaml')
        """
        config_data = self.to_dict()
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, default=str)
        elif format.lower() in ['yaml', 'yml']:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False)
        else:
            raise ConfigurationError(f"Unsupported format: {format}")
        
        self.logger.info(f"Configuration saved to {file_path}")
    
    def get_source_priority(self) -> List[str]:
        """Get the priority order of configuration sources."""
        return self.source_priority.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            'mode': self.settings.mode.value,
            'fallback_enabled': self.settings.fallback_enabled,
            'fallback_strategy': self.settings.fallback_strategy.value,
            'ui_base_path': self.settings.ui_base_path,
            'cache_enabled': self.settings.cache_enabled,
            'validate_ui_files': self.settings.validate_ui_files,
            'log_level': self.settings.log_level,
            'source_priority': self.source_priority
#            'settings_count': len([f for f in self.settings.__dataclass_fields__ if #getattr(self.settings, f.name) is not None])
        }
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"EnhancedUIConfig(mode={self.settings.mode.value}, fallback={self.settings.fallback_enabled}, path={self.settings.ui_base_path})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()


def main():
    """Test the enhanced UI configuration."""
    print("Testing EnhancedUIConfig...")
    
    # Test from multiple sources
    try:
        config = EnhancedUIConfig.from_multiple_sources()
        print(f"Configuration loaded: {config}")
        print(f"Summary: {config.get_summary()}")
        
        # Test runtime updates
        config.update_setting('log_level', 'DEBUG')
        print(f"Updated log level: {config.get_setting('log_level')}")
        
        # Test saving configuration
        config.save_to_file("test_config.json")
        print("Configuration saved to test_config.json")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()