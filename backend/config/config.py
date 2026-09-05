import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-key-relief-platform')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-relief-platform')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    
    # Database configuration: defaults to SQLite inside the project directory for quick run, 
    # but easily points to MySQL by setting DATABASE_URL environment variable.
    DEFAULT_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'relief.db'))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f'sqlite:///{DEFAULT_DB_PATH}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Weather integration configuration
    OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY', 'mock_api_key_for_offline_run')
    WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # Ensure in production, secret keys are actually set via environment variables
    # and fail fast if not.
    
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig
}

active_config = config_by_name[os.environ.get('FLASK_ENV', 'dev')]
