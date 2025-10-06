"""
Thread-safe JSON file storage with file locking.
"""
import json
import os
from pathlib import Path
from filelock import FileLock
from typing import Any, List, Dict
import logging

logger = logging.getLogger(__name__)


class FileStore:
    """Thread-safe JSON file storage manager."""
    
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.lock_path = Path(str(file_path) + '.lock')
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create file with empty list if it doesn't exist."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def load(self) -> List[Dict]:
        """Load data from JSON file with file locking."""
        lock = FileLock(self.lock_path, timeout=10)
        try:
            with lock:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {self.file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading {self.file_path}: {e}")
            return []
    
    def save(self, data: List[Dict]) -> bool:
        """Save data to JSON file with file locking."""
        lock = FileLock(self.lock_path, timeout=10)
        try:
            with lock:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved data to {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving to {self.file_path}: {e}")
            return False
    
    def find_by_id(self, item_id: str) -> Dict | None:
        """Find item by ID."""
        data = self.load()
        for item in data:
            if item.get('id') == item_id:
                return item
        return None
    
    def find_by(self, **filters) -> List[Dict]:
        """Find items matching filters."""
        data = self.load()
        results = []
        for item in data:
            match = all(item.get(k) == v for k, v in filters.items())
            if match:
                results.append(item)
        return results
    
    def create(self, item: Dict) -> bool:
        """Add new item."""
        data = self.load()
        # Check for duplicate ID
        if any(existing.get('id') == item.get('id') for existing in data):
            logger.warning(f"Item with id {item.get('id')} already exists")
            return False
        data.append(item)
        return self.save(data)
    
    def update(self, item_id: str, updates: Dict) -> bool:
        """Update existing item."""
        data = self.load()
        for i, item in enumerate(data):
            if item.get('id') == item_id:
                data[i].update(updates)
                return self.save(data)
        logger.warning(f"Item with id {item_id} not found")
        return False
    
    def delete(self, item_id: str) -> bool:
        """Delete item by ID."""
        data = self.load()
        original_length = len(data)
        data = [item for item in data if item.get('id') != item_id]
        if len(data) < original_length:
            return self.save(data)
        return False
