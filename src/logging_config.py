# src/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    # Ensure logs directory exists
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    # Configure logging
    log_file = os.path.join(log_dir, 'app.log')
    
    # Create a custom logger
    logger = logging.getLogger('examenes_finales')
    logger.setLevel(logging.INFO)

    # Create handlers
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    console_handler = logging.StreamHandler()

    # Create formatters and add it to handlers
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger