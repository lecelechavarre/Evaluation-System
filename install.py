#!/usr/bin/env python3
"""
Installation and setup script for Performance Evaluation System.
Run this after extracting the package to set up everything automatically.
"""

import os
import sys
from pathlib import Path
import subprocess
import shutil

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def check_python_version():
    """Check if Python version is 3.10 or higher."""
    print_info("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error(f"Python 3.10+ required. Current: {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_directory_structure():
    """Create necessary directories."""
    print_info("Creating directory structure...")
    
    directories = [
        'data',
        'logs',
        'exports',
        'src',
        'src/templates',
        'tests',
        'tests/fixtures',
        'scripts',
        'backups'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_success(f"Created: {directory}/")
    
    return True

def create_env_file():
    """Create .env file from .env.example."""
    print_info("Setting up environment file...")
    
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if env_file.exists():
        print_warning(".env file already exists, skipping...")
        return True
    
    if not env_example.exists():
        print_warning(".env.example not found, creating default .env...")
        default_env = """# Application Configuration
SECRET_KEY=change-this-to-random-secret-key
FLASK_ENV=development
FLASK_DEBUG=True

# File paths
DATA_DIR=data
LOGS_DIR=logs
EXPORTS_DIR=exports

# Security
SESSION_LIFETIME_HOURS=8
PASSWORD_MIN_LENGTH=8
"""
        with open('.env', 'w') as f:
            f.write(default_env)
    else:
        shutil.copy('.env.example', '.env')
    
    print_success("Created .env file")
    print_warning("⚠ Remember to change SECRET_KEY in .env!")
    return True

def setup_virtual_environment():
    """Create and setup virtual environment."""
    print_info("Setting up virtual environment...")
    
    venv_path = Path('.venv')
    
    if venv_path.exists():
        print_warning("Virtual environment already exists, skipping creation...")
        return True
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
        print_success("Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to create virtual environment")
        return False

def install_dependencies():
    """Install required packages."""
    print_info("Installing dependencies...")
    
    # Determine pip path based on OS
    if sys.platform == 'win32':
        pip_path = Path('.venv/Scripts/pip.exe')
        python_path = Path('.venv/Scripts/python.exe')
    else:
        pip_path = Path('.venv/bin/pip')
        python_path = Path('.venv/bin/python')
    
    # Check if virtual environment exists
    if not python_path.exists():
        print_error("Virtual environment not found. Please delete .venv and run setup again.")
        print_info(f"Expected Python at: {python_path}")
        return False
    
    # Check if requirements.txt exists
    if not Path('requirements.txt').exists():
        print_error("requirements.txt not found!")
        return False
    
    try:
        # Use python -m pip instead of direct pip path (more reliable)
        print_info("Upgrading pip...")
        subprocess.run([str(python_path), '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        print_info("Installing packages from requirements.txt...")
        result = subprocess.run([str(python_path), '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              check=True, capture_output=False)
        
        print_success("All dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        print_info("Try running manually:")
        if sys.platform == 'win32':
            print_info("  .venv\\Scripts\\activate")
        else:
            print_info("  source .venv/bin/activate")
        print_info("  pip install -r requirements.txt")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def initialize_data_files():
    """Initialize empty JSON data files."""
    print_info("Initializing data files...")
    
    data_files = ['data/users.json', 'data/criteria.json', 'data/evaluations.json']
    
    for file_path in data_files:
        path = Path(file_path)
        if not path.exists():
            with open(path, 'w', encoding='utf-8') as f:
                f.write('[]')
            print_success(f"Created: {file_path}")
        else:
            print_warning(f"Already exists: {file_path}")
    
    return True

def create_gitkeep_files():
    """Create .gitkeep files for empty directories."""
    print_info("Creating .gitkeep files...")
    
    directories = ['logs', 'exports', 'tests/fixtures']
    
    for directory in directories:
        gitkeep = Path(directory) / '.gitkeep'
        gitkeep.touch()
    
    print_success("Created .gitkeep files")
    return True

def print_next_steps():
    """Print instructions for next steps."""
    print_header("Installation Complete!")
    
    print(f"\n{Colors.OKGREEN}✓ Setup completed successfully!{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}\n")
    
    if sys.platform == 'win32':
        activate_cmd = ".venv\\Scripts\\activate"
    else:
        activate_cmd = "source .venv/bin/activate"
    
    print(f"  1. Activate virtual environment:")
    print(f"     {Colors.OKCYAN}{activate_cmd}{Colors.ENDC}\n")
    
    print(f"  2. Initialize admin account:")
    print(f"     {Colors.OKCYAN}python scripts/init_admin.py{Colors.ENDC}\n")
    
    print(f"  3. Run the application:")
    print(f"     {Colors.OKCYAN}python src/web_app.py{Colors.ENDC}")
    print(f"     OR")
    print(f"     {Colors.OKCYAN}python src/desktop_app.py{Colors.ENDC}\n")
    
    print(f"  4. Access web app at:")
    print(f"     {Colors.OKCYAN}http://localhost:5000{Colors.ENDC}\n")
    
    print(f"{Colors.WARNING}⚠ Important:{Colors.ENDC}")
    print(f"  • Edit .env and change SECRET_KEY")
    print(f"  • Change default admin password after first login")
    print(f"  • Review security settings before production use\n")

def main():
    """Main installation routine."""
    print_header("Performance Evaluation System - Setup")
    
    print("This script will set up your environment automatically.\n")
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating directory structure", create_directory_structure),
        ("Creating environment file", create_env_file),
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Initializing data files", initialize_data_files),
        ("Creating .gitkeep files", create_gitkeep_files),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print_error(f"\nSetup failed at: {step_name}")
            sys.exit(1)
    
    print_next_steps()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup interrupted by user.{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        sys.exit(1)