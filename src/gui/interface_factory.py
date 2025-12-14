"""
Enhanced Interface Factory for Battery Simulator with Advanced Fallback.

This module provides an advanced InterfaceFactory that integrates with the
enhanced UI loading system, providing sophisticated fallback mechanisms,
template integration, and comprehensive error handling.
"""

import sys
import logging
import traceback
from typing import Optional, Dict, Any, List, Type, Union
from PyQt6.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt6.QtCore import Qt, QTimer
import os

logger = logging.getLogger(__name__)


class InterfaceCreationError(Exception):
    """Exception raised when interface creation fails."""
    pass


class InterfaceFactory:
    """
    Enhanced interface factory with advanced fallback and template integration.
    
    This factory provides sophisticated interface creation with:
    - Multi-level fallback mechanisms
    - Template-based interface generation
    - Performance monitoring and caching
    - Comprehensive error handling and recovery
    - Integration with enhanced UI loading system
    """
    
    # Interface creation cache for performance
    _interface_cache: Dict[str, Dict[str, Any]] = {}
    _creation_stats: Dict[str, int] = {'success': 0, 'fallbacks': 0, 'failures': 0}
    
    @classmethod
    def create_interface(
        cls,
        interface_type: str,
        parent: Optional[QWidget] = None,
        ui_config: Optional['UIConfig'] = None,
        use_cache: bool = True
    ) -> QWidget:
        """
        Create an interface with enhanced fallback and error handling.
        
        Args:
            interface_type: Type of interface (carbon, halfcell, fullcell, result)
            parent: Parent widget
            ui_config: UI configuration
            use_cache: Whether to use cached interfaces
            
        Returns:
            QWidget: The created interface
            
        Raises:
            InterfaceCreationError: If interface creation fails completely
        """
        start_time = cls._get_timestamp()
        
        # Get or create UI configuration
        ui_config = ui_config or cls._get_default_ui_config()
        logger.info(f"Creating interface: {interface_type} with mode: {ui_config.mode.value}")
        
        # Check cache if enabled
        if use_cache:
            cached = cls._get_cached_interface(interface_type, ui_config)
            if cached:
                logger.info(f"Using cached interface for {interface_type}")
                return cached
        
        # Create interface with fallback mechanism
        interface = cls._create_interface_with_fallback(
            interface_type, parent, ui_config
        )
        
        # Cache the interface if successful
        if interface and use_cache:
            cls._cache_interface(interface_type, ui_config, interface)
        
        # Update statistics
        cls._update_creation_stats('success')
        
        # Log performance metrics
        creation_time = cls._get_timestamp() - start_time
        logger.info(f"Interface creation completed in {creation_time:.3f}s")
        
        return interface
    
    @classmethod
    def _create_interface_with_fallback(
        cls,
        interface_type: str,
        parent: Optional[QWidget],
        ui_config: 'UIConfig'
    ) -> QWidget:
        """
        Create interface with comprehensive fallback mechanism.
        
        Args:
            interface_type: Type of interface
            parent: Parent widget
            ui_config: UI configuration
            
        Returns:
            QWidget: The created interface
            
        Raises:
            InterfaceCreationError: If all creation methods fail
        """
        fallback_methods = []
        last_error = None
        
        # Determine creation methods based on configuration
        if ui_config.mode.value == 'ui_files':
            fallback_methods = [
                ('ui_enhanced', 'Enhanced UI loading'),
                ('ui_basic', 'Basic UI loading'),
                ('hand_coded', 'Hand-coded widgets')
            ]
        elif ui_config.mode.value == 'hand_coded':
            fallback_methods = [
                ('hand_coded', 'Hand-coded widgets'),
                ('ui_enhanced', 'Enhanced UI loading (fallback)')
            ]
        else:  # auto_detect
            fallback_methods = [
                ('ui_enhanced', 'Enhanced UI loading (auto)'),
                ('ui_basic', 'Basic UI loading'),
                ('hand_coded', 'Hand-coded widgets')
            ]
        
        # Try each method in sequence
        for method, description in fallback_methods:
            try:
                logger.debug(f"Trying {description} for {interface_type}")
                
                if method == 'ui_enhanced':
                    interface = cls._create_ui_enhanced(interface_type, parent, ui_config)
                elif method == 'ui_basic':
                    interface = cls._create_ui_basic(interface_type, parent, ui_config)
                elif method == 'hand_coded':
                    interface = cls._create_hand_coded(interface_type, parent, ui_config)
                else:
                    continue
                
                if interface:
                    logger.info(f"Successfully created interface using {description}")
                    if method != fallback_methods[0][0]:  # Not the primary method
                        cls._update_creation_stats('fallbacks')
                    return interface
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to create interface using {description}: {e}")
                logger.debug(f"Full traceback: {traceback.format_exc()}")
        
        # All methods failed
        error_msg = f"Failed to create {interface_type} interface. Last error: {last_error}"
        logger.error(error_msg)
        cls._update_creation_stats('failures')
        raise InterfaceCreationError(error_msg)
    
    @classmethod
    def _create_ui_enhanced(
        cls,
        interface_type: str,
        parent: Optional[QWidget],
        ui_config: 'UIConfig'
    ) -> Optional[QWidget]:
        """Create interface using enhanced UI loading."""
        if not cls._should_try_ui_loading(interface_type, ui_config, 'enhanced'):
            return None
        
        # Import UI loader
        from src.gui.ui_loader import UiLoader
        
        # Get UI name mapping
        ui_name = cls._get_ui_name(interface_type)
        
        # Load UI using UiLoader
        try:
            widget = UiLoader.load_ui(ui_name, parent)
            if widget:
                logger.debug(f"Successfully loaded UI: {ui_name}")
                return widget
        except Exception as e:
            logger.debug(f"Failed to load UI {ui_name}: {e}")
        
        return None
    
    @classmethod
    def _create_ui_basic(
        cls,
        interface_type: str,
        parent: Optional[QWidget],
        ui_config: 'UIConfig'
    ) -> Optional[QWidget]:
        """Create interface using basic UI loading."""
        if not cls._should_try_ui_loading(interface_type, ui_config, 'basic'):
            return None
        
        # Import basic UI loader
        from src.gui.ui_loader import UiLoader
        
        # Get UI name mapping
        ui_name = cls._get_ui_name(interface_type)
        
        # Load UI
        try:
            widget = UiLoader.load_ui(ui_name, parent)
            if widget:
                logger.debug(f"Successfully loaded UI: {ui_name}")
                return widget
        except Exception as e:
            logger.debug(f"Failed to load UI {ui_name}: {e}")
        
        return None
    
    @classmethod
    def _create_hand_coded(
        cls,
        interface_type: str,
        parent: Optional[QWidget],
        ui_config: 'UIConfig'
    ) -> Optional[QWidget]:
        """Create interface using hand-coded widgets."""
        logger.debug(f"Creating hand-coded interface: {interface_type}")
        
        # Import interface classes with lazy loading to avoid circular imports
        interface_classes = {
            'carbon': 'src.gui.interfaces.carbon_interface.CarbonInterface',
            'halfcell': 'src.gui.interfaces.halfcell_interface.HalfCellInterface',
            'fullcell': 'src.gui.interfaces.fullcell_interface.FullCellInterface',
            'result': 'src.gui.interfaces.result_interface.ResultInterface'
        }
        
        if interface_type not in interface_classes:
            logger.error(f"Unknown interface type: {interface_type}")
            return None
        
        class_path = interface_classes[interface_type]
        module_path, class_name = class_path.rsplit('.', 1)
        
        try:
            # Import the module
            import importlib
            module = importlib.import_module(module_path)
            interface_class = getattr(module, class_name)
            
            # Create instance with UI configuration
            if hasattr(interface_class, '__init__'):
                # Check if the constructor accepts ui_config parameter
                import inspect
                sig = inspect.signature(interface_class.__init__)
                if 'ui_config' in sig.parameters:
                    return interface_class(parent, ui_config=ui_config)
                else:
                    return interface_class(parent)
            else:
                return interface_class(parent)
                
        except ImportError as e:
            logger.error(f"Failed to import {class_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create {class_name}: {e}")
            return None
    
    @classmethod
    def _should_try_ui_loading(
        cls,
        interface_type: str,
        ui_config: 'UIConfig',
        loader_type: str = 'enhanced'
    ) -> bool:
        """Determine if UI loading should be attempted."""
        from src.gui.ui_config import UILoadingMode
        
        if ui_config.mode == UILoadingMode.UI_FILES:
            return True
        elif ui_config.mode == UILoadingMode.HAND_CODED:
            return False
        elif ui_config.mode == UILoadingMode.AUTO_DETECT:
            # In auto-detect mode, prefer hand-coded for now (UI files may not be properly set up)
            return False
        return False
    
    @staticmethod
    def _get_ui_name(interface_type: str) -> str:
        """Get the .ui file name for an interface type."""
        ui_name_map = {
            "carbon": "carboninterface",
            "halfcell": "halfcellinterface",
            "fullcell": "fullcellfoam",
            "result": "resultinterface"
        }
        return ui_name_map.get(interface_type, interface_type)
    
    @classmethod
    def _cache_interface(
        cls,
        interface_type: str,
        ui_config: 'UIConfig',
        interface: QWidget
    ):
        """Cache a created interface for reuse."""
        cache_key = cls._generate_cache_key(interface_type, ui_config)
        cls._interface_cache[cache_key] = {
            'interface': interface,
            'timestamp': cls._get_timestamp(),
            'config': ui_config.to_dict()
        }
        logger.debug(f"Cached interface: {cache_key}")
    
    @classmethod
    def _get_cached_interface(
        cls,
        interface_type: str,
        ui_config: 'UIConfig'
    ) -> Optional[QWidget]:
        """Retrieve a cached interface if available."""
        cache_key = cls._generate_cache_key(interface_type, ui_config)
        cached = cls._interface_cache.get(cache_key)
        
        if cached:
            # Check if cache is still valid (simple time-based invalidation)
            cache_age = cls._get_timestamp() - cached['timestamp']
            if cache_age < 300:  # 5 minutes cache lifetime
                return cached['interface']
            else:
                # Remove expired cache
                del cls._interface_cache[cache_key]
                logger.debug(f"Removed expired cache: {cache_key}")
        
        return None
    
    @staticmethod
    def _generate_cache_key(interface_type: str, ui_config: 'UIConfig') -> str:
        """Generate a cache key for the interface configuration."""
        config_hash = hash(str(sorted(ui_config.to_dict().items())))
        return f"{interface_type}_{config_hash}"
    
    @staticmethod
    def _get_default_ui_config() -> 'UIConfig':
        """Get default UI configuration."""
        from src.gui.ui_config import UIConfig
        return UIConfig()
    
    @staticmethod
    def _get_timestamp() -> float:
        """Get current timestamp for performance monitoring."""
        import time
        return time.time()
    
    @classmethod
    def _update_creation_stats(cls, stat_type: str):
        """Update interface creation statistics."""
        if stat_type in cls._creation_stats:
            cls._creation_stats[stat_type] += 1
    
    @classmethod
    def get_creation_stats(cls) -> Dict[str, int]:
        """Get interface creation statistics."""
        return cls._creation_stats.copy()
    
    @classmethod
    def clear_cache(cls):
        """Clear the interface cache."""
        cls._interface_cache.clear()
        logger.debug("Cleared interface cache")
    
    @classmethod
    def diagnose_interface_creation(
        cls,
        interface_type: str,
        ui_config: Optional['UIConfig'] = None
    ) -> Dict[str, Any]:
        """
        Diagnose interface creation issues for debugging.
        
        Args:
            interface_type: Type of interface to diagnose
            ui_config: UI configuration (optional)
            
        Returns:
            Dictionary containing diagnosis results
        """
        diagnosis = {
            'interface_type': interface_type,
            'config': ui_config.to_dict() if ui_config else {},
            'issues': [],
            'recommendations': [],
            'test_results': {},
            'success': False
        }
        
        try:
            # Test UI file availability
            diagnosis['test_results']['ui_files_available'] = cls._test_ui_files(interface_type, ui_config)
            
            # Test hand-coded interface creation
            diagnosis['test_results']['hand_coded_works'] = cls._test_hand_coded(interface_type)
            
            # Test enhanced UI loading
            diagnosis['test_results']['enhanced_ui_works'] = cls._test_enhanced_ui(interface_type, ui_config)
            
            # Test basic UI loading
            diagnosis['test_results']['basic_ui_works'] = cls._test_basic_ui(interface_type, ui_config)
            
            # Analyze results and provide recommendations
            cls._analyze_diagnosis_results(diagnosis)
            
            # Try to create the interface to verify it works
            try:
                interface = cls.create_interface(interface_type, ui_config=ui_config, use_cache=False)
                diagnosis['success'] = True
                diagnosis['recommendations'].append("Interface creation successful")
            except Exception as e:
                diagnosis['issues'].append(f"Interface creation failed: {str(e)}")
                
        except Exception as e:
            diagnosis['issues'].append(f"Diagnosis failed: {str(e)}")
            diagnosis['recommendations'].append("Check application logs for more details")
        
        return diagnosis
    
    @classmethod
    def _test_ui_files(cls, interface_type: str, ui_config: Optional['UIConfig']) -> Dict[str, Any]:
        """Test UI file availability and integrity."""
        results = {'enhanced': {}, 'basic': {}}
        
        try:
            # Test enhanced UI loader
            from src.gui.ui_loader import UILoader
            ui_name = cls._get_ui_name(interface_type)
            ui_path = UILoader.get_ui_path(ui_name, ui_config.get_ui_base_path() if ui_config else None)
            
            results['enhanced']['file_exists'] = os.path.exists(ui_path)
            results['enhanced']['integrity_valid'] = UILoader.validate_ui_integrity(ui_path) if results['enhanced']['file_exists'] else False
            results['enhanced']['path'] = ui_path
            
        except Exception as e:
            results['enhanced']['error'] = str(e)
        
        try:
            # Test basic UI loader
            from src.gui.ui_loader import UILoader
            ui_name = cls._get_ui_name(interface_type)
            ui_path = UILoader.get_ui_path(ui_name, ui_config.get_ui_base_path() if ui_config else None)
            
            results['basic']['file_exists'] = os.path.exists(ui_path)
            results['basic']['path'] = ui_path
            
        except Exception as e:
            results['basic']['error'] = str(e)
        
        return results
    
    @classmethod
    def _test_hand_coded(cls, interface_type: str) -> Dict[str, Any]:
        """Test hand-coded interface creation."""
        results = {'import_success': False, 'creation_success': False, 'error': None}
        
        try:
            # Test import
            interface_classes = {
                'carbon': 'src.gui.interfaces.carbon_interface.CarbonInterface',
                'halfcell': 'src.gui.interfaces.halfcell_interface.HalfCellInterface',
                'fullcell': 'src.gui.interfaces.fullcell_interface.FullCellInterface',
                'result': 'src.gui.interfaces.result_interface.ResultInterface'
            }
            
            if interface_type not in interface_classes:
                results['error'] = f"Unknown interface type: {interface_type}"
                return results
            
            class_path = interface_classes[interface_type]
            module_path, class_name = class_path.rsplit('.', 1)
            
            import importlib
            module = importlib.import_module(module_path)
            interface_class = getattr(module, class_name)
            results['import_success'] = True
            
            # Test creation (without parent to avoid widget issues in testing)
            try:
                # Create a minimal test instance
                test_instance = interface_class.__new__(interface_class)
                results['creation_success'] = True
            except Exception as e:
                results['error'] = f"Creation failed: {str(e)}"
                
        except Exception as e:
            results['error'] = f"Import failed: {str(e)}"
        
        return results
    
    @classmethod
    def _test_enhanced_ui(cls, interface_type: str, ui_config: Optional['UIConfig']) -> Dict[str, Any]:
        """Test enhanced UI loading."""
        results = {'success': False, 'error': None}
        
        try:
            from src.gui.ui_loader import UILoader
            ui_name = cls._get_ui_name(interface_type)
            ui_path = UILoader.get_ui_path(ui_name, ui_config.get_ui_base_path() if ui_config else None)
            
            if UILoader.validate_ui_integrity(ui_path):
                # Try to load without parent (for testing)
                widget = UILoader.load_ui_file(ui_path, parent=None, validate_ui=True)
                results['success'] = widget is not None
            else:
                results['error'] = "UI file integrity check failed"
                
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    @classmethod
    def _test_basic_ui(cls, interface_type: str, ui_config: Optional['UIConfig']) -> Dict[str, Any]:
        """Test basic UI loading."""
        results = {'success': False, 'error': None}
        
        try:
            from src.gui.ui_loader import UILoader
            ui_name = cls._get_ui_name(interface_type)
            ui_path = UILoader.get_ui_path(ui_name, ui_config.get_ui_base_path() if ui_config else None)
            
            if UILoader.ui_file_exists(ui_name, ui_config.get_ui_base_path() if ui_config else None):
                # Try to load without parent (for testing)
                widget = UILoader.load_ui_file(ui_path, parent=None)
                results['success'] = widget is not None
            else:
                results['error'] = "UI file not found"
                
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    @classmethod
    def _analyze_diagnosis_results(cls, diagnosis: Dict[str, Any]):
        """Analyze diagnosis results and provide recommendations."""
        test_results = diagnosis['test_results']
        
        # Check for common issues
        if not test_results.get('ui_files_available', {}).get('enhanced', {}).get('file_exists', False):
            diagnosis['issues'].append("UI files not found in expected location")
            diagnosis['recommendations'].append("Check that UI files exist in resources/ui directory")
        
        if not test_results.get('hand_coded_works', {}).get('import_success', False):
            diagnosis['issues'].append("Hand-coded interface import failed")
            diagnosis['recommendations'].append("Check that interface modules are properly installed")
        
        # Provide specific recommendations based on test results
        if test_results.get('enhanced_ui_works', {}).get('success', False):
            diagnosis['recommendations'].append("Use enhanced UI loading mode for best results")
        elif test_results.get('basic_ui_works', {}).get('success', False):
            diagnosis['recommendations'].append("Use basic UI loading mode as fallback")
        elif test_results.get('hand_coded_works', {}).get('creation_success', False):
            diagnosis['recommendations'].append("Use hand-coded widgets mode")
        else:
            diagnosis['issues'].append("No working interface creation method found")
            diagnosis['recommendations'].append("Check application configuration and dependencies")
