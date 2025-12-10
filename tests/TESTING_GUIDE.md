# Battery Simulator Testing Guide

This document provides comprehensive guidance on testing the Battery Simulator Python implementation, including test organization, running tests, coverage analysis, and best practices.

## Table of Contents

1. [Test Organization](#test-organization)
2. [Running Tests](#running-tests)
3. [Test Categories](#test-categories)
4. [Coverage Analysis](#coverage-analysis)
5. [Performance Testing](#performance-testing)
6. [CI/CD Integration](#cicd-integration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Test Organization

The test suite is organized into the following structure:

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests by module
│   ├── test_core_application.py    # Core application tests
│   ├── test_gui_components.py      # GUI component tests
│   ├── test_openfoam_integration.py # OpenFOAM integration tests
│   └── test_utils_components.py     # Utility component tests
├── integration/                # Integration tests
│   └── test_workflows.py       # End-to-end workflow tests
└── performance/                # Performance tests
    └── test_benchmarks.py      # Performance benchmarks
```

### Test Categories

#### Unit Tests (`tests/unit/`)

Unit tests focus on individual components in isolation:

- **Core Application Tests**: Test the main application logic, project creation, and management
- **GUI Component Tests**: Test UI components, signal/slot connections, and widget behavior
- **OpenFOAM Integration Tests**: Test process control, solver management, and subprocess handling
- **Utility Component Tests**: Test template management, parameter parsing, and file operations

#### Integration Tests (`tests/integration/`)

Integration tests validate component interactions:

- **Workflow Tests**: Test complete end-to-end workflows
- **Project Creation Workflow**: Test project creation from start to finish
- **Simulation Execution Workflow**: Test simulation setup and execution
- **UI Loading Workflow**: Test UI loading and switching
- **Error Handling Workflow**: Test error propagation and recovery

#### Performance Tests (`tests/performance/`)

Performance tests measure system performance:

- **Benchmark Tests**: Measure execution time of critical operations
- **Memory Usage Tests**: Monitor memory consumption and detect leaks
- **Scalability Tests**: Test performance with increasing load
- **Stress Tests**: Test system under extreme conditions

## Running Tests

### Using the Test Runner Script

The project includes a comprehensive test runner script:

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --performance

# Run tests with coverage
python run_tests.py --coverage

# Run tests in parallel
python run_tests.py --parallel

# Run tests for CI/CD
python run_tests.py --ci

# Run specific test file
python run_tests.py --test-file test_core_application.py

# Run tests matching pattern
python run_tests.py --test-pattern "test_project_creation"
```

### Using pytest Directly

You can also run tests directly with pytest:

```bash
# Run all tests
pytest src/tests/

# Run specific test category
pytest src/tests/unit/
pytest src/tests/integration/
pytest src/tests/performance/

# Run with verbose output
pytest src/tests/ -v

# Run specific test
pytest src/tests/unit/test_core_application.py::test_project_creation

# Run tests with markers
pytest src/tests/ -m "unit"
pytest src/tests/ -m "integration"
pytest src/tests/ -m "performance"

# Run tests excluding slow ones
pytest src/tests/ -m "not slow"

# Run with coverage
pytest src/tests/ --cov=src --cov-report=html
```

### Test Configuration

The test runner supports various configuration options:

```bash
# Fast mode (skip slow tests)
python run_tests.py --fast

# Verbose output
python run_tests.py --verbose

# Debug mode
python run_tests.py --debug

# Custom output directory
python run_tests.py --output-dir /custom/reports/path

# Multiple markers
python run_tests.py --marker unit --marker ui
python run_tests.py --exclude-marker slow --exclude-marker openfoam
```

## Coverage Analysis

### Coverage Requirements

The project aims for comprehensive test coverage:

- **Unit Tests**: >90% code coverage
- **Integration Tests**: All critical workflows
- **Performance Tests**: Critical path coverage
- **Cross-Platform Tests**: All supported platforms

### Running Coverage Analysis

```bash
# Generate coverage report
python run_tests.py --coverage

# Generate HTML coverage report
python run_tests.py --coverage --coverage-html

# Generate XML coverage report (for CI/CD)
python run_tests.py --coverage --coverage-xml

# View coverage report
open test_reports/coverage_html/index.html
```

### Coverage Configuration

Coverage is configured to:

- Include source files in `src/` directory
- Exclude test files (`*/tests/*`, `*/test_*`, `*/conftest.py`)
- Generate multiple report formats (terminal, HTML, XML)
- Track line coverage and missing lines

## Performance Testing

### Performance Test Categories

1. **Benchmark Tests**: Measure execution time of critical operations
2. **Memory Tests**: Monitor memory usage and detect leaks
3. **Scalability Tests**: Test performance scaling with load
4. **Stress Tests**: Test system under extreme conditions

### Running Performance Tests

```bash
# Run performance tests
python run_tests.py --performance

# Run specific performance benchmarks
pytest src/tests/performance/ -v

# Run memory usage tests
pytest src/tests/performance/test_benchmarks.py::TestMemoryUsage -v

# Run scalability tests
pytest src/tests/performance/test_benchmarks.py::TestScalability -v
```

### Performance Metrics

Performance tests measure:

- **Execution Time**: Time taken for critical operations
- **Memory Usage**: Peak memory consumption and leaks
- **CPU Usage**: CPU utilization during operations
- **Disk I/O**: File operation performance
- **Network Usage**: Network activity (should be minimal)

### Performance Thresholds

The project defines performance thresholds:

- **Project Creation**: < 5 seconds for large projects
- **UI Loading**: < 1 second for complex UIs
- **Parameter Parsing**: < 0.5 seconds for large files
- **Memory Usage**: < 100 MB for typical operations
- **Memory Leaks**: < 10 MB increase over time

## CI/CD Integration

### GitHub Actions Integration

The project includes GitHub Actions workflows for automated testing:

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest coverage pytest-cov pytest-xdist
    
    - name: Run tests
      run: python run_tests.py --ci
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v1
      with:
        file: ./test_reports/coverage.xml
```

### CI/CD Test Configuration

CI/CD mode enables:

- Fast test execution (skip slow tests)
- Coverage reporting
- JUnit XML output for CI systems
- HTML coverage reports
- Performance baseline comparison

### Running CI Tests

```bash
# Run tests in CI mode
python run_tests.py --ci

# This enables:
# - Fast mode (skip slow tests)
# - Coverage reporting
# - JUnit XML output
# - HTML coverage reports
```

## Best Practices

### Writing Tests

1. **Use Descriptive Test Names**
   ```python
   def test_project_creation_with_valid_template():
       # Good: Describes what's being tested
   
   def test_create_project():
       # Bad: Too generic
   ```

2. **Follow AAA Pattern**
   ```python
   def test_project_creation():
       # Arrange: Set up test data
       temp_dir = tempfile.mkdtemp()
       
       # Act: Execute the operation
       result = project_manager.create_project(temp_dir, "test", "SPM")
       
       # Assert: Verify the result
       assert result is True
       assert Path(temp_dir / "test").exists()
   ```

3. **Use Fixtures for Common Setup**
   ```python
   @pytest.fixture
   def mock_project(temp_dir):
       # Common setup code
       return create_test_project(temp_dir)
   ```

4. **Test Both Success and Failure Paths**
   ```python
   def test_project_creation_success(mock_templates):
       # Test successful creation
   
   def test_project_creation_failure_invalid_template():
       # Test failure with invalid template
   ```

5. **Use Parametrized Tests for Variations**
   ```python
   @pytest.mark.parametrize("module", ["SPM", "halfCell", "fullCell"])
   def test_project_creation_different_modules(module, temp_dir):
       # Test with different modules
   ```

### Test Organization

1. **Group Related Tests**
   - Use test classes for related functionality
   - Use descriptive test method names
   - Group setup code in fixtures

2. **Use Markers for Categorization**
   ```python
   @pytest.mark.unit
   def test_unit_functionality():
       pass
   
   @pytest.mark.integration
   def test_integration_functionality():
       pass
   
   @pytest.mark.slow
   def test_slow_operation():
       pass
   ```

3. **Separate Test Data**
   - Use fixtures for test data
   - Keep test data separate from test logic
   - Use temporary directories for file operations

### Mocking and Stubbing

1. **Mock External Dependencies**
   ```python
   @patch('subprocess.run')
   def test_process_execution(mock_run):
       mock_run.return_value.returncode = 0
       # Test code
   ```

2. **Use Real Objects When Possible**
   - Mock only when necessary
   - Use real objects for internal dependencies
   - Mock external systems (files, network, subprocess)

3. **Verify Mock Interactions**
   ```python
   mock_process.start_process.assert_called_once_with(command)
   ```

### Performance Testing

1. **Measure Real Performance**
   - Use `time.perf_counter()` for accurate timing
   - Run multiple iterations for statistical significance
   - Measure both average and worst-case performance

2. **Test with Realistic Data**
   - Use data sizes similar to production
   - Test with complex UI files
   - Test with large parameter files

3. **Monitor Resource Usage**
   - Track memory usage
   - Monitor CPU usage
   - Check for resource leaks

## Troubleshooting

### Common Issues

1. **PyQt6 Import Errors**
   ```bash
   # Install PyQt6
   pip install PyQt6
   
   # Or install all dependencies
   pip install -r requirements.txt
   ```

2. **OpenFOAM Integration Issues**
   ```bash
   # Check OpenFOAM installation
   which icoFoam
   
   # Set environment variables
   export WM_PROJECT_DIR=/path/to/openfoam
   ```

3. **Coverage Issues**
   ```bash
   # Install coverage tools
   pip install coverage pytest-cov
   
   # Check coverage configuration
   python run_tests.py --coverage --verbose
   ```

4. **Parallel Test Issues**
   ```bash
   # Install pytest-xdist
   pip install pytest-xdist
   
   # Run tests sequentially for debugging
   python run_tests.py --parallel=false
   ```

### Debugging Tests

1. **Verbose Output**
   ```bash
   python run_tests.py --verbose
   pytest src/tests/ -v
   ```

2. **Debug Mode**
   ```bash
   python run_tests.py --debug
   pytest src/tests/ -s -v
   ```

3. **Run Single Test**
   ```bash
   pytest src/tests/unit/test_core_application.py::test_specific_function -v -s
   ```

4. **Check Test Reports**
   ```bash
   # View test reports
   ls test_reports/
   
   # View coverage report
   open test_reports/coverage_html/index.html
   
   # View test report
   cat test_reports/test_report.json
   ```

### Performance Issues

1. **Slow Tests**
   ```bash
   # Run in fast mode
   python run_tests.py --fast
   
   # Skip slow tests
   pytest src/tests/ -m "not slow"
   ```

2. **Memory Issues**
   ```bash
   # Monitor memory usage
   pytest src/tests/performance/test_benchmarks.py::TestMemoryUsage -v
   
   # Check for memory leaks
   pytest src/tests/performance/test_benchmarks.py::TestMemoryUsage::test_memory_leak_detection -v
   ```

3. **Resource Issues**
   ```bash
   # Check resource usage
   pytest src/tests/performance/test_benchmarks.py::TestSystemResourceUsage -v
   ```

### CI/CD Issues

1. **Test Failures in CI**
   ```bash
   # Run CI mode locally
   python run_tests.py --ci
   
   # Check for platform-specific issues
   python run_tests.py --verbose
   ```

2. **Coverage Reporting Issues**
   ```bash
   # Check coverage configuration
   python run_tests.py --coverage --verbose
   
   # Verify coverage files
   ls test_reports/
   ```

3. **Performance Regression**
   ```bash
   # Run performance tests
   python run_tests.py --performance
   
   # Compare with baseline
   python run_tests.py --performance --verbose
   ```

## Test Data Management

### Test Data Organization

Test data is organized as follows:

```
tests/
├── data/                   # Static test data files
│   ├── ui_files/          # Sample UI files
│   ├── parameter_files/   # Sample parameter files
│   └── templates/         # Sample template files
└── conftest.py            # Test configuration and fixtures
```

### Creating Test Data

1. **UI Files**: Create minimal UI files for testing
2. **Parameter Files**: Create sample OpenFOAM parameter files
3. **Templates**: Create sample project templates
4. **Fixtures**: Use pytest fixtures for dynamic test data

### Test Data Cleanup

Tests automatically clean up temporary files:

```python
@pytest.fixture
def temp_dir():
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)
```

## Continuous Improvement

### Test Metrics

Track these metrics to improve test quality:

1. **Coverage Percentage**: Aim for >90% coverage
2. **Test Execution Time**: Minimize test runtime
3. **Test Reliability**: Reduce flaky tests
4. **Performance Trends**: Monitor performance over time
5. **Bug Detection**: Track bugs caught by tests

### Regular Maintenance

1. **Review Test Coverage**: Regularly check coverage reports
2. **Update Test Data**: Keep test data current
3. **Optimize Slow Tests**: Identify and optimize slow tests
4. **Fix Flaky Tests**: Investigate and fix unreliable tests
5. **Add New Tests**: Add tests for new features and bug fixes

### Test Review Process

1. **Code Reviews**: Include tests in code reviews
2. **Coverage Checks**: Verify coverage requirements
3. **Performance Checks**: Ensure performance standards
4. **Documentation**: Keep test documentation updated

## Conclusion

This testing guide provides comprehensive guidance for testing the Battery Simulator Python implementation. By following these practices, you can ensure high-quality, reliable code that meets performance and functionality requirements.

For additional questions or issues, refer to:

- [Project README](../README.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [GitHub Issues](https://github.com/your-repo/issues)
- [Contributing Guidelines](CONTRIBUTING.md)