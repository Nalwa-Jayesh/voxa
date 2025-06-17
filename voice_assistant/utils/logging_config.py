"""Logging configuration for the voice assistant."""

import logging
from pathlib import Path

def setup_logging():
    """Configure logging for the application."""
    log_file = Path('voice_assistant.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

# Create logger instance
logger = setup_logging() 