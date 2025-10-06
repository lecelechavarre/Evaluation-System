"""
Backup all JSON data files.
"""
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import DATA_DIR, BASE_DIR


def backup_data():
    """Create backup of all data files."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BASE_DIR / 'backups' / f'backup_{timestamp}'
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating backup at: {backup_dir}")
    
    # Copy all JSON files
    data_files = list(DATA_DIR.glob('*.json'))
    
    if not data_files:
        print("No data files found to backup.")
        return
    
    for file in data_files:
        dest = backup_dir / file.name
        shutil.copy2(file, dest)
        print(f"✓ Backed up: {file.name}")
    
    print(f"\n✅ Backup completed: {len(data_files)} files backed up")
    print(f"   Location: {backup_dir}")


if __name__ == '__main__':
    backup_data()


# ============================================================================
# MAIN ENTRY POINT FOR DESKTOP APP
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting Performance Evaluation System (Desktop)")
    app = PerformanceEvalApp()
    app.run()