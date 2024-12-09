import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Application Configuration
    APPLICATION_NAME = os.getenv('APPLICATION_NAME', 'Examenes Finales - Instituto ALFA')
    VERSION = os.getenv('APPLICATION_VERSION', '1.0.0')

    # Database Configuration
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    # Database Connection String
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Email Configuration
    EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'hcgalvantech@gmail.com')
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

    # Security Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    CSRF_PROTECTION = os.getenv('CSRF_PROTECTION', 'true') == 'true'

    # Exam Configuration
    MAX_EXAM_TIME = int(os.getenv('MAX_EXAM_TIME_MINUTES', 120))
    ALLOWED_FILE_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', '.py,.js,.html,.css').split(',')

    # Rate Limiting
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 5))