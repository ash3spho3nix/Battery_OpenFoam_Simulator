#!/usr/bin/env python3
"""
Standalone CLI Interface for Battery OpenFoam Simulator.

This script provides a command-line interface to run battery simulations
without the GUI, using the same core functions as the main application.

Usage:
    python main_standalone.py [options]

Examples:
    python main_standalone.py --simulation spm --project test_project
    python main_standalone.py --simulation halfcell --project hc_test --config config.json
"""

import sys
import os
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add src directory to Python path
current_dir = Path(__file__).parent  # This is src/
parent_dir = current_dir.parent     # This is the project root
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from src.core.project_manager import ProjectManager
from src.openfoam.process_controller import ProcessController
from src.openfoam.solver_manager import OpenFOAMSolverManager
from src.openfoam.msys2_executor import MSYS2Executor


class StandaloneSimulator:
    """Standalone battery simulator using CLI interface."""

    def __init__(self):
        self.project_manager = None
        self.process_controller = ProcessController()
        self.solver_manager = OpenFOAMSolverManager()
        self.msys2_executor = MSYS2Executor()
        self.project_path = None
        self.project_name = None

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging for standalone execution."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def parse_arguments(self):
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(
            description="Battery OpenFoam Simulator - Standalone CLI"
        )

        parser.add_argument(
            '--simulation',
            choices=['spm', 'halfcell', 'fullcell'],
            required=True,
            help='Type of simulation to run'
        )

        parser.add_argument(
            '--project',
            required=True,
            help='Project name'
        )

        parser.add_argument(
            '--output-dir',
            default='./projects',
            help='Output directory for projects (default: ./projects)'
        )

        parser.add_argument(
            '--config',
            help='Configuration file with simulation parameters'
        )

        parser.add_argument(
            '--skip-mesh',
            action='store_true',
            help='Skip mesh generation (blockMesh, topoSet)'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be executed without running'
        )

        return parser.parse_args()

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not config_file or not Path(config_file).exists():
            self.logger.info("No config file provided or file doesn't exist, using defaults")
            return {}

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            self.logger.info(f"Loaded configuration from {config_file}")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load config file: {e}")
            return {}

    def setup_project(self, simulation_type: str, project_name: str, output_dir: str):
        """Setup project structure."""
        self.logger.info(f"Setting up {simulation_type} project: {project_name}")

        # Map simulation types to template names
        template_map = {
            'spm': 'SPM',
            'halfcell': 'halfCell',
            'fullcell': 'fullCell'
        }

        template_name = template_map[simulation_type]

        # Initialize project manager
        self.project_manager = ProjectManager(output_dir)

        # Create project
        success = self.project_manager.create_project(project_name, template_name)
        if not success:
            raise RuntimeError(f"Failed to create project {project_name}")

        # Set project paths
        self.project_path = Path(output_dir) / project_name
        self.project_name = project_name

        # Set solver
        solver_map = {
            'spm': 'SPMFoam',
            'halfcell': 'halfCellFoam',
            'fullcell': 'fullCellFoam'
        }

        self.solver_manager.set_case_path(str(self.project_path))
        self.solver_manager.set_solver(solver_map[simulation_type])

        self.logger.info(f"Project setup complete: {self.project_path}")

    def validate_case(self) -> bool:
        """Validate OpenFOAM case structure."""
        self.logger.info("Validating case structure...")
        return self.solver_manager.validate_case()

    def run_mesh_generation(self, dry_run: bool = False):
        """Run mesh generation commands."""
        self.logger.info("Running mesh generation...")

        commands = [
            self.solver_manager.get_block_mesh_command(),
            self.solver_manager.get_topo_set_command(),
        ]

        for cmd in commands:
            self.logger.info(f"Executing: {cmd}")
            if not dry_run:
                success = self._execute_command(cmd, str(self.project_path))
                if not success:
                    raise RuntimeError(f"Command failed: {cmd}")
            else:
                self.logger.info(f"[DRY RUN] Would execute: {cmd}")

    def run_solver(self, dry_run: bool = False):
        """Run the OpenFOAM solver."""
        self.logger.info("Running solver...")

        cmd = self.solver_manager.get_solver_command()
        self.logger.info(f"Executing solver: {cmd}")

        if not dry_run:
            success = self._execute_command(cmd, str(self.project_path))
            if not success:
                raise RuntimeError(f"Solver failed: {cmd}")
        else:
            self.logger.info(f"[DRY RUN] Would execute: {cmd}")

    def _execute_command(self, command: str, working_dir: str) -> bool:
        """Execute a command using MSYS2Executor."""
        try:
            self.logger.info(f"Executing OpenFOAM command: {command}")
            self.logger.info(f"Working directory: {working_dir}")

            # Use MSYS2Executor to run the command
            return_code, stdout, stderr = self.msys2_executor.execute_command(
                command=command,
                working_dir=working_dir,
                timeout=600  # 10 minute timeout for OpenFOAM commands
            )

            if return_code == 0:
                self.logger.info(f"Command completed successfully: {command}")
                if stdout:
                    self.logger.debug(f"Command output: {stdout[:200]}...")
                return True
            else:
                self.logger.error(f"Command failed with return code {return_code}: {command}")
                if stderr:
                    self.logger.error(f"Command error: {stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to execute command {command}: {e}")
            return False

    def _verify_openfoam_environment(self) -> bool:
        """Verify that OpenFOAM/MSYS2 environment is available."""
        self.logger.info("Verifying OpenFOAM environment...")
        return self.msys2_executor.verify_msys2()

    def run_simulation(self, args):
        """Run the complete simulation workflow."""
        try:
            # Check MSYS2/OpenFOAM availability (skip in dry-run mode)
            if not args.dry_run and not self._verify_openfoam_environment():
                self.logger.error("OpenFOAM environment not available. Use --dry-run to test without execution.")
                return False

            # Load configuration
            config = self.load_config(args.config)

            # Setup project
            self.setup_project(args.simulation, args.project, args.output_dir)

            # Validate case
            if not self.validate_case():
                raise RuntimeError("Case validation failed")

            # Run mesh generation
            if not args.skip_mesh:
                self.run_mesh_generation(args.dry_run)

            # Run solver
            self.run_solver(args.dry_run)

            self.logger.info("Simulation completed successfully!")
            return True

        except Exception as e:
            self.logger.error(f"Simulation failed: {e}")
            return False

    def run(self):
        """Main entry point."""
        self.logger.info("Battery OpenFoam Simulator - Standalone CLI")
        self.logger.info("=" * 50)

        # Parse arguments
        args = self.parse_arguments()

        # Run simulation
        success = self.run_simulation(args)

        # Exit with appropriate code
        sys.exit(0 if success else 1)


def main():
    """Main entry point."""
    simulator = StandaloneSimulator()
    simulator.run()


if __name__ == "__main__":
    main()