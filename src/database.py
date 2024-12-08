# src/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import Config

class DatabaseConnection:
    def __init__(self):
        connection_string = (
            f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}"
            f"@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
        )
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def get_connection(self):
        return self.Session()

    def execute_query(self, query, params=None):
        with self.engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            return result