#!/usr/bin/env python3
"""
Quick Fix Script - Resolve common setup issues
Run this if you're getting errors about missing modules or config.
"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("  Performance Evaluation System - Quick Fix")
print("=" * 70)
print()

# Step 1: Check if we're in the right directory
print("Step 1: Checking directory structure...")
expected_dirs = ['src', 'data', 'logs', 'exports']
missing_dirs = []

for dir_name in expected_dirs:
    if not Path(dir_name).exists():
        missing_dirs.append(dir_name)
        print(f"  ✗ Missing: {dir_name}/")
    else:
        print(f"  ✓ Found: {dir_name}/")

if missing_dirs:
    print(f"\nCreating missing directories...")
    for dir_name in missing_dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created: {dir_name}/")

# Step 2: Create __init__.py if missing
print("\nStep 2: Checking __init__.py files...")
init_files = ['src/__init__.py', 'tests/__init__.py']

for init_file in init_files:
    path = Path(init_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with open(path, 'w') as f:
            f.write("# Package initialization\n")
        print(f"  ✓ Created: {init_file}")
    else:
        print(f"  ✓ Exists: {init_file}")

# Step 3: Check data files
print("\nStep 3: Checking data files...")
data_files = ['data/users.json', 'data/criteria.json', 'data/evaluations.json']

for data_file in data_files:
    path = Path(data_file)
    if not path.exists():
        with open(path, 'w', encoding='utf-8') as f:
            f.write('[]')
        print(f"  ✓ Created: {data_file}")
    else:
        print(f"  ✓ Exists: {data_file}")

# Step 4: Check .env file
print("\nStep 4: Checking .env file...")
env_file = Path('.env')

if not env_file.exists():
    print("  ✗ .env file missing, creating default...")
    with open('.env', 'w') as f:
        f.write("""# Application Configuration
SECRET_KEY=change-this-to-random-secret-key-NOW
FLASK_ENV=development
FLASK_DEBUG=True

# File paths
DATA_DIR=data
LOGS_DIR=logs
EXPORTS_DIR=exports

# Security
SESSION_LIFETIME_HOURS=8
PASSWORD_MIN_LENGTH=8
""")
    print("  ✓ Created: .env")
    print("  ⚠ WARNING: Change SECRET_KEY before production!")
else:
    print("  ✓ Exists: .env")

# Step 5: Check critical source files
print("\nStep 5: Checking critical source files...")
critical_files = [
    'src/config.py',
    'src/file_store.py',
    'src/auth.py',
    'src/models.py',
    'src/web_app.py'
]

missing_files = []
for file_path in critical_files:
    if not Path(file_path).exists():
        missing_files.append(file_path)
        print(f"  ✗ Missing: {file_path}")
    else:
        print(f"  ✓ Found: {file_path}")

if missing_files:
    print(f"\n  ⚠ WARNING: {len(missing_files)} critical files are missing!")
    print("  You must copy these files from the artifacts.")
    print("\n  Missing files:")
    for file_path in missing_files:
        print(f"    - {file_path}")

# Step 6: Test imports
print("\nStep 6: Testing imports...")

# Add src to path for testing
src_path = Path('src').absolute()
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

test_imports = [
    ('flask', 'Flask'),
    ('pandas', 'Pandas'),
    ('bcrypt', 'Bcrypt'),
    ('filelock', 'FileLock'),
]

for module_name, display_name in test_imports:
    try:
        __import__(module_name)
        print(f"  ✓ {display_name} installed")
    except ImportError:
        print(f"  ✗ {display_name} NOT installed")

# Test src imports if files exist
if Path('src/config.py').exists():
    try:
        import config
        print(f"  ✓ src.config imports OK")
    except Exception as e:
        print(f"  ✗ src.config import failed: {e}")
else:
    print(f"  ⚠ Cannot test src.config (file missing)")

# Step 7: Check virtual environment
print("\nStep 7: Checking virtual environment...")
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("  ✓ Virtual environment is ACTIVE")
else:
    print("  ✗ Virtual environment is NOT active")
    print("\n  Activate it with:")
    if sys.platform == 'win32':
        print("    .venv\\Scripts\\activate")
    else:
        print("    source .venv/bin/activate")

# Summary
print("\n" + "=" * 70)
print("  SUMMARY")
print("=" * 70)

if not missing_files and not missing_dirs:
    print("\n✓ Basic setup looks good!")
    print("\nNext steps:")
    print("  1. Make sure virtual environment is activated")
    print("  2. Install dependencies: pip install -r requirements.txt")
    print("  3. Initialize admin: python scripts/init_admin.py")
    print("  4. Run app: python src/web_app.py")
else:
    print("\n✗ Issues found that need attention:")
    if missing_dirs:
        print(f"  - {len(missing_dirs)} directories were missing (now created)")
    if missing_files:
        print(f"  - {len(missing_files)} source files are missing")
        print("    Copy these from the artifacts!")

print()