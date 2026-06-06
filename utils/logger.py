"""
Logging module for the application
Provides structured logging with file and console output
"""

import logging
import logging.handlers
import json
from pathlib import Path
from typing import Optional


class LoggerConfig:
    """Configuration for application logging"""
    
    _instance: Optional['LoggerConfig'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.log_dir = Path("./logs")
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "app.log"
        self.log_level = logging.INFO
        self._initialized = True


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    config = LoggerConfig()
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(config.log_level)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        config.log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(config.log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def load_config() -> dict:
    """
    Load configuration from settings.json
    
    Returns:
        Configuration dictionary
    """
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger = get_logger(__name__)
        logger.error(f"Config file not found at {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logger = get_logger(__name__)
        logger.error(f"Invalid JSON in config file: {e}")
        return {}


# Global logger instance
logger = get_logger(__name__)
