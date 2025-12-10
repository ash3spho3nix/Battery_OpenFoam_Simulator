#!/usr/bin/env python3
"""
Performance benchmarks for Battery Simulator.

This module contains performance benchmarks to measure and validate
the performance characteristics of the application.
"""

import time
import psutil
import pytest
import logging
from pathlib import Path
from typing import Dict, Any

# Import the main application components
from src.gui.main_window import MainWindow
from src.core.project_manager import ProjectManager
from src.gui.ui_config import UIConfig

logger = logging.getLogger(__name__)

class PerformanceBenchmark:
    """Performance benchmarking utilities."""
    
    def __init__(self):
        self.results = {}
        
    def measure_memory_usage(self) -> float:
        """Measure current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
        
    def measure_time(self, func, *args, **kwargs) -> Dict[str, Any]:
        """Measure execution time and memory usage of a function."""
        start_time = time.time()
        start_memory = self.measure_memory_usage()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = self.measure_memory_usage()
        
        return {
            'execution_time': end_time - start_time,
            'memory_delta': end_memory - start_memory,
            'result': result
        }

@pytest.fixture
def benchmark():
    """Performance benchmark fixture."""
    return PerformanceBenchmark()

@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        'path': '/tmp/test_projects',
        'name': 'performance_test_project',
        'module': 'SPM'
    }

class TestApplicationPerformance:
    """Performance tests for the main application."""
    
    def test_main_window_creation_time(self, benchmark):
        """Test MainWindow creation time."""
        logger.info("Testing MainWindow creation time...")
        
        # Measure MainWindow creation
        result = benchmark.measure_time(
            MainWindow,
            ui_config=UIConfig()
        )
        
        creation_time = result['execution_time']
        memory_delta = result['memory_delta']
        
        logger.info(f"MainWindow creation time: {creation_time:.3f}s")
        logger.info(f"Memory delta: {memory_delta:.2f}MB")
        
        # Assert performance requirements
        assert creation_time < 5.0, f"MainWindow creation too slow: {creation_time:.3f}s"
        assert abs(memory_delta) < 100.0, f"Memory usage too high: {memory_delta:.2f}MB"
        
        self.results['main_window_creation'] = result
        
    def test_project_manager_creation_time(self, benchmark):
        """Test ProjectManager creation time."""
        logger.info("Testing ProjectManager creation time...")
        
        # Measure ProjectManager creation
        result = benchmark.measure_time(
            ProjectManager,
            base_projects_path=Path('/tmp/test_projects')
        )
        
        creation_time = result['execution_time']
        memory_delta = result['memory_delta']
        
        logger.info(f"ProjectManager creation time: {creation_time:.3f}s")
        logger.info(f"Memory delta: {memory_delta:.2f}MB")
        
        # Assert performance requirements
        assert creation_time < 1.0, f"ProjectManager creation too slow: {creation_time:.3f}s"
        assert abs(memory_delta) < 50.0, f"Memory usage too high: {memory_delta:.2f}MB"
        
        self.results['project_manager_creation'] = result
        
    def test_large_project_creation(self, benchmark, sample_project_data):
        """Test creating a large project."""
        logger.info("Testing large project creation...")
        
        # Create project manager
        project_manager = ProjectManager(
            base_projects_path=Path(sample_project_data['path'])
        )
        
        # Measure large project creation
        result = benchmark.measure_time(
            project_manager.create_project,
            sample_project_data['path'],
            sample_project_data['name'],
            sample_project_data['module']
        )
        
        creation_time = result['execution_time']
        memory_delta = result['memory_delta']
        
        logger.info(f"Large project creation time: {creation_time:.3f}s")
        logger.info(f"Memory delta: {memory_delta:.2f}MB")
        
        # Assert performance requirements
        assert creation_time < 30.0, f"Project creation too slow: {creation_time:.3f}s"
        assert abs(memory_delta) < 200.0, f"Memory usage too high: {memory_delta:.2f}MB"
        
        self.results['large_project_creation'] = result

class TestMemoryLeaks:
    """Memory leak tests."""
    
    def test_main_window_memory_leaks(self):
        """Test for memory leaks in MainWindow creation."""
        logger.info("Testing MainWindow memory leaks...")
        
        # Measure initial memory
        initial_memory = self._get_memory_usage()
        
        # Create and destroy multiple MainWindow instances
        for i in range(10):
            window = MainWindow(ui_config=UIConfig())
            window.close()
            
        # Force garbage collection
        import gc
        gc.collect()
        
        # Measure final memory
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        logger.info(f"Memory increase after 10 MainWindow creations: {memory_increase:.2f}MB")
        
        # Assert no significant memory leak
        assert memory_increase < 50.0, f"Potential memory leak detected: {memory_increase:.2f}MB"
        
    def test_project_manager_memory_leaks(self):
        """Test for memory leaks in ProjectManager creation."""
        logger.info("Testing ProjectManager memory leaks...")
        
        # Measure initial memory
        initial_memory = self._get_memory_usage()
        
        # Create and destroy multiple ProjectManager instances
        for i in range(10):
            manager = ProjectManager(
                base_projects_path=Path('/tmp/test_projects')
            )
            
        # Force garbage collection
        import gc
        gc.collect()
        
        # Measure final memory
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        logger.info(f"Memory increase after 10 ProjectManager creations: {memory_increase:.2f}MB")
        
        # Assert no significant memory leak
        assert memory_increase < 20.0, f"Potential memory leak detected: {memory_increase:.2f}MB"
        
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

class TestUIPerformance:
    """UI performance tests."""
    
    def test_ui_loading_performance(self, benchmark):
        """Test UI loading performance."""
        logger.info("Testing UI loading performance...")
        
        # Create main window and measure UI setup
        main_window = MainWindow(ui_config=UIConfig())
        
        result = benchmark.measure_time(main_window._setup_ui)
        
        setup_time = result['execution_time']
        memory_delta = result['memory_delta']
        
        logger.info(f"UI setup time: {setup_time:.3f}s")
        logger.info(f"Memory delta: {memory_delta:.2f}MB")
        
        # Assert performance requirements
        assert setup_time < 2.0, f"UI setup too slow: {setup_time:.3f}s"
        assert abs(memory_delta) < 100.0, f"Memory usage too high: {memory_delta:.2f}MB"
        
        self.results['ui_setup'] = result

def run_performance_benchmarks():
    """Run all performance benchmarks."""
    logger.info("Running performance benchmarks...")
    
    # Create test instance
    benchmark_test = TestApplicationPerformance()
    
    # Run benchmarks
    benchmark_test.test_main_window_creation_time(PerformanceBenchmark())
    benchmark_test.test_project_manager_creation_time(PerformanceBenchmark())
    
    # Run memory leak tests
    leak_test = TestMemoryLeaks()
    leak_test.test_main_window_memory_leaks()
    leak_test.test_project_manager_memory_leaks()
    
    # Run UI performance tests
    ui_test = TestUIPerformance()
    ui_test.test_ui_loading_performance(PerformanceBenchmark())
    
    logger.info("Performance benchmarks completed successfully")

if __name__ == "__main__":
    run_performance_benchmarks()