import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "CỨU TRỢ - Community Disaster Alert and Relief Platform"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "cuu-tro-platform-secret-key-2026-secure")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-super-secret-cuu-tro-platform")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database configuration: defaults to SQLite for local development, easily configured for MySQL via DATABASE_URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'relief.db'}")
    
    # Uploads
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    
    # Open-Meteo Weather API (Free, open access)
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
