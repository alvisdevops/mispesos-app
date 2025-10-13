"""
Application configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # Basic settings
    APP_NAME: str = "MisPesos API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://mispesos_user:password@localhost:5432/mispesos"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_HOSTS: List[str] = ["*"]

    # File uploads
    MAX_FILE_SIZE_MB: int = 10
    UPLOAD_DIR: str = "/app/uploads"
    ALLOWED_IMAGE_TYPES: List[str] = ["jpg", "jpeg", "png", "pdf"]

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()