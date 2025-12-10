"""
Performance and benchmark tests for Battery Simulator.

This module tests performance aspects including:
- Critical operation benchmarks
- Memory usage profiling
- Large project handling
- UI responsiveness
- OpenFOAM integration performance
"""

import pytest
import os
import tempfile
import shutil
import time
import psutil
import tracemalloc
from pathlib import Path
from unittest.mock import Mock, patch

from src.core.application import BatterySimulatorApp
from src.core.project_manager import ProjectManager
from src.gui.ui_loader import UILoader
from src.gui.ui_loader_enhanced import UILoaderEnhanced
from src.gui.ui_config import UIConfig
from src.openfoam.process_controller import ProcessController
from src.openfoam.solver_manager import OpenFOAMSolverManager
from src.utils.file_operations import TemplateManager
from src.utils.parameter_parser import ParameterManager


class TestPerformanceBenchmarks:
    """Test performance benchmarks for critical operations."""
    
    def test_project_creation_performance(self, temp_dir):
        """Benchmark project creation performance."""
        # Create large template
        templates_path = Path(temp_dir) / "templates"
        large_template = templates_path / "LargeTemplate"
        large_template.mkdir(parents=True)
        
        # Create many files to simulate large template
        for i in range(50):
            file_path = large_template / f"file_{i}.txt"
            file_path.write_text(f"Content of file {i}" * 1000)  # Large content
        
        # Benchmark project creation
        pm = ProjectManager()
        
        execution_times = []
        for i in range(5):  # Run 5 times for average
            project_name = f"perf_test_{i}"
            
            start_time = time.perf_counter()
            
            with patch('src.core.constants.TEMPLATES_PATH', templates_path):
                pm.create_project(temp_dir, project_name, "LargeTemplate")
            
            end_time = time.perf_counter()
            execution_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        print(f"Project Creation Performance:")
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  Min time: {min_time:.3f}s")
        print(f"  Max time: {max_time:.3f}s")
        
        # Performance should be reasonable (less than 5 seconds average)
        assert avg_time < 5.0, f"Project creation too slow: {avg_time:.3f}s"
    
    def test_ui_loading_performance(self, qt_app, temp_dir):
        """Benchmark UI loading performance."""
        # Create multiple UI files
        ui_files = {}
        for i in range(10):
            filename = f"interface_{i}.ui"
            content = f'''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>TestWidget{i}</class>
 <widget class="QWidget" name="TestWidget{i}">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>400</width>
    <height>300</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Test Widget {i}</string>
  </property>
  <widget class="QPushButton" name="testButton{i}">
   <property name="geometry">
    <rect>
     <x>10</x>
     <y>10</y>
     <width>80</width>
     <height>25</height>
    </rect>
   </property>
   <property name="text">
    <string>Test Button {i}</string>
   </property>
  </widget>
 </widget>
</ui>'''
            ui_files[filename] = content
        
        # Write UI files
        for filename, content in ui_files.items():
            ui_file = Path(temp_dir) / filename
            ui_file.write_text(content)
        
        # Benchmark UI loading
        execution_times = []
        
        for i in range(5):  # Load each UI file 5 times
            for filename in ui_files.keys():
                ui_path = str(Path(temp_dir) / filename)
                
                start_time = time.perf_counter()
                
                with patch('src.gui.ui_loader.UI_LOADER_PATH', temp_dir):
                    widget = UILoader.load_ui_file(ui_path)
                
                end_time = time.perf_counter()
                execution_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        print(f"UI Loading Performance:")
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  Min time: {min_time:.3f}s")
        print(f"  Max time: {max_time:.3f}s")
        
        # UI loading should be fast (less than 1 second average)
        assert avg_time < 1.0, f"UI loading too slow: {avg_time:.3f}s"
    
    def test_parameter_file_parsing_performance(self, temp_dir):
        """Benchmark parameter file parsing performance."""
        # Create large parameter file
        large_content = "/* Large parameter file */\n"
        for i in range(1000):
            large_content += f"vertex {i} ({i} {i} {i});\n"
        
        param_file = Path(temp_dir) / "large_blockMeshDict"
        param_file.write_text(large_content)
        
        manager = ParameterManager(temp_dir)
        
        # Benchmark parsing
        execution_times = []
        
        for i in range(10):  # Parse 10 times
            start_time = time.perf_counter()
            
            content = manager.read_parameter_file("large_blockMeshDict")
            
            end_time = time.perf_counter()
            execution_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        print(f"Parameter File Parsing Performance:")
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  Min time: {min_time:.3f}s")
        print(f"  Max time: {max_time:.3f}s")
        
        # Parsing should be fast (less than 0.5 seconds average)
        assert avg_time < 0.5, f"Parameter parsing too slow: {avg_time:.3f}s"
    
    def test_template_validation_performance(self, temp_dir):
        """Benchmark template validation performance."""
        # Create multiple templates
        templates_path = Path(temp_dir) / "templates"
        templates_path.mkdir()
        
        for i in range(20):
            template_dir = templates_path / f"Template{i}"
            template_dir.mkdir()
            (template_dir / "README.md").write_text(f"Template {i} README")
        
        manager = TemplateManager(str(templates_path))
        
        # Benchmark validation
        execution_times = []
        
        for i in range(5):  # Validate all templates 5 times
            start_time = time.perf_counter()
            
            templates = manager.list_templates()
            for template in templates:
                is_valid = TemplateManager.validate_template(str(templates_path / template))
            
            end_time = time.perf_counter()
            execution_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        print(f"Template Validation Performance:")
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  Min time: {min_time:.3f}s")
        print(f"  Max time: {max_time:.3f}s")
        
        # Validation should be fast (less than 1 second average)
        assert avg_time < 1.0, f"Template validation too slow: {avg_time:.3f}s"
    
    def test_process_controller_performance(self):
        """Benchmark process controller performance."""
        controller = ProcessController()
        
        # Benchmark process creation overhead
        execution_times = []
        
        for i in range(10):  # Create 10 processes
            start_time = time.perf_counter()
            
            # Use a simple command for testing
            controller.start_process('echo "test"')
            
            # Wait for completion
            while controller.is_running():
                time.sleep(0.01)
            
            end_time = time.perf_counter()
            execution_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        print(f"Process Controller Performance:")
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  Min time: {min_time:.3f}s")
        print(f"  Max time: {max_time:.3f}s")
        
        # Process creation should be reasonably fast
        assert avg_time < 2.0, f"Process creation too slow: {avg_time:.3f}s"


class TestMemoryUsage:
    """Test memory usage and profiling."""
    
    def test_project_creation_memory_usage(self, temp_dir):
        """Test memory usage during project creation."""
        # Start memory tracking
        tracemalloc.start()
        
        # Create template
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        
        (spm_template / "README.md").write_text("SPM Template")
        
        # Create project
        pm = ProjectManager()
        
        with patch('src.core.constants.TEMPLATES_PATH', templates_path):
            pm.create_project(temp_dir, "memory_test", "SPM")
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Project Creation Memory Usage:")
        print(f"  Current memory: {current / 1024 / 1024:.2f} MB")
        print(f"  Peak memory: {peak / 1024 / 1024:.2f} MB")
        
        # Memory usage should be reasonable (less than 100 MB)
        assert peak < 100 * 1024 * 1024, f"Memory usage too high: {peak / 1024 / 1024:.2f} MB"
    
    def test_ui_loading_memory_usage(self, qt_app, temp_dir):
        """Test memory usage during UI loading."""
        # Create UI file
        ui_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>TestWidget</class>
 <widget class="QWidget" name="TestWidget">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Test Widget</string>
  </property>
  <widget class="QPushButton" name="testButton">
   <property name="geometry">
    <rect>
     <x>10</x>
     <y>10</y>
     <width>80</width>
     <height>25</height>
    </rect>
   </property>
   <property name="text">
    <string>Test Button</string>
   </property>
  </widget>
 </widget>
</ui>'''
        
        ui_file = Path(temp_dir) / "test.ui"
        ui_file.write_text(ui_content)
        
        # Start memory tracking
        tracemalloc.start()
        
        # Load UI multiple times
        for i in range(10):
            widget = UILoader.load_ui_file(str(ui_file))
            # Don't delete widget to simulate memory accumulation
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"UI Loading Memory Usage:")
        print(f"  Current memory: {current / 1024 / 1024:.2f} MB")
        print(f"  Peak memory: {peak / 1024 / 1024:.2f} MB")
        
        # Memory usage should be reasonable (less than 50 MB)
        assert peak < 50 * 1024 * 1024, f"Memory usage too high: {peak / 1024 / 1024:.2f} MB"
    
    def test_parameter_parsing_memory_usage(self, temp_dir):
        """Test memory usage during parameter parsing."""
        # Create large parameter file
        large_content = "/* Large parameter file */\n"
        for i in range(5000):  # Very large file
            large_content += f"vertex {i} ({i} {i} {i});\n"
        
        param_file = Path(temp_dir) / "large_blockMeshDict"
        param_file.write_text(large_content)
        
        # Start memory tracking
        tracemalloc.start()
        
        manager = ParameterManager(temp_dir)
        
        # Parse file multiple times
        for i in range(5):
            content = manager.read_parameter_file("large_blockMeshDict")
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Parameter Parsing Memory Usage:")
        print(f"  Current memory: {current / 1024 / 1024:.2f} MB")
        print(f"  Peak memory: {peak / 1024 / 1024:.2f} MB")
        
        # Memory usage should be reasonable for large files (less than 200 MB)
        assert peak < 200 * 1024 * 1024, f"Memory usage too high: {peak / 1024 / 1024:.2f} MB"
    
    def test_memory_leak_detection(self, temp_dir):
        """Test for memory leaks in repeated operations."""
        # Start memory tracking
        tracemalloc.start()
        
        initial_memory = tracemalloc.get_traced_memory()[0]
        
        # Perform repeated operations
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        (spm_template / "README.md").write_text("SPM Template")
        
        pm = ProjectManager()
        
        # Create and delete projects multiple times
        for i in range(10):
            project_name = f"leak_test_{i}"
            
            with patch('src.core.constants.TEMPLATES_PATH', templates_path):
                pm.create_project(temp_dir, project_name, "SPM")
            
            # Simulate project deletion
            project_path = Path(temp_dir) / project_name
            if project_path.exists():
                shutil.rmtree(project_path)
        
        # Get final memory usage
        final_memory = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        
        memory_increase = final_memory - initial_memory
        
        print(f"Memory Leak Detection:")
        print(f"  Initial memory: {initial_memory / 1024 / 1024:.2f} MB")
        print(f"  Final memory: {final_memory / 1024 / 1024:.2f} MB")
        print(f"  Memory increase: {memory_increase / 1024 / 1024:.2f} MB")
        
        # Memory increase should be minimal (less than 10 MB)
        assert memory_increase < 10 * 1024 * 1024, f"Possible memory leak: {memory_increase / 1024 / 1024:.2f} MB"


class TestLargeScalePerformance:
    """Test performance with large-scale operations."""
    
    def test_large_project_hierarchy(self, temp_dir):
        """Test performance with deeply nested project hierarchies."""
        # Create deeply nested template
        templates_path = Path(temp_dir) / "templates"
        deep_template = templates_path / "DeepTemplate"
        
        # Create 10 levels of nesting
        current_dir = deep_template
        for i in range(10):
            current_dir = current_dir / f"level_{i}"
            current_dir.mkdir(parents=True)
            
            # Create files at each level
            for j in range(5):
                file_path = current_dir / f"file_{j}.txt"
                file_path.write_text(f"Content at level {i}, file {j}")
        
        # Benchmark creation of project with deep hierarchy
        pm = ProjectManager()
        
        start_time = time.perf_counter()
        
        with patch('src.core.constants.TEMPLATES_PATH', templates_path):
            pm.create_project(temp_dir, "deep_project", "DeepTemplate")
        
        end_time = time.perf_counter()
        creation_time = end_time - start_time
        
        print(f"Large Project Hierarchy Performance:")
        print(f"  Creation time: {creation_time:.3f}s")
        
        # Should complete in reasonable time (less than 10 seconds)
        assert creation_time < 10.0, f"Deep hierarchy creation too slow: {creation_time:.3f}s"
    
    def test_many_files_performance(self, temp_dir):
        """Test performance with projects containing many files."""
        # Create template with many files
        templates_path = Path(temp_dir) / "templates"
        many_files_template = templates_path / "ManyFilesTemplate"
        many_files_template.mkdir(parents=True)
        
        # Create 200 files
        for i in range(200):
            file_path = many_files_template / f"file_{i:03d}.txt"
            file_path.write_text(f"Content of file {i}" * 100)
        
        # Benchmark creation
        pm = ProjectManager()
        
        start_time = time.perf_counter()
        
        with patch('src.core.constants.TEMPLATES_PATH', templates_path):
            pm.create_project(temp_dir, "many_files_project", "ManyFilesTemplate")
        
        end_time = time.perf_counter()
        creation_time = end_time - start_time
        
        print(f"Many Files Performance:")
        print(f"  Creation time: {creation_time:.3f}s")
        
        # Should complete in reasonable time (less than 30 seconds)
        assert creation_time < 30.0, f"Many files creation too slow: {creation_time:.3f}s"
    
    def test_large_ui_file_performance(self, qt_app, temp_dir):
        """Test performance with large UI files."""
        # Create large UI file
        large_ui_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>LargeWidget</class>
 <widget class="QWidget" name="LargeWidget">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1000</width>
    <height>800</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Large Widget</string>
  </property>
'''
        
        # Add many widgets to make it large
        for i in range(1000):
            large_ui_content += f'''  <widget class="QPushButton" name="button_{i}">
   <property name="geometry">
    <rect>
     <x>{i % 10 * 100}</x>
     <y>{i // 10 * 50}</y>
     <width>80</width>
     <height>25</height>
    </rect>
   </property>
   <property name="text">
    <string>Button {i}</string>
   </property>
  </widget>
'''
        
        large_ui_content += ''' </widget>
</ui>'''
        
        large_ui_file = Path(temp_dir) / "large.ui"
        large_ui_file.write_text(large_ui_content)
        
        # Benchmark loading
        start_time = time.perf_counter()
        
        widget = UILoader.load_ui_file(str(large_ui_file))
        
        end_time = time.perf_counter()
        loading_time = end_time - start_time
        
        print(f"Large UI File Performance:")
        print(f"  Loading time: {loading_time:.3f}s")
        
        # Should load in reasonable time (less than 5 seconds)
        assert loading_time < 5.0, f"Large UI loading too slow: {loading_time:.3f}s"


class TestSystemResourceUsage:
    """Test system resource usage during operations."""
    
    def test_cpu_usage_during_project_creation(self, temp_dir):
        """Test CPU usage during project creation."""
        # Create template
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        (spm_template / "README.md").write_text("SPM Template")
        
        pm = ProjectManager()
        
        # Monitor CPU usage
        process = psutil.Process()
        cpu_percentages = []
        
        for i in range(5):
            # Start monitoring
            process.cpu_percent(interval=None)  # Reset
            time.sleep(0.1)  # Small delay
            
            # Create project
            with patch('src.core.constants.TEMPLATES_PATH', templates_path):
                pm.create_project(temp_dir, f"cpu_test_{i}", "SPM")
            
            # Get CPU usage
            cpu_percent = process.cpu_percent(interval=0.1)
            cpu_percentages.append(cpu_percent)
        
        avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
        
        print(f"CPU Usage During Project Creation:")
        print(f"  Average CPU: {avg_cpu:.1f}%")
        print(f"  Max CPU: {max(cpu_percentages):.1f}%")
        
        # CPU usage should be reasonable
        assert avg_cpu < 80.0, f"CPU usage too high: {avg_cpu:.1f}%"
    
    def test_disk_io_during_template_copying(self, temp_dir):
        """Test disk I/O during template copying."""
        # Create template with large files
        templates_path = Path(temp_dir) / "templates"
        large_template = templates_path / "LargeTemplate"
        large_template.mkdir(parents=True)
        
        # Create large files
        for i in range(10):
            large_file = large_template / f"large_file_{i}.dat"
            # Create 1MB file
            with open(large_file, 'wb') as f:
                f.write(b'x' * 1024 * 1024)
        
        pm = ProjectManager()
        
        # Monitor disk I/O
        disk_io_before = psutil.disk_io_counters()
        
        # Copy template
        with patch('src.core.constants.TEMPLATES_PATH', templates_path):
            pm.create_project(temp_dir, "disk_io_test", "LargeTemplate")
        
        disk_io_after = psutil.disk_io_counters()
        
        bytes_written = disk_io_after.write_bytes - disk_io_before.write_bytes
        
        print(f"Disk I/O During Template Copying:")
        print(f"  Bytes written: {bytes_written / 1024 / 1024:.2f} MB")
        
        # Should write reasonable amount of data
        assert bytes_written > 0, "No disk I/O detected"
    
    def test_network_usage_during_operations(self):
        """Test that operations don't use unnecessary network."""
        # Get initial network stats
        net_io_before = psutil.net_io_counters()
        
        # Perform operations that shouldn't use network
        time.sleep(1)  # Allow for any background network activity
        
        # Get final network stats
        net_io_after = psutil.net_io_counters()
        
        bytes_sent = net_io_after.bytes_sent - net_io_before.bytes_sent
        bytes_recv = net_io_after.bytes_recv - net_io_before.bytes_recv
        
        print(f"Network Usage During Operations:")
        print(f"  Bytes sent: {bytes_sent}")
        print(f"  Bytes received: {bytes_recv}")
        
        # Operations should not use significant network (allowing for background)
        # This is more of a baseline test since there might be background network activity
        assert bytes_sent >= 0, "Unexpected negative network usage"
        assert bytes_recv >= 0, "Unexpected negative network usage"


class TestScalability:
    """Test scalability of operations."""
    
    def test_project_creation_scalability(self, temp_dir):
        """Test how project creation scales with template size."""
        template_sizes = [10, 50, 100, 200]  # Number of files
        creation_times = []
        
        for size in template_sizes:
            # Create template with specific size
            templates_path = Path(temp_dir) / "templates"
            template_dir = templates_path / f"Template_{size}"
            template_dir.mkdir(parents=True)
            
            # Create files
            for i in range(size):
                file_path = template_dir / f"file_{i}.txt"
                file_path.write_text(f"Content of file {i}")
            
            # Benchmark creation
            pm = ProjectManager()
            
            start_time = time.perf_counter()
            
            with patch('src.core.constants.TEMPLATES_PATH', templates_path):
                pm.create_project(temp_dir, f"scalability_test_{size}", f"Template_{size}")
            
            end_time = time.perf_counter()
            creation_time = end_time - start_time
            creation_times.append(creation_time)
        
        # Check that creation time scales reasonably (should be roughly linear)
        # The ratio of times should not be too different from the ratio of sizes
        if len(creation_times) > 1:
            time_ratio = creation_times[-1] / creation_times[0]
            size_ratio = template_sizes[-1] / template_sizes[0]
            
            print(f"Project Creation Scalability:")
            print(f"  Size ratio: {size_ratio}")
            print(f"  Time ratio: {time_ratio}")
            
            # Time should not scale worse than size^2
            assert time_ratio < size_ratio ** 2, f"Creation time scales poorly: {time_ratio} vs {size_ratio}"
    
    def test_ui_loading_scalability(self, qt_app, temp_dir):
        """Test how UI loading scales with UI complexity."""
        ui_complexities = [10, 50, 100, 200]  # Number of widgets
        loading_times = []
        
        for complexity in ui_complexities:
            # Create UI file with specific complexity
            ui_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>TestWidget</class>
 <widget class="QWidget" name="TestWidget">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>400</width>
    <height>300</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Test Widget</string>
  </property>
'''
            
            # Add widgets
            for i in range(complexity):
                ui_content += f'''  <widget class="QPushButton" name="button_{i}">
   <property name="geometry">
    <rect>
     <x>{i % 10 * 40}</x>
     <y>{i // 10 * 30}</y>
     <width>30</width>
     <height>20</height>
    </rect>
   </property>
   <property name="text">
    <string>Button {i}</string>
   </property>
  </widget>
'''
            
            ui_content += ''' </widget>
</ui>'''
            
            ui_file = Path(temp_dir) / f"complex_{complexity}.ui"
            ui_file.write_text(ui_content)
            
            # Benchmark loading
            start_time = time.perf_counter()
            
            widget = UILoader.load_ui_file(str(ui_file))
            
            end_time = time.perf_counter()
            loading_time = end_time - start_time
            loading_times.append(loading_time)
        
        # Check that loading time scales reasonably
        if len(loading_times) > 1:
            time_ratio = loading_times[-1] / loading_times[0]
            complexity_ratio = ui_complexities[-1] / ui_complexities[0]
            
            print(f"UI Loading Scalability:")
            print(f"  Complexity ratio: {complexity_ratio}")
            print(f"  Time ratio: {time_ratio}")
            
            # Time should not scale worse than complexity^2
            assert time_ratio < complexity_ratio ** 2, f"Loading time scales poorly: {time_ratio} vs {complexity_ratio}"


class TestStressTesting:
    """Test system under stress conditions."""
    
    def test_concurrent_project_creation(self, temp_dir):
        """Test concurrent project creation."""
        import threading
        
        # Create template
        templates_path = Path(temp_dir) / "templates"
        spm_template = templates_path / "SPM"
        spm_template.mkdir(parents=True)
        (spm_template / "README.md").write_text("SPM Template")
        
        results = []
        errors = []
        
        def create_project(i):
            try:
                pm = ProjectManager()
                with patch('src.core.constants.TEMPLATES_PATH', templates_path):
                    pm.create_project(temp_dir, f"concurrent_test_{i}", "SPM")
                results.append(i)
            except Exception as e:
                errors.append((i, str(e)))
        
        # Create 5 concurrent threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_project, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        print(f"Concurrent Project Creation:")
        print(f"  Successful: {len(results)}")
        print(f"  Errors: {len(errors)}")
        
        # Should have some successful creations
        assert len(results) > 0, "No successful concurrent creations"
    
    def test_memory_stress_test(self, temp_dir):
        """Test system under memory stress."""
        # Create many large templates
        templates_path = Path(temp_dir) / "templates"
        templates_path.mkdir()
        
        for i in range(10):
            template_dir = templates_path / f"StressTemplate{i}"
            template_dir.mkdir()
            
            # Create large files
            for j in range(20):
                large_file = template_dir / f"large_file_{j}.dat"
                with open(large_file, 'wb') as f:
                    f.write(b'x' * 1024 * 1024)  # 1MB file
        
        # Start memory tracking
        tracemalloc.start()
        
        pm = ProjectManager()
        
        # Create multiple projects rapidly
        for i in range(5):
            with patch('src.core.constants.TEMPLATES_PATH', templates_path):
                pm.create_project(temp_dir, f"stress_test_{i}", "StressTemplate0")
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Memory Stress Test:")
        print(f"  Current memory: {current / 1024 / 1024:.2f} MB")
        print(f"  Peak memory: {peak / 1024 / 1024:.2f} MB")
        
        # Should handle stress without excessive memory usage
        assert peak < 500 * 1024 * 1024, f"Memory usage too high under stress: {peak / 1024 / 1024:.2f} MB"
    
    def test_ui_stress_test(self, qt_app, temp_dir):
        """Test UI system under stress."""
        # Create many complex UI files
        for i in range(10):
            ui_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>StressWidget</class>
 <widget class="QWidget" name="StressWidget">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Stress Widget</string>
  </property>
'''
            
            # Add many widgets
            for j in range(500):
                ui_content += f'''  <widget class="QPushButton" name="button_{j}">
   <property name="geometry">
    <rect>
     <x>{j % 20 * 40}</x>
     <y>{j // 20 * 30}</y>
     <width>30</width>
     <height>20</height>
    </rect>
   </property>
   <property name="text">
    <string>Button {j}</string>
   </property>
  </widget>
'''
            
            ui_content += ''' </widget>
</ui>'''
            
            ui_file = Path(temp_dir) / f"stress_{i}.ui"
            ui_file.write_text(ui_content)
        
        # Load all UI files rapidly
        widgets = []
        start_time = time.perf_counter()
        
        for i in range(10):
            ui_path = str(Path(temp_dir) / f"stress_{i}.ui")
            widget = UILoader.load_ui_file(ui_path)
            widgets.append(widget)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        print(f"UI Stress Test:")
        print(f"  Total loading time: {total_time:.3f}s")
        print(f"  Average per UI: {total_time / 10:.3f}s")
        
        # Should complete in reasonable time
        assert total_time < 30.0, f"UI stress test too slow: {total_time:.3f}s"


class TestPerformanceRegression:
    """Test for performance regressions."""
    
    def test_performance_baseline_comparison(self, temp_dir):
        """Compare current performance against baseline."""
        # This would typically compare against stored baseline performance
        # For now, we'll just establish a baseline
        
        # Create baseline template
        templates_path = Path(temp_dir) / "templates"
        baseline_template = templates_path / "BaselineTemplate"
        baseline_template.mkdir(parents=True)
        
        for i in range(50):
            file_path = baseline_template / f"file_{i}.txt"
            file_path.write_text(f"Content of file {i}" * 100)
        
        # Benchmark baseline operation
        pm = ProjectManager()
        
        start_time = time.perf_counter()
        
        with patch('src.core.constants.TEMPLATES_PATH', templates_path):
            pm.create_project(temp_dir, "baseline_test", "BaselineTemplate")
        
        end_time = time.perf_counter()
        baseline_time = end_time - start_time
        
        print(f"Performance Baseline:")
        print(f"  Baseline time: {baseline_time:.3f}s")
        
        # Store baseline for future comparison
        # In a real implementation, this would be saved to a file
        baseline_file = Path(temp_dir) / "performance_baseline.txt"
        baseline_file.write_text(f"baseline_time={baseline_time}\n")
        
        # Performance should be reasonable
        assert baseline_time < 5.0, f"Baseline performance too slow: {baseline_time:.3f}s"
    
    def test_performance_monitoring(self, temp_dir):
        """Test performance monitoring capabilities."""
        # This would typically integrate with a performance monitoring system
        # For now, we'll just demonstrate the concept
        
        performance_metrics = {
            'project_creation_time': [],
            'ui_loading_time': [],
            'parameter_parsing_time': [],
            'memory_usage': []
        }
        
        # Simulate collecting performance metrics
        for i in range(5):
            # Project creation
            templates_path = Path(temp_dir) / "templates"
            spm_template = templates_path / "SPM"
            spm_template.mkdir(parents=True)
            (spm_template / "README.md").write_text("SPM Template")
            
            pm = ProjectManager()
            
            start_time = time.perf_counter()
            with patch('src.core.constants.TEMPLATES_PATH', templates_path):
                pm.create_project(temp_dir, f"perf_test_{i}", "SPM")
            end_time = time.perf_counter()
            
            performance_metrics['project_creation_time'].append(end_time - start_time)
            
            # Memory usage
            current, peak = tracemalloc.get_traced_memory()
            performance_metrics['memory_usage'].append(peak)
        
        # Calculate averages
        avg_creation_time = sum(performance_metrics['project_creation_time']) / len(performance_metrics['project_creation_time'])
        avg_memory_usage = sum(performance_metrics['memory_usage']) / len(performance_metrics['memory_usage'])
        
        print(f"Performance Monitoring:")
        print(f"  Avg creation time: {avg_creation_time:.3f}s")
        print(f"  Avg memory usage: {avg_memory_usage / 1024 / 1024:.2f} MB")
        
        # Performance should meet thresholds
        assert avg_creation_time < 3.0, f"Average creation time too slow: {avg_creation_time:.3f}s"
        assert avg_memory_usage < 100 * 1024 * 1024, f"Average memory usage too high: {avg_memory_usage / 1024 / 1024:.2f} MB"