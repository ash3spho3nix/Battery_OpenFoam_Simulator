#!/usr/bin/env python3
"""
Test runner script for Battery Simulator.

This script provides a comprehensive test runner with options for:
- Running all tests
- Running specific test categories
- Generating coverage reports
- Performance testing
- Cross-platform testing
- CI/CD integration

Usage:
    python run_tests.py [options]
    
Examples:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run unit tests only
    python run_tests.py --coverage         # Run tests with coverage
    python run_tests.py --performance      # Run performance tests
    python run_tests.py --ci               # Run tests for CI/CD
"""

import sys
import os
import subprocess
import argparse
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Add src to Python path
SCRIPT_DIR = Path(__file__).parent.absolute()
SRC_DIR = SCRIPT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

# Import test utilities
try:
    import pytest
    from coverage import Coverage
    HAS_TESTING_TOOLS = True
except ImportError:
    HAS_TESTING_TOOLS = False
    print("Warning: Testing tools not available. Install pytest and coverage.")


class TestRunner:
    """Comprehensive test runner for Battery Simulator."""
    
    def __init__(self):
        self.project_root = SCRIPT_DIR
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "src" / "tests"
        self.reports_dir = self.project_root / "test_reports"
        self.coverage_file = self.project_root / ".coverage"
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Test configuration
        self.test_config = {
            'pytest_args': [],
            'coverage_enabled': False,
            'performance_enabled': False,
            'ci_mode': False,
            'verbose': False,
            'parallel': False,
            'markers': [],
            'exclude_markers': []
        }
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_file = self.reports_dir / "test_runner.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def parse_arguments(self) -> argparse.Namespace:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(
            description="Battery Simulator Test Runner",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit             # Run unit tests only
  python run_tests.py --coverage         # Run tests with coverage
  python run_tests.py --performance      # Run performance tests
  python run_tests.py --ci               # Run tests for CI/CD
  python run_tests.py --fast             # Skip slow tests
  python run_tests.py --parallel         # Run tests in parallel
  python run_tests.py --verbose          # Verbose output
            """
        )
        
        # Test selection
        parser.add_argument(
            '--unit', action='store_true',
            help='Run unit tests only'
        )
        parser.add_argument(
            '--integration', action='store_true',
            help='Run integration tests only'
        )
        parser.add_argument(
            '--performance', action='store_true',
            help='Run performance tests only'
        )
        parser.add_argument(
            '--ui', action='store_true',
            help='Run UI tests only'
        )
        parser.add_argument(
            '--openfoam', action='store_true',
            help='Run OpenFOAM integration tests only'
        )
        
        # Test options
        parser.add_argument(
            '--fast', action='store_true',
            help='Skip slow tests'
        )
        parser.add_argument(
            '--parallel', action='store_true',
            help='Run tests in parallel'
        )
        parser.add_argument(
            '--verbose', '-v', action='store_true',
            help='Verbose output'
        )
        parser.add_argument(
            '--debug', action='store_true',
            help='Debug mode'
        )
        
        # Coverage options
        parser.add_argument(
            '--coverage', action='store_true',
            help='Run tests with coverage'
        )
        parser.add_argument(
            '--coverage-html', action='store_true',
            help='Generate HTML coverage report'
        )
        parser.add_argument(
            '--coverage-xml', action='store_true',
            help='Generate XML coverage report'
        )
        
        # CI/CD options
        parser.add_argument(
            '--ci', action='store_true',
            help='Run tests in CI mode'
        )
        parser.add_argument(
            '--junit', action='store_true',
            help='Generate JUnit XML report'
        )
        
        # Custom test selection
        parser.add_argument(
            '--test-file', type=str,
            help='Run specific test file'
        )
        parser.add_argument(
            '--test-pattern', type=str,
            help='Run tests matching pattern'
        )
        parser.add_argument(
            '--marker', type=str, action='append', default=[],
            help='Run tests with specific marker'
        )
        parser.add_argument(
            '--exclude-marker', type=str, action='append', default=[],
            help='Exclude tests with specific marker'
        )
        
        # Output options
        parser.add_argument(
            '--output-dir', type=str,
            help='Output directory for reports'
        )
        
        return parser.parse_args()
    
    def configure_test_run(self, args: argparse.Namespace):
        """Configure test run based on arguments."""
        # Basic configuration
        self.test_config['verbose'] = args.verbose or args.debug
        self.test_config['ci_mode'] = args.ci
        self.test_config['parallel'] = args.parallel
        
        # Test selection
        if args.unit:
            self.test_config['markers'].append('unit')
        if args.integration:
            self.test_config['markers'].append('integration')
        if args.performance:
            self.test_config['markers'].append('performance')
        if args.ui:
            self.test_config['markers'].append('ui')
        if args.openfoam:
            self.test_config['markers'].append('openfoam')
        
        # Add custom markers
        self.test_config['markers'].extend(args.marker)
        
        # Add exclude markers
        self.test_config['exclude_markers'].extend(args.exclude_marker)
        
        # Coverage configuration
        self.test_config['coverage_enabled'] = args.coverage
        self.test_config['coverage_html'] = args.coverage_html
        self.test_config['coverage_xml'] = args.coverage_xml
        
        # Performance testing
        self.test_config['performance_enabled'] = args.performance
        
        # CI mode configuration
        if args.ci:
            self.test_config['fast'] = True
            self.test_config['junit'] = True
            self.test_config['coverage'] = True
            self.test_config['coverage_html'] = True
        
        # Fast mode
        if args.fast:
            self.test_config['exclude_markers'].append('slow')
        
        # Output directory
        if args.output_dir:
            self.reports_dir = Path(args.output_dir)
            self.reports_dir.mkdir(exist_ok=True)
        
        # Test file or pattern
        if args.test_file:
            self.test_config['pytest_args'].append(str(self.tests_dir / args.test_file))
        elif args.test_pattern:
            self.test_config['pytest_args'].append(f"-k {args.test_pattern}")
    
    def build_pytest_args(self) -> List[str]:
        """Build pytest arguments based on configuration."""
        args = []
        
        # Basic arguments
        args.extend(['-xvs' if self.test_config['verbose'] else '-x'])
        
        # Test discovery
        args.append(str(self.tests_dir))
        
        # Markers
        if self.test_config['markers']:
            marker_expr = ' or '.join(self.test_config['markers'])
            args.extend(['-m', marker_expr])
        
        # Exclude markers
        if self.test_config['exclude_markers']:
            for marker in self.test_config['exclude_markers']:
                args.extend(['-m', f'not {marker}'])
        
        # Parallel execution
        if self.test_config['parallel']:
            try:
                import pytest_xdist
                args.append('-n auto')
            except ImportError:
                self.logger.warning("pytest-xdist not available, running tests sequentially")
        
        # JUnit XML output
        if self.test_config['ci_mode'] or self.test_config.get('junit', False):
            junit_file = self.reports_dir / "junit.xml"
            args.extend(['--junitxml', str(junit_file)])
        
        # Coverage
        if self.test_config['coverage_enabled']:
            args.extend([
                '--cov', str(self.src_dir),
                '--cov-report', 'term-missing',
                '--cov-report', 'html:' + str(self.reports_dir / "coverage_html"),
                '--cov-report', 'xml:' + str(self.reports_dir / "coverage.xml")
            ])
        
        # Custom pytest arguments
        args.extend(self.test_config['pytest_args'])
        
        return args
    
    def run_coverage_analysis(self) -> Dict[str, Any]:
        """Run coverage analysis and generate reports."""
        if not self.test_config['coverage_enabled']:
            return {}
        
        self.logger.info("Running coverage analysis...")
        
        # Start coverage
        cov = Coverage(
            source=[str(self.src_dir)],
            omit=['*/tests/*', '*/test_*', '*/conftest.py']
        )
        cov.start()
        
        # Run tests
        pytest_args = self.build_pytest_args()
        exit_code = pytest.main(pytest_args)
        
        # Stop coverage
        cov.stop()
        cov.save()
        
        # Generate reports
        coverage_data = {}
        
        # Terminal report
        cov.report(show_missing=True)
        
        # HTML report
        if self.test_config['coverage_html']:
            cov.html_report(directory=str(self.reports_dir / "coverage_html"))
            self.logger.info(f"HTML coverage report: {self.reports_dir / 'coverage_html' / 'index.html'}")
        
        # XML report
        if self.test_config['coverage_xml']:
            cov.xml_report(outfile=str(self.reports_dir / "coverage.xml"))
            self.logger.info(f"XML coverage report: {self.reports_dir / 'coverage.xml'}")
        
        # Get coverage data
        analysis = cov.analysis()
        coverage_data = {
            'total_lines': analysis[1],
            'covered_lines': analysis[2],
            'missing_lines': len(analysis[3]),
            'coverage_percent': cov.report()
        }
        
        return coverage_data
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests and generate reports."""
        if not self.test_config['performance_enabled']:
            return {}
        
        self.logger.info("Running performance tests...")
        
        # Run performance tests
        pytest_args = self.build_pytest_args()
        pytest_args.extend(['-m', 'performance'])
        
        exit_code = pytest.main(pytest_args)
        
        # Generate performance report
        performance_data = {
            'exit_code': exit_code,
            'timestamp': time.time(),
            'tests_run': 0,
            'performance_metrics': []
        }
        
        return performance_data
    
    def run_tests(self) -> Dict[str, Any]:
        """Run the test suite."""
        self.logger.info("Starting test run...")
        start_time = time.time()
        
        # Build pytest arguments
        pytest_args = self.build_pytest_args()
        
        self.logger.info(f"Running pytest with args: {' '.join(pytest_args)}")
        
        # Run tests
        exit_code = pytest.main(pytest_args)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Generate test report
        test_data = {
            'exit_code': exit_code,
            'duration': duration,
            'timestamp': time.time(),
            'config': self.test_config.copy()
        }
        
        # Run coverage if enabled
        if self.test_config['coverage_enabled']:
            coverage_data = self.run_coverage_analysis()
            test_data['coverage'] = coverage_data
        
        # Run performance tests if enabled
        if self.test_config['performance_enabled']:
            performance_data = self.run_performance_tests()
            test_data['performance'] = performance_data
        
        # Save test report
        self.save_test_report(test_data)
        
        return test_data
    
    def save_test_report(self, test_data: Dict[str, Any]):
        """Save test report to JSON file."""
        report_file = self.reports_dir / "test_report.json"
        
        with open(report_file, 'w') as f:
            json.dump(test_data, f, indent=2, default=str)
        
        self.logger.info(f"Test report saved to: {report_file}")
    
    def generate_summary(self, test_data: Dict[str, Any]):
        """Generate test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        # Basic info
        print(f"Exit Code: {test_data['exit_code']}")
        print(f"Duration: {test_data['duration']:.2f}s")
        print(f"Timestamp: {test_data['timestamp']}")
        
        # Coverage info
        if 'coverage' in test_data:
            coverage = test_data['coverage']
            print(f"\nCoverage:")
            print(f"  Total Lines: {coverage.get('total_lines', 'N/A')}")
            print(f"  Covered Lines: {coverage.get('covered_lines', 'N/A')}")
            print(f"  Missing Lines: {coverage.get('missing_lines', 'N/A')}")
            print(f"  Coverage %: {coverage.get('coverage_percent', 'N/A')}")
        
        # Performance info
        if 'performance' in test_data:
            performance = test_data['performance']
            print(f"\nPerformance:")
            print(f"  Exit Code: {performance.get('exit_code', 'N/A')}")
        
        # Configuration
        print(f"\nConfiguration:")
        for key, value in test_data['config'].items():
            print(f"  {key}: {value}")
        
        print("="*60)
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        if not HAS_TESTING_TOOLS:
            print("Error: Required testing tools not available.")
            print("Please install: pip install pytest coverage")
            return False
        
        return True
    
    def run(self):
        """Main test runner method."""
        # Parse arguments
        args = self.parse_arguments()
        
        # Configure test run
        self.configure_test_run(args)
        
        # Check dependencies
        if not self.check_dependencies():
            sys.exit(1)
        
        # Run tests
        test_data = self.run_tests()
        
        # Generate summary
        self.generate_summary(test_data)
        
        # Exit with appropriate code
        sys.exit(test_data['exit_code'])


def main():
    """Main entry point."""
    runner = TestRunner()
    runner.run()


if __name__ == "__main__":
    main()