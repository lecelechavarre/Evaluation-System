"""
Utility functions.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(logs_dir: Path, level=logging.INFO):
    """Configure application logging."""
    logs_dir = Path(logs_dir)
    logs_dir.mkdir(exist_ok=True)
    
    log_file = logs_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info("Logging initialized")


def format_date(date_string: str, format_out: str = '%Y-%m-%d') -> str:
    """Format date string."""
    try:
        dt = datetime.fromisoformat(date_string)
        return dt.strftime(format_out)
    except:
        return date_string


def truncate_string(text: str, length: int = 50) -> str:
    """Truncate string to specified length."""
    return text[:length] + '...' if len(text) > length else text
