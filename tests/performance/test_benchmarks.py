#!/usr/bin/env python3
"""
Performance benchmark tests for Battery Simulator.
This module provides performance benchmarks for critical operations.
"""

import pytest
import time
import psutil
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import test modules
from src.core.project_manager_enhanced import EnhancedProjectManager
from src.gui.ui_loader_enhanced import UILoaderEnhanced
from src.utils.file_operations_enhanced import EnhancedTemplateManager
from src.openfoam.process_controller import ProcessController

class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(__file__).parent.parent / "temp_performance"
        self.temp_dir.mkdir(exist_ok=True)
        self.templates_path = Path(__file__).parent.parent / "src" / "resources" / "templates"
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def measure_performance(self, func, *args, **kwargs):
        """Measure function performance including time and memory."""
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = end_memory - start_memory
        
        return {
            'result': result,
            'time': end_time - start_time,
            'memory_delta': memory_delta
        }
    
    def test_project_creation_performance(self):
        """Test project creation performance."""
        pm = EnhancedProjectManager(str(self.temp_dir))
        
        def create_project():
            return pm.create_project_safe(
                str(self.temp_dir),
                "perf_test_project",
                "SPM",
                validate_template=False,
                create_backup=False
            )
        
        metrics = self.measure_performance(create_project)
        
        print(f"Project creation time: {metrics['time']:.3f}s")
        print(f"Memory delta: {metrics['memory_delta']:.2f}MB")
        
        # Performance thresholds
        assert metrics['time'] < 10.0, f"Project creation too slow: {metrics['time']:.3f}s"
        assert metrics['memory_delta'] < 100.0, f"Memory usage too high: {metrics['memory_delta']:.2f}MB"
        assert metrics['result'] is True, "Project creation failed"
    
    def test_ui_loading_performance(self):
        """Test UI loading performance."""
        ui_loader = UILoaderEnhanced()
        
        # Test loading multiple UI files
        ui_files = ['mainwindow', 'carboninterface', 'halfcellinterface', 'fullcellfoam', 'resultinterface']
        
        def load_all_ui_files():
            widgets = []
            for ui_name in ui_files:
                try:
                    widget = ui_loader.load_ui_file(ui_name)
                    if widget:
                        widgets.append(widget)
                except Exception:
                    pass
            return widgets
        
        metrics = self.measure_performance(load_all_ui_files)
        
        print(f"UI loading time: {metrics['time']:.3f}s")
        print(f"Memory delta: {metrics['memory_delta']:.2f}MB")
        print(f"Widgets loaded: {len(metrics['result'])}")
        
        # Performance thresholds
        assert metrics['time'] < 5.0, f"UI loading too slow: {metrics['time']:.3f}s"
        assert metrics['memory_delta'] < 50.0, f"Memory usage too high: {metrics['memory_delta']:.2f}MB"
    
    def test_template_copying_performance(self):
        """Test template copying performance."""
        template_manager = EnhancedTemplateManager(str(self.templates_path))
        
        def copy_template():
            return template_manager.copy_template_directory_atomic(
                "SPM", str(self.temp_dir / "template_copy_test")
            )
        
        metrics = self.measure_performance(copy_template)
        
        print(f"Template copying time: {metrics['time']:.3f}s")
        print(f"Memory delta: {metrics['memory_delta']:.2f}MB")
        
        # Performance thresholds
        assert metrics['time'] < 3.0, f"Template copying too slow: {metrics['time']:.3f}s"
        assert metrics['memory_delta'] < 30.0, f"Memory usage too high: {metrics['memory_delta']:.2f}MB"
        assert metrics['result'] is True, "Template copying failed"
    
    def test_process_controller_performance(self):
        """Test process controller performance."""
        controller = ProcessController()
        
        def run_process():
            import subprocess
            process = subprocess.Popen(['python', '-c', 'import time; time.sleep(0.1)'], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            controller.process = process
            return controller.is_running()
        
        metrics = self.measure_performance(run_process)
        
        print(f"Process controller time: {metrics['time']:.3f}s")
        print(f"Memory delta: {metrics['memory_delta']:.2f}MB")
        
        # Performance thresholds
        assert metrics['time'] < 1.0, f"Process controller too slow: {metrics['time']:.3f}s"
        assert metrics['memory_delta'] < 10.0, f"Memory usage too high: {metrics['memory_delta']:.2f}MB"
    
    def test_memory_usage_stability(self):
        """Test memory usage stability over multiple operations."""
        pm = EnhancedProjectManager(str(self.temp_dir))
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple projects
        for i in range(5):
            project_name = f"memory_test_{i}"
            pm.create_project_safe(
                str(self.temp_dir),
                project_name,
                "SPM",
                validate_template=False,
                create_backup=False
            )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory increase after 5 projects: {memory_increase:.2f}MB")
        
        # Memory should not increase excessively
        assert memory_increase < 200.0, f"Memory leak detected: {memory_increase:.2f}MB increase"
    
    def test_concurrent_operations(self):
        """Test concurrent operations performance."""
        import threading
        import queue
        
        pm = EnhancedProjectManager(str(self.temp_dir))
        results = queue.Queue()
        
        def create_project_worker(worker_id):
            try:
                result = pm.create_project_safe(
                    str(self.temp_dir),
                    f"concurrent_test_{worker_id}",
                    "SPM",
                    validate_template=False,
                    create_backup=False
                )
                results.put(('success', result))
            except Exception as e:
                results.put(('error', str(e)))
        
        # Start multiple threads
        threads = []
        num_threads = 3
        
        start_time = time.perf_counter()
        for i in range(num_threads):
            thread = threading.Thread(target=create_project_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        end_time = time.perf_counter()
        
        # Collect results
        success_count = 0
        error_count = 0
        while not results.empty():
            status, result = results.get()
            if status == 'success':
                success_count += 1
            else:
                error_count += 1
                print(f"Error: {result}")
        
        print(f"Concurrent operations time: {end_time - start_time:.3f}s")
        print(f"Successful operations: {success_count}")
        print(f"Failed operations: {error_count}")
        
        # All operations should succeed
        assert success_count == num_threads, f"Not all operations succeeded: {success_count}/{num_threads}"
        assert error_count == 0, f"Some operations failed: {error_count}"
    
    def test_large_file_handling(self):
        """Test handling of large files."""
        # Create a large test file
        large_file = self.temp_dir / "large_test_file.txt"
        with open(large_file, 'w') as f:
            # Write 10MB of data
            for _ in range(1000):
                f.write("x" * 10000 + "\n")
        
        def read_large_file():
            with open(large_file, 'r') as f:
                content = f.read()
            return len(content)
        
        metrics = self.measure_performance(read_large_file)
        
        print(f"Large file reading time: {metrics['time']:.3f}s")
        print(f"Memory delta: {metrics['memory_delta']:.2f}MB")
        print(f"File size: {metrics['result']} characters")
        
        # Performance thresholds for large file handling
        assert metrics['time'] < 2.0, f"Large file reading too slow: {metrics['time']:.3f}s"
        assert metrics['memory_delta'] < 50.0, f"Memory usage too high: {metrics['memory_delta']:.2f}MB"
    
    def test_cleanup_performance(self):
        """Test cleanup performance."""
        pm = EnhancedProjectManager(str(self.temp_dir))
        
        # Create test projects
        for i in range(10):
            pm.create_project_safe(
                str(self.temp_dir),
                f"cleanup_test_{i}",
                "SPM",
                validate_template=False,
                create_backup=False
            )
        
        def cleanup_projects():
            import shutil
            for item in self.temp_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
            return True
        
        metrics = self.measure_performance(cleanup_projects)
        
        print(f"Cleanup time: {metrics['time']:.3f}s")
        print(f"Memory delta: {metrics['memory_delta']:.2f}MB")
        
        # Performance thresholds for cleanup
        assert metrics['time'] < 5.0, f"Cleanup too slow: {metrics['time']:.3f}s"
        assert metrics['memory_delta'] < 20.0, f"Memory usage too high: {metrics['memory_delta']:.2f}MB"
        assert metrics['result'] is True, "Cleanup failed"


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s"])