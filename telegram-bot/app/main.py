"""
MisPesos Telegram Bot
Main bot application entry point
"""

import os
import asyncio
import signal
import sys
from loguru import logger
from telegram.ext import Application

from app.config import settings
from app.handlers import setup_handlers
from app.services.message_processor import MessageProcessor


async def test_services():
    """Test all service connections"""
    logger.info("🔧 Testing service connections...")

    processor = MessageProcessor()
    results = await processor.test_services()

    logger.info(f"📊 API Connection: {'✅' if results.get('api') else '❌'}")
    logger.info(f"🤖 AI Connection: {'✅' if results.get('ai') else '❌'}")

    if not results.get('api'):
        logger.warning("⚠️ API service not available - bot functionality will be limited")

    if not results.get('ai'):
        logger.warning("⚠️ AI service not available - using fallback parsing")

    return results


async def main():
    """Main bot function"""
    logger.info("🤖 Starting MisPesos Telegram Bot...")

    # Check configuration
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not configured")
        sys.exit(1)

    logger.info(f"🌐 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔗 FastAPI URL: {settings.FASTAPI_URL}")
    logger.info(f"🤖 Ollama URL: {settings.OLLAMA_URL}")

    # Test services
    await test_services()

    # Create application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Setup handlers
    setup_handlers(application)

    # Setup shutdown handler
    stop_event = asyncio.Event()

    def signal_handler(signum, frame):
        logger.info(f"🛑 Received signal {signum}, stopping bot...")
        stop_event.set()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start the bot
    if settings.USE_POLLING:
        logger.info("🔄 Starting bot with polling...")

        # Initialize the application
        await application.initialize()
        await application.start()

        # Start polling
        await application.updater.start_polling(drop_pending_updates=True)

        logger.info("✅ Bot is running! Press Ctrl+C to stop.")

        # Wait for stop signal
        await stop_event.wait()

        # Graceful shutdown
        logger.info("🔄 Shutting down bot...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

    else:
        logger.info("🌐 Starting bot with webhook...")
        # TODO: Implement webhook mode
        logger.error("❌ Webhook mode not implemented yet")
        sys.exit(1)


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        sys.exit(1)
    finally:
        logger.info("👋 Bot shutdown complete")