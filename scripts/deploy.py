#!/usr/bin/env python3
"""
Deployment automation script for Battery Simulator.

This script handles the complete deployment process including:
- Environment validation
- Package building
- Installation
- Configuration
- Service setup
- Health checks
"""

import os
import sys
import json
import logging
import argparse
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import platform
import tempfile
import zipfile
import tarfile

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentConfig:
    """Deployment configuration management."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load deployment configuration."""
        default_config = {
            "application": {
                "name": "BatterySimulator",
                "version": "1.0.0",
                "python_version": "3.10"
            },
            "paths": {
                "install_dir": "/opt/batterysimulator",
                "data_dir": "/var/lib/batterysimulator",
                "log_dir": "/var/log/batterysimulator",
                "config_dir": "/etc/batterysimulator"
            },
            "dependencies": {
                "python": ["PyQt6>=6.5.2", "pyqtgraph>=0.13.4"],
                "system": ["openfoam"]
            },
            "services": {
                "enabled": True,
                "name": "batterysimulator"
            },
            "security": {
                "user": "batterysimulator",
                "group": "batterysimulator",
                "permissions": "755"
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                self._merge_config(default_config, user_config)
                
        return default_config
    
    def _merge_config(self, default: Dict, user: Dict):
        """Recursively merge user config with default config."""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value


class EnvironmentValidator:
    """Validate deployment environment."""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.platform = platform.system().lower()
        
    def validate_python(self) -> bool:
        """Validate Python installation."""
        logger.info("Validating Python environment...")
        
        # Check Python version
        required_version = self.config.config["application"]["python_version"]
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        if current_version < required_version:
            logger.error(f"Python {required_version} required, but {current_version} found")
            return False
            
        logger.info(f"Python version OK: {current_version}")
        return True
    
    def validate_dependencies(self) -> bool:
        """Validate system dependencies."""
        logger.info("Validating system dependencies...")
        
        dependencies = self.config.config["dependencies"]
        
        # Check Python packages
        for package in dependencies["python"]:
            try:
                package_name = package.split(">=")[0]
                __import__(package_name)
                logger.info(f"Python package OK: {package_name}")
            except ImportError:
                logger.error(f"Python package missing: {package_name}")
                return False
        
        # Check system packages (Unix-like systems only)
        if self.platform != "windows":
            for package in dependencies["system"]:
                result = subprocess.run(
                    ["which", package], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode != 0:
                    logger.error(f"System package missing: {package}")
                    return False
                logger.info(f"System package OK: {package}")
        
        return True
    
    def validate_permissions(self) -> bool:
        """Validate file system permissions."""
        logger.info("Validating file system permissions...")
        
        paths = self.config.config["paths"]
        
        for path_name, path_value in paths.items():
            if path_name.endswith("_dir"):
                try:
                    os.makedirs(path_value, exist_ok=True)
                    # Test write permissions
                    test_file = os.path.join(path_value, ".test_write")
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    logger.info(f"Permissions OK: {path_value}")
                except PermissionError:
                    logger.error(f"Permission denied: {path_value}")
                    return False
                except Exception as e:
                    logger.error(f"Error accessing {path_value}: {e}")
                    return False
        
        return True
    
    def validate_openfoam(self) -> bool:
        """Validate OpenFOAM installation."""
        logger.info("Validating OpenFOAM installation...")
        
        if self.platform == "windows":
            # On Windows, check for OpenFOAM environment variables
            openfoam_vars = ["WM_PROJECT_DIR", "FOAM_INST_DIR"]
            for var in openfoam_vars:
                if var in os.environ:
                    logger.info(f"OpenFOAM environment variable OK: {var}")
                else:
                    logger.warning(f"OpenFOAM environment variable missing: {var}")
            return True
        
        # On Unix-like systems, check for icoFoam command
        result = subprocess.run(
            ["which", "icoFoam"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            logger.info("OpenFOAM installation OK")
            return True
        else:
            logger.warning("OpenFOAM not found in PATH")
            return False


class PackageBuilder:
    """Build deployment packages."""
    
    def __init__(self, config: DeploymentConfig, source_dir: str):
        self.config = config
        self.source_dir = Path(source_dir)
        self.build_dir = self.source_dir / "build"
        self.dist_dir = self.source_dir / "dist"
        
    def build_wheel(self) -> Optional[Path]:
        """Build Python wheel package."""
        logger.info("Building Python wheel package...")
        
        try:
            # Create build directories
            self.build_dir.mkdir(exist_ok=True)
            self.dist_dir.mkdir(exist_ok=True)
            
            # Run build command
            subprocess.run(
                [sys.executable, "-m", "build", "--wheel"],
                cwd=self.source_dir,
                check=True,
                capture_output=True
            )
            
            # Find the built wheel
            wheel_files = list(self.dist_dir.glob("*.whl"))
            if wheel_files:
                logger.info(f"Wheel built successfully: {wheel_files[0]}")
                return wheel_files[0]
            else:
                logger.error("No wheel file found after build")
                return None
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Wheel build failed: {e}")
            return None
    
    def build_executable(self) -> Optional[Path]:
        """Build standalone executable using PyInstaller."""
        logger.info("Building standalone executable...")
        
        try:
            # Install PyInstaller if not present
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pyinstaller"],
                check=True,
                capture_output=True
            )
            
            # Create PyInstaller spec
            spec_content = self._generate_pyinstaller_spec()
            spec_file = self.build_dir / "BatterySimulator.spec"
            with open(spec_file, 'w') as f:
                f.write(spec_content)
            
            # Build executable
            subprocess.run(
                [sys.executable, "-m", "PyInstaller", str(spec_file)],
                cwd=self.source_dir,
                check=True,
                capture_output=True
            )
            
            # Find the built executable
            dist_executable = self.build_dir / "dist" / "BatterySimulator"
            if dist_executable.exists():
                logger.info(f"Executable built successfully: {dist_executable}")
                return dist_executable
            else:
                logger.error("No executable found after build")
                return None
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Executable build failed: {e}")
            return None
    
    def _generate_pyinstaller_spec(self) -> str:
        """Generate PyInstaller spec file."""
        return """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/resources/', 'resources/'),
        ('src/gui/interfaces/', 'gui/interfaces/'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BatterySimulator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/resources/icons/batterysimulator.ico'
)
"""
    
    def create_docker_image(self) -> bool:
        """Create Docker image."""
        logger.info("Creating Docker image...")
        
        try:
            # Build Docker image
            subprocess.run(
                ["docker", "build", "-t", "batterysimulator:latest", "."],
                cwd=self.source_dir,
                check=True,
                capture_output=True
            )
            
            logger.info("Docker image created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker build failed: {e}")
            return False


class Installer:
    """Install the application."""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.platform = platform.system().lower()
        
    def install_package(self, package_path: Path) -> bool:
        """Install Python package."""
        logger.info(f"Installing package: {package_path}")
        
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", str(package_path)],
                check=True,
                capture_output=True
            )
            logger.info("Package installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Package installation failed: {e}")
            return False
    
    def install_executable(self, executable_path: Path, target_dir: Path) -> bool:
        """Install standalone executable."""
        logger.info(f"Installing executable: {executable_path}")
        
        try:
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy executable
            target_executable = target_dir / "BatterySimulator"
            shutil.copy2(executable_path, target_executable)
            
            # Make executable (Unix-like systems)
            if self.platform != "windows":
                os.chmod(target_executable, 0o755)
            
            logger.info(f"Executable installed to: {target_executable}")
            return True
            
        except Exception as e:
            logger.error(f"Executable installation failed: {e}")
            return False
    
    def create_desktop_entry(self) -> bool:
        """Create desktop entry (Unix-like systems)."""
        if self.platform == "windows":
            return True  # Windows uses different mechanism
            
        logger.info("Creating desktop entry...")
        
        try:
            desktop_entry = self._generate_desktop_entry()
            desktop_dir = Path.home() / ".local" / "share" / "applications"
            desktop_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_file = desktop_dir / "batterysimulator.desktop"
            with open(desktop_file, 'w') as f:
                f.write(desktop_entry)
            
            os.chmod(desktop_file, 0o644)
            logger.info("Desktop entry created")
            return True
            
        except Exception as e:
            logger.error(f"Desktop entry creation failed: {e}")
            return False
    
    def _generate_desktop_entry(self) -> str:
        """Generate desktop entry content."""
        config = self.config.config
        install_dir = config["paths"]["install_dir"]
        
        return f"""[Desktop Entry]
Version={config["application"]["version"]}
Type=Application
Name={config["application"]["name"]}
Comment=Battery Simulator Application
Exec={install_dir}/BatterySimulator
Icon={install_dir}/resources/icons/batterysimulator.png
Terminal=false
Categories=Application;Science;Engineering;
"""
    
    def setup_service(self) -> bool:
        """Set up system service."""
        if not self.config.config["services"]["enabled"]:
            logger.info("Service setup disabled in configuration")
            return True
            
        if self.platform == "windows":
            return self._setup_windows_service()
        else:
            return self._setup_unix_service()
    
    def _setup_windows_service(self) -> bool:
        """Set up Windows service."""
        logger.info("Setting up Windows service...")
        
        try:
            # This would require additional tools like nssm
            # For now, just log the requirement
            logger.info("Windows service setup requires nssm or similar tool")
            logger.info("Manual setup instructions:")
            logger.info("1. Download nssm from https://nssm.cc/")
            logger.info("2. Run: nssm install BatterySimulator")
            logger.info("3. Set application path and parameters")
            return True
            
        except Exception as e:
            logger.error(f"Windows service setup failed: {e}")
            return False
    
    def _setup_unix_service(self) -> bool:
        """Set up Unix-like system service."""
        logger.info("Setting up system service...")
        
        try:
            config = self.config.config
            install_dir = config["paths"]["install_dir"]
            service_name = config["services"]["name"]
            
            service_content = f"""[Unit]
Description=Battery Simulator Service
After=network.target

[Service]
Type=simple
User={config["security"]["user"]}
Group={config["security"]["group"]}
ExecStart={install_dir}/BatterySimulator
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
            
            service_file = f"/etc/systemd/system/{service_name}.service"
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            # Reload systemd and enable service
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            subprocess.run(["systemctl", "enable", service_name], check=True)
            
            logger.info(f"Service {service_name} created and enabled")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Service setup failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Service file creation failed: {e}")
            return False


class HealthChecker:
    """Perform health checks on deployed application."""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        
    def check_application(self) -> bool:
        """Check if application can be imported and started."""
        logger.info("Checking application health...")
        
        try:
            # Test import
            import src.main
            logger.info("Application import successful")
            
            # Test basic functionality
            from src.core.constants import APP_NAME, APP_VERSION
            logger.info(f"Application constants: {APP_NAME} v{APP_VERSION}")
            
            return True
            
        except ImportError as e:
            logger.error(f"Application import failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Application health check failed: {e}")
            return False
    
    def check_dependencies(self) -> bool:
        """Check if all dependencies are available."""
        logger.info("Checking dependencies...")
        
        try:
            # Test PyQt6
            import PyQt6
            logger.info(f"PyQt6 version: {PyQt6.QtCore.PYQT_VERSION_STR}")
            
            # Test pyqtgraph
            import pyqtgraph
            logger.info(f"pyqtgraph version: {pyqtgraph.__version__}")
            
            return True
            
        except ImportError as e:
            logger.error(f"Dependency check failed: {e}")
            return False
    
    def check_openfoam_integration(self) -> bool:
        """Check OpenFOAM integration."""
        logger.info("Checking OpenFOAM integration...")
        
        try:
            from src.openfoam.process_controller import ProcessController
            from src.openfoam.solver_manager import OpenFOAMSolverManager
            
            # Test ProcessController
            controller = ProcessController()
            logger.info("ProcessController initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"OpenFOAM integration check failed: {e}")
            return False


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy Battery Simulator")
    parser.add_argument("--config", help="Deployment configuration file")
    parser.add_argument("--source", default=".", help="Source directory")
    parser.add_argument("--target", help="Target installation directory")
    parser.add_argument("--mode", choices=["wheel", "executable", "docker"], 
                       default="wheel", help="Deployment mode")
    parser.add_argument("--validate-only", action="store_true", 
                       help="Only run validation, don't deploy")
    
    args = parser.parse_args()
    
    # Load configuration
    config = DeploymentConfig(args.config)
    
    # Validate environment
    validator = EnvironmentValidator(config)
    
    validation_checks = [
        validator.validate_python,
        validator.validate_dependencies,
        validator.validate_permissions,
        validator.validate_openfoam
    ]
    
    logger.info("Running environment validation...")
    for check in validation_checks:
        if not check():
            logger.error("Environment validation failed")
            sys.exit(1)
    
    if args.validate_only:
        logger.info("Validation completed successfully")
        sys.exit(0)
    
    # Build package
    builder = PackageBuilder(config, args.source)
    
    if args.mode == "wheel":
        package_path = builder.build_wheel()
    elif args.mode == "executable":
        package_path = builder.build_executable()
    elif args.mode == "docker":
        success = builder.create_docker_image()
        if success:
            logger.info("Docker deployment completed")
        else:
            logger.error("Docker deployment failed")
            sys.exit(1)
        return
    else:
        logger.error(f"Unknown deployment mode: {args.mode}")
        sys.exit(1)
    
    if not package_path:
        logger.error("Package build failed")
        sys.exit(1)
    
    # Install package
    installer = Installer(config)
    
    if args.mode == "wheel":
        success = installer.install_package(package_path)
    else:
        target_dir = Path(args.target) if args.target else Path(config.config["paths"]["install_dir"])
        success = installer.install_executable(package_path, target_dir)
    
    if not success:
        logger.error("Installation failed")
        sys.exit(1)
    
    # Set up additional components
    installer.create_desktop_entry()
    installer.setup_service()
    
    # Run health checks
    health_checker = HealthChecker(config)
    
    health_checks = [
        health_checker.check_application,
        health_checker.check_dependencies,
        health_checker.check_openfoam_integration
    ]
    
    logger.info("Running health checks...")
    for check in health_checks:
        if not check():
            logger.error("Health check failed")
            sys.exit(1)
    
    logger.info("Deployment completed successfully!")


if __name__ == "__main__":
    main()