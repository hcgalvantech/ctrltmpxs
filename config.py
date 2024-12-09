import os
from typing import List

class Config:
    # Application Configuration
    APPLICATION_NAME: str = os.getenv('APP_NAME', 'Examenes Finales - Instituto ALFA')
    APPLICATION_VERSION: str = os.getenv('APP_VERSION', '1.0.0')

    # Database Configuration
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: str = os.getenv('DB_PORT', '5432')
    DB_NAME: str = os.getenv('DB_NAME', 'alumnos')
    DB_USER: str = os.getenv('DB_USER', 'evalua')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')

    # Database Connection String
    SQLALCHEMY_DATABASE_URI: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Email Configuration
    EMAIL_SENDER: str = os.getenv('EMAIL_SENDER', 'hcgalvantech@gmail.com')
    EMAIL_SERVICE: str = os.getenv('EMAIL_SERVICE', 'sendgrid')
    SENDGRID_API_KEY: str = os.getenv('SENDGRID_API_KEY', '')

    # Exam Configuration
    MAX_EXAM_TIME_MINUTES: int = int(os.getenv('MAX_EXAM_TIME_MINUTES', 120))
    ALLOWED_FILE_EXTENSIONS: List[str] = os.getenv('ALLOWED_EXTENSIONS', '.py,.js,.html,.css').split(',')

    # Security Configuration
    CSRF_PROTECTION: bool = os.getenv('CSRF_PROTECTION', 'true').lower() == 'true'
    SECRET_KEY: str = os.getenv('FLASK_SECRET_KEY', '')

    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', 5))

    @classmethod
    def validate(cls):
        """
        Validate critical configuration parameters
        """
        critical_vars = [
            'DB_HOST', 'DB_PORT', 'DB_NAME', 
            'DB_USER', 'DB_PASSWORD', 
            'FLASK_SECRET_KEY', 'SENDGRID_API_KEY'
        ]
        
        missing_vars = [var for var in critical_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing critical environment variables: {', '.join(missing_vars)}")