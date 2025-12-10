# Battery Simulator Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Battery Simulator application in various environments, from development to production. It covers installation, configuration, monitoring, and troubleshooting.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Environment Setup](#environment-setup)
5. [Monitoring and Logging](#monitoring-and-logging)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)
8. [Security Considerations](#security-considerations)
9. [Performance Tuning](#performance-tuning)
10. [Appendix](#appendix)

## Prerequisites

### System Requirements

- **Operating System**: Windows 10+, Ubuntu 18.04+, macOS 10.14+
- **Processor**: 2 GHz dual-core or better
- **Memory**: 4 GB RAM minimum, 8 GB recommended
- **Storage**: 2 GB free space
- **Display**: 1024x768 resolution minimum

### Software Dependencies

#### Required
- **Python**: 3.8 or higher
- **PyQt6**: 6.5.2 or higher
- **OpenFOAM**: Version 6 or higher (external installation)

#### Optional
- **pyqtgraph**: For advanced plotting
- **matplotlib**: Alternative plotting library
- **Docker**: For containerized deployment

### OpenFOAM Installation

#### Ubuntu/Debian
```bash
# Add OpenFOAM repository
wget -O - https://dl.openfoam.org/gpg.key | sudo apt-key add -
echo "deb https://dl.openfoam.org/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/openfoam.list

# Install OpenFOAM
sudo apt-get update
sudo apt-get install openfoam2206

# Source environment
source /opt/openfoam2206/etc/bashrc
```

#### Windows
1. Download OpenFOAM for Windows from [openfoam.org](https://openfoam.org/download/windows/)
2. Follow installation instructions
3. Add OpenFOAM to PATH environment variable

#### macOS
```bash
# Using Homebrew
brew tap openfoam/openfoam
brew install openfoam

# Source environment
source /usr/local/Cellar/openfoam/2206/etc/bashrc
```

## Installation Methods

### Method 1: Python Package Installation

#### From PyPI (Recommended)
```bash
pip install BatterySimulator
```

#### From Source
```bash
# Clone repository
git clone https://github.com/your-repo/battery-simulator.git
cd battery-simulator

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

### Method 2: Standalone Executable

#### Windows
```bash
# Download executable from releases
# Run installer
BatterySimulator-Setup.exe
```

#### Linux/macOS
```bash
# Download executable
wget https://github.com/your-repo/battery-simulator/releases/latest/BatterySimulator

# Make executable
chmod +x BatterySimulator

# Run
./BatterySimulator
```

### Method 3: Docker Deployment

#### Using Pre-built Image
```bash
# Pull image
docker pull your-repo/battery-simulator:latest

# Run container
docker run -it --rm \
  -p 8080:8080 \
  -v /path/to/data:/app/data \
  your-repo/battery-simulator:latest
```

#### Building Custom Image
```bash
# Build image
docker build -t battery-simulator:custom .

# Run container
docker run -it --rm \
  -p 8080:8080 \
  -v /path/to/data:/app/data \
  battery-simulator:custom
```

### Method 4: Development Installation

#### Clone and Setup
```bash
# Clone repository
git clone https://github.com/your-repo/battery-simulator.git
cd battery-simulator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run application
python src/main.py
```

## Configuration

### Configuration Files

#### Main Configuration (`config.yaml`)
```yaml
application:
  name: "BatterySimulator"
  version: "1.0.0"
  debug: false

paths:
  data_dir: "/var/lib/batterysimulator"
  log_dir: "/var/log/batterysimulator"
  config_dir: "/etc/batterysimulator"
  templates_dir: "/usr/share/batterysimulator/templates"

openfoam:
  installation_path: "/opt/openfoam2206"
  solver_path: "/usr/local/bin"
  parallel: true
  np: 4

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "/var/log/batterysimulator/app.log"
  max_size: "10MB"
  backup_count: 5

ui:
  theme: "default"
  language: "en"
  window_size: [1200, 800]
  recent_projects_limit: 5

performance:
  memory_limit: "2GB"
  timeout: 300
  cache_size: 100
```

#### Environment Variables
```bash
# Application settings
export BATTERY_SIM_DEBUG=true
export BATTERY_SIM_CONFIG_PATH=/etc/batterysimulator/config.yaml

# OpenFOAM settings
export WM_PROJECT_DIR=/opt/openfoam2206
export FOAM_INST_DIR=/opt/openfoam2206

# UI settings
export BATTERY_SIM_UI_MODE=auto_detect
export BATTERY_SIM_UI_PATH=/custom/ui/path

# Logging settings
export BATTERY_SIM_LOG_LEVEL=DEBUG
export BATTERY_SIM_LOG_PATH=/var/log/batterysimulator
```

### Database Configuration

#### SQLite (Default)
```yaml
database:
  type: "sqlite"
  path: "/var/lib/batterysimulator/batterysimulator.db"
```

#### PostgreSQL
```yaml
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  name: "batterysimulator"
  user: "batterysimulator"
  password: "secure_password"
```

### Network Configuration

#### Firewall Rules
```bash
# Allow application port
sudo ufw allow 8080/tcp

# Allow OpenFOAM ports (if using parallel execution)
sudo ufw allow 127.0.0.1 port 12345:12350/tcp
```

## Environment Setup

### Production Environment

#### User and Permissions
```bash
# Create application user
sudo useradd -r -s /bin/false batterysimulator

# Create directories
sudo mkdir -p /opt/batterysimulator
sudo mkdir -p /var/lib/batterysimulator
sudo mkdir -p /var/log/batterysimulator
sudo mkdir -p /etc/batterysimulator

# Set permissions
sudo chown -R batterysimulator:batterysimulator /opt/batterysimulator
sudo chown -R batterysimulator:batterysimulator /var/lib/batterysimulator
sudo chown -R batterysimulator:batterysimulator /var/log/batterysimulator
sudo chmod -R 755 /opt/batterysimulator
sudo chmod -R 755 /var/lib/batterysimulator
```

#### System Service
```bash
# Create systemd service file
sudo tee /etc/systemd/system/batterysimulator.service << EOF
[Unit]
Description=Battery Simulator Service
After=network.target

[Service]
Type=simple
User=batterysimulator
Group=batterysimulator
ExecStart=/opt/batterysimulator/BatterySimulator
Restart=always
RestartSec=3
Environment=PATH=/opt/openfoam2206/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable batterysimulator
sudo systemctl start batterysimulator
```

#### Reverse Proxy (Optional)
```bash
# Install nginx
sudo apt-get install nginx

# Create nginx configuration
sudo tee /etc/nginx/sites-available/batterysimulator << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/batterysimulator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Development Environment

#### Virtual Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

#### IDE Configuration

##### VS Code
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=100"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

##### PyCharm
1. Open Project Settings
2. Set Python interpreter to virtual environment
3. Configure code style:
   - Line length: 100
   - Formatter: Black
   - Linter: flake8, mypy
4. Set up run configuration for `src/main.py`

## Monitoring and Logging

### Log Files

#### Application Logs
```bash
# View application logs
tail -f /var/log/batterysimulator/app.log

# View error logs
grep ERROR /var/log/batterysimulator/app.log

# View debug logs
grep DEBUG /var/log/batterysimulator/app.log
```

#### System Logs
```bash
# View systemd service logs
sudo journalctl -u batterysimulator -f

# View OpenFOAM logs
tail -f /var/log/batterysimulator/openfoam.log
```

### Monitoring Tools

#### Prometheus Metrics
```yaml
# Add to configuration
monitoring:
  prometheus:
    enabled: true
    port: 9090
    path: /metrics
```

#### Health Check Endpoint
```bash
# Check application health
curl http://localhost:8080/health

# Expected response
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2024-01-01T00:00:00Z",
    "checks": {
        "database": "ok",
        "openfoam": "ok",
        "disk_space": "ok"
    }
}
```

#### Performance Monitoring
```python
# Enable performance monitoring
import cProfile
import pstats

# Profile application startup
cProfile.run('import src.main; src.main.main()', 'profile.stats')
stats = pstats.Stats('profile.stats')
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Alerting

#### Systemd Notifications
```bash
# Check service status
sudo systemctl status batterysimulator

# Restart on failure
sudo systemctl restart batterysimulator

# View recent restarts
sudo journalctl -u batterysimulator --no-pager | grep -i restart
```

#### Custom Monitoring Script
```bash
#!/bin/bash
# monitor.sh

APP_URL="http://localhost:8080/health"
LOG_FILE="/var/log/batterysimulator/monitor.log"

check_app() {
    if curl -s $APP_URL > /dev/null; then
        echo "$(date): Application is healthy" >> $LOG_FILE
        return 0
    else
        echo "$(date): Application is unhealthy" >> $LOG_FILE
        return 1
    fi
}

# Check every 5 minutes
while true; do
    if ! check_app; then
        # Send alert (email, Slack, etc.)
        echo "Application is down!" | mail -s "Alert" admin@example.com
        # Restart service
        sudo systemctl restart batterysimulator
    fi
    sleep 300
done
```

## Troubleshooting

### Common Issues

#### 1. PyQt6 Import Error
**Symptoms**: `ModuleNotFoundError: No module named 'PyQt6'`

**Solutions**:
```bash
# Reinstall PyQt6
pip uninstall PyQt6
pip install PyQt6==6.5.2

# Check Python version compatibility
python --version
pip show PyQt6
```

#### 2. OpenFOAM Not Found
**Symptoms**: `Error: OpenFOAM not found in PATH`

**Solutions**:
```bash
# Check OpenFOAM installation
which icoFoam
echo $WM_PROJECT_DIR

# Source OpenFOAM environment
source /opt/openfoam2206/etc/bashrc

# Add to ~/.bashrc
echo "source /opt/openfoam2206/etc/bashrc" >> ~/.bashrc
```

#### 3. Permission Denied
**Symptoms**: `PermissionError: [Errno 13] Permission denied`

**Solutions**:
```bash
# Check file permissions
ls -la /path/to/file

# Fix permissions
sudo chown -R $USER:$USER /path/to/directory
sudo chmod -R 755 /path/to/directory

# For system-wide installation
sudo chown -R batterysimulator:batterysimulator /opt/batterysimulator
```

#### 4. Port Already in Use
**Symptoms**: `OSError: [Errno 98] Address already in use`

**Solutions**:
```bash
# Find process using port
sudo lsof -i :8080
sudo netstat -tlnp | grep :8080

# Kill process
sudo kill -9 <PID>

# Or change application port in config
```

#### 5. Memory Issues
**Symptoms**: `MemoryError` or application crashes

**Solutions**:
```bash
# Check available memory
free -h
top

# Reduce memory usage in config
# Set memory_limit to lower value
# Reduce cache_size
# Limit concurrent processes
```

### Debug Mode

#### Enable Debug Logging
```bash
# Set environment variable
export BATTERY_SIM_DEBUG=true

# Or modify config
logging:
  level: "DEBUG"
```

#### Run with Verbose Output
```bash
# Run application with verbose output
python src/main.py --verbose

# Run with profiling
python -m cProfile -s cumulative src/main.py
```

#### OpenFOAM Debugging
```bash
# Enable OpenFOAM debug output
export WM_NCOMPPROCS=1
export FOAM_SIGFPE=1

# Run solver with debug flags
icoFoam -debug
```

### Log Analysis

#### Parse Application Logs
```python
import re
from collections import Counter

def analyze_logs(log_file):
    errors = []
    warnings = []
    
    with open(log_file, 'r') as f:
        for line in f:
            if 'ERROR' in line:
                errors.append(line)
            elif 'WARNING' in line:
                warnings.append(line)
    
    print(f"Total errors: {len(errors)}")
    print(f"Total warnings: {len(warnings)}")
    
    # Find most common errors
    error_patterns = [re.search(r'ERROR: (.+)', e).group(1) for e in errors if re.search(r'ERROR: (.+)', e)]
    print("Most common errors:", Counter(error_patterns).most_common(5))

analyze_logs('/var/log/batterysimulator/app.log')
```

#### Performance Analysis
```python
import time
import psutil

def monitor_performance():
    process = psutil.Process()
    
    while True:
        cpu_usage = process.cpu_percent()
        memory_info = process.memory_info()
        
        print(f"CPU: {cpu_usage}%")
        print(f"Memory: {memory_info.rss / 1024 / 1024:.2f} MB")
        
        time.sleep(5)

monitor_performance()
```

## Maintenance

### Regular Tasks

#### Log Rotation
```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/batterysimulator << EOF
/var/log/batterysimulator/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 batterysimulator batterysimulator
    postrotate
        systemctl reload batterysimulator
    endscript
}
EOF
```

#### Database Maintenance
```bash
# Backup database
sqlite3 /var/lib/batterysimulator/batterysimulator.db ".backup backup.db"

# Vacuum database (SQLite)
sqlite3 /var/lib/batterysimulator/batterysimulator.db "VACUUM;"

# Clean old data
sqlite3 /var/lib/batterysimulator/batterysimulator.db "DELETE FROM logs WHERE timestamp < datetime('now', '-30 days');"
```

#### Update Application
```bash
# Stop service
sudo systemctl stop batterysimulator

# Backup current installation
sudo cp -r /opt/batterysimulator /opt/batterysimulator.backup

# Update application
# Method 1: From package
pip install --upgrade BatterySimulator

# Method 2: From source
git pull
pip install -e .

# Start service
sudo systemctl start batterysimulator

# Verify
sudo systemctl status batterysimulator
```

### Backup and Recovery

#### Full System Backup
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/batterysimulator"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="batterysimulator_$DATE.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
tar -czf $BACKUP_DIR/$BACKUP_FILE \
    /opt/batterysimulator \
    /var/lib/batterysimulator \
    /var/log/batterysimulator \
    /etc/batterysimulator

# Keep last 10 backups
ls -t $BACKUP_DIR/batterysimulator_*.tar.gz | tail -n +11 | xargs -r rm

echo "Backup completed: $BACKUP_DIR/$BACKUP_FILE"
EOF

chmod +x backup.sh

# Schedule backup
echo "0 2 * * * /path/to/backup.sh" | sudo crontab -
```

#### Recovery Procedure
```bash
# Stop service
sudo systemctl stop batterysimulator

# Restore from backup
tar -xzf /backup/batterysimulator/batterysimulator_YYYYMMDD_HHMMSS.tar.gz -C /

# Fix permissions
sudo chown -R batterysimulator:batterysimulator /opt/batterysimulator
sudo chown -R batterysimulator:batterysimulator /var/lib/batterysimulator

# Start service
sudo systemctl start batterysimulator

# Verify
sudo systemctl status batterysimulator
```

## Security Considerations

### File Permissions
```bash
# Set secure permissions
sudo chmod 644 /etc/batterysimulator/config.yaml
sudo chmod 750 /var/lib/batterysimulator
sudo chmod 750 /var/log/batterysimulator

# Set ownership
sudo chown root:batterysimulator /etc/batterysimulator/config.yaml
sudo chown -R batterysimulator:batterysimulator /var/lib/batterysimulator
sudo chown -R batterysimulator:batterysimulator /var/log/batterysimulator
```

### Network Security
```bash
# Use HTTPS
# Configure SSL/TLS certificates
sudo apt-get install certbot
sudo certbot certonly --standalone -d your-domain.com

# Update nginx configuration for HTTPS
```

### Application Security
```python
# Input validation
import re

def validate_project_name(name):
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        raise ValueError("Invalid project name")
    if len(name) > 50:
        raise ValueError("Project name too long")
    return name

# Secure file operations
import os
import tempfile

def secure_file_write(content, filename):
    # Use temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        temp_file.write(content.encode('utf-8'))
        temp_file.close()
        
        # Atomic move
        os.rename(temp_file.name, filename)
    except Exception:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise
```

## Performance Tuning

### Application Optimization
```yaml
# Configuration settings
performance:
  memory_limit: "4GB"  # Increase for larger simulations
  timeout: 600         # Increase for longer simulations
  cache_size: 200      # Increase for better performance
  parallel_processing: true
  max_concurrent_jobs: 4
```

### OpenFOAM Optimization
```bash
# Set environment variables
export WM_NCOMPPROCS=8  # Number of compilation processes
export WM_MPLIB=SYSTEMOPENMPI  # Use system MPI

# Optimize solver settings
# In controlDict
application     icoFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         100;
deltaT          0.01;
writeControl    time;
writeInterval   1;
purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
```

### System Optimization
```bash
# Increase file descriptor limit
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize network settings
sudo sysctl -w net.core.somaxconn=1024
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=2048

# Use SSD storage for better I/O performance
# Allocate sufficient swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Appendix

### Configuration Reference

#### Complete Configuration File
```yaml
# Complete configuration example
application:
  name: "BatterySimulator"
  version: "1.0.0"
  debug: false
  log_level: "INFO"

paths:
  data_dir: "/var/lib/batterysimulator"
  log_dir: "/var/log/batterysimulator"
  config_dir: "/etc/batterysimulator"
  templates_dir: "/usr/share/batterysimulator/templates"
  ui_dir: "/usr/share/batterysimulator/ui"

openfoam:
  installation_path: "/opt/openfoam2206"
  solver_path: "/usr/local/bin"
  parallel: true
  np: 4
  environment:
    WM_PROJECT_DIR: "/opt/openfoam2206"
    FOAM_INST_DIR: "/opt/openfoam2206"

database:
  type: "sqlite"
  path: "/var/lib/batterysimulator/batterysimulator.db"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "/var/log/batterysimulator/app.log"
  max_size: "10MB"
  backup_count: 5
  console: true

ui:
  theme: "default"
  language: "en"
  window_size: [1200, 800]
  recent_projects_limit: 5
  auto_save_interval: 300

performance:
  memory_limit: "2GB"
  timeout: 300
  cache_size: 100
  parallel_processing: true
  max_concurrent_jobs: 4

monitoring:
  enabled: true
  prometheus:
    enabled: true
    port: 9090
    path: /metrics
  health_check:
    enabled: true
    path: /health
    interval: 30

security:
  file_permissions: "644"
  directory_permissions: "755"
  user: "batterysimulator"
  group: "batterysimulator"

network:
  host: "0.0.0.0"
  port: 8080
  ssl:
    enabled: false
    cert_file: ""
    key_file: ""

notifications:
  email:
    enabled: false
    smtp_server: "localhost"
    smtp_port: 587
    username: ""
    password: ""
  slack:
    enabled: false
    webhook_url: ""
```

### Command Reference

#### System Commands
```bash
# Service management
sudo systemctl start batterysimulator
sudo systemctl stop batterysimulator
sudo systemctl restart batterysimulator
sudo systemctl status batterysimulator
sudo systemctl enable batterysimulator
sudo systemctl disable batterysimulator

# Log viewing
sudo journalctl -u batterysimulator -f
tail -f /var/log/batterysimulator/app.log

# Process management
ps aux | grep batterysimulator
kill -9 <PID>
```

#### Application Commands
```bash
# Run application
BatterySimulator
python src/main.py

# Run with options
python src/main.py --ui-mode auto_detect
python src/main.py --ui-path /custom/ui/path
python src/main.py --no-fallback

# Run tests
pytest tests/
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Build package
python -m build
pip install dist/BatterySimulator-*.whl

# Create executable
pyinstaller --onefile --windowed src/main.py
```

#### OpenFOAM Commands
```bash
# Check installation
which icoFoam
foamInstallationTest

# Run solver
icoFoam
icoFoam -parallel

# Clean case
foamCleanTutorials

# Generate mesh
blockMesh
topoSet
splitMeshRegions -cellZones -overwrite

# Post-process
paraFoam
```

### Troubleshooting Checklist

#### Application Won't Start
- [ ] Check Python version compatibility
- [ ] Verify PyQt6 installation
- [ ] Check OpenFOAM environment
- [ ] Review application logs
- [ ] Check file permissions
- [ ] Verify configuration file syntax

#### OpenFOAM Integration Issues
- [ ] Verify OpenFOAM installation
- [ ] Check environment variables
- [ ] Test solver manually
- [ ] Check case directory structure
- [ ] Verify template files

#### Performance Problems
- [ ] Check system resources
- [ ] Review memory usage
- [ ] Optimize OpenFOAM settings
- [ ] Check for memory leaks
- [ ] Monitor CPU usage
- [ ] Review database performance

#### UI Issues
- [ ] Check PyQt6 version
- [ ] Verify .ui files exist
- [ ] Test fallback mechanism
- [ ] Check display settings
- [ ] Review UI configuration

### Support Resources

#### Documentation
- [Project README](README.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [API Documentation](docs/api/)
- [User Guide](docs/user-guide.md)

#### Community
- [GitHub Issues](https://github.com/your-repo/battery-simulator/issues)
- [Discussions](https://github.com/your-repo/battery-simulator/discussions)
- [Wiki](https://github.com/your-repo/battery-simulator/wiki)

#### Professional Support
- [Commercial Support](https://your-company.com/support)
- [Training](https://your-company.com/training)
- [Consulting](https://your-company.com/consulting)

### Version History

#### v1.0.0 (2024-01-01)
- Initial release
- Core functionality implemented
- OpenFOAM integration
- UI loading system
- Cross-platform support

#### v1.1.0 (2024-02-01)
- Performance improvements
- Bug fixes
- Enhanced logging
- Better error handling

#### v1.2.0 (2024-03-01)
- New UI themes
- Advanced configuration options
- Monitoring and alerting
- Docker support

### License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.

### Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Authors

- [Your Name](https://github.com/your-username) - Initial work - [Your Organization](https://your-organization.com)

See also the list of [contributors](https://github.com/your-repo/battery-simulator/contributors) who participated in this project.

### Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

---

For more information, visit our [GitHub repository](https://github.com/your-repo/battery-simulator) or contact us at [support@your-organization.com](mailto:support@your-organization.com).