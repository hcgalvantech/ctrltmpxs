# src/config.py
import os
from dotenv import load_dotenv
import secrets
import logging

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    # Generate secret key, prioritizing environment variable
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    
    # If no environment variable, generate a new one
    if not SECRET_KEY:
        SECRET_KEY = secrets.token_hex(16)
        # Optionally, write to .env file
        with open('.env', 'a') as f:
            f.write(f"\nFLASK_SECRET_KEY={SECRET_KEY}")
    @classmethod
    def validate(cls):
        """
        Validate configuration settings
        Raises an exception if any critical configuration is missing
        """
        required_keys = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_keys = [key for key in required_keys if not getattr(cls, key)]
        
        if missing_keys:
            error_msg = f"Missing configuration keys: {', '.join(missing_keys)}"
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        # Additional validations can be added here
        logging.info("Configuration validated successfully")
        return True