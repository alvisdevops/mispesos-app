"""
Telegram bot handlers setup
"""

from telegram.ext import Application
from loguru import logger

from .message_handler import setup_message_handlers
from .command_handler import setup_command_handlers
from .callback_handler import setup_callback_handlers


def setup_handlers(application: Application) -> None:
    """Setup all bot handlers"""

    logger.info("Setting up Telegram bot handlers...")

    # Setup command handlers (/start, /help, etc.)
    setup_command_handlers(application)

    # Setup message handlers (text, photos)
    setup_message_handlers(application)

    # Setup callback handlers (inline buttons)
    setup_callback_handlers(application)

    logger.info("✅ All handlers configured successfully")