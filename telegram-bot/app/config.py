"""
Telegram Bot Configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Bot settings"""

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""

    # API Connection
    FASTAPI_URL: str = "http://fastapi:8000"

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"

    # Bot Configuration
    BOT_WEBHOOK_URL: Optional[str] = None
    BOT_WEBHOOK_SECRET: Optional[str] = None
    USE_POLLING: bool = True  # True for development, False for production with webhook

    # File handling
    MAX_FILE_SIZE_MB: int = 10
    TEMP_DIR: str = "/app/temp"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()