"""
dLNk AI Bridge - Logger Utility
===============================
Centralized logging configuration for the AI Bridge system.

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


# Color codes for terminal output
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    LEVEL_COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.MAGENTA,
    }
    
    def format(self, record):
        # Add color to level name
        color = self.LEVEL_COLORS.get(record.levelno, Colors.WHITE)
        record.levelname = f"{color}{record.levelname}{Colors.RESET}"
        
        # Add color to logger name
        record.name = f"{Colors.BLUE}{record.name}{Colors.RESET}"
        
        return super().format(record)


def setup_logger(
    name: str = 'dLNk-AI-Bridge',
    level: str = 'INFO',
    log_file: Optional[str] = None,
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    max_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    use_colors: bool = True
) -> logging.Logger:
    """
    Setup and configure logger
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        log_format: Log message format
        max_size: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        use_colors: Whether to use colored output in terminal
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if use_colors and sys.stdout.isatty():
        console_formatter = ColoredFormatter(log_format)
    else:
        console_formatter = logging.Formatter(log_format)
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = 'dLNk-AI-Bridge') -> logging.Logger:
    """
    Get existing logger or create new one
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set up basic configuration
    if not logger.handlers:
        setup_logger(name)
    
    return logger


# Create default logger
default_logger = setup_logger()
