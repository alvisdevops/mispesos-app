"""
Telegram bot message handlers for text and photos
"""

from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from loguru import logger
import os

from app.services.api_client import APIClient
from app.services.message_processor import MessageProcessor


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages (potential financial transactions)"""

    user = update.effective_user
    message_text = update.message.text
    message_id = update.message.message_id

    logger.info(f"Processing text message from user {user.id}: '{message_text}'")

    # Send typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Process the message using AI
        processor = MessageProcessor()
        result = await processor.process_text_message(
            message=message_text,
            telegram_user_id=user.id,
            telegram_message_id=message_id
        )

        if result.success:
            # Success - send confirmation with inline buttons
            await send_transaction_confirmation(update, context, result)
        else:
            # Failed to parse - send helpful error message
            await send_parsing_error(update, context, result.message)

    except Exception as e:
        logger.error(f"Error processing text message: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error inesperado. Por favor intenta de nuevo.\n\n"
            "💡 **Formato esperado:** '50k almuerzo tarjeta'"
        )


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages (receipts for OCR processing)"""

    user = update.effective_user
    message_id = update.message.message_id

    logger.info(f"Processing photo message from user {user.id}")

    # Send processing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")

    # Send initial processing message
    processing_msg = await update.message.reply_text(
        "📸 **Procesando imagen...**\n"
        "⏳ Extrayendo datos de la factura..."
    )

    try:
        # Get the largest photo
        photo = update.message.photo[-1]

        # Download photo
        file = await context.bot.get_file(photo.file_id)
        temp_path = f"/app/temp/{photo.file_id}.jpg"

        # Ensure temp directory exists
        os.makedirs("/app/temp", exist_ok=True)

        # Download file
        await file.download_to_drive(temp_path)

        # Process the photo using OCR + AI
        processor = MessageProcessor()
        result = await processor.process_photo_message(
            photo_path=temp_path,
            telegram_user_id=user.id,
            telegram_message_id=message_id
        )

        # Delete processing message
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=processing_msg.message_id
        )

        if result.success:
            # Success - send confirmation
            await send_transaction_confirmation(update, context, result)
        else:
            # Failed to process - send error
            await send_ocr_error(update, context, result.message)

        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass

    except Exception as e:
        logger.error(f"Error processing photo: {e}")

        # Delete processing message
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id
            )
        except:
            pass

        await update.message.reply_text(
            "❌ Error procesando la imagen.\n\n"
            "💡 **Tips:**\n"
            "• Asegúrate que la imagen sea clara\n"
            "• La factura debe estar bien iluminada\n"
            "• Formatos soportados: JPG, PNG\n"
            "• Tamaño máximo: 10MB"
        )


async def send_transaction_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, result) -> None:
    """Send transaction confirmation with inline buttons"""

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    # Create inline keyboard for actions
    keyboard = [
        [
            InlineKeyboardButton("✅ Validar", callback_data=f"validate_{result.transaction_id}"),
            InlineKeyboardButton("✏️ Editar", callback_data=f"edit_{result.transaction_id}")
        ],
        [
            InlineKeyboardButton("🗑️ Eliminar", callback_data=f"delete_{result.transaction_id}"),
            InlineKeyboardButton("📊 Ver Resumen", callback_data="summary_today")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Add confidence indicator
    confidence_emoji = "✨" if result.confidence > 0.9 else "⚠️" if result.confidence < 0.7 else "✅"

    message = f"{confidence_emoji} {result.message}"

    if result.confidence < 0.7:
        message += "\n\n⚠️ **Baja confianza** - Por favor revisa los datos"

    await update.message.reply_text(message, reply_markup=reply_markup)


async def send_parsing_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error_message: str) -> None:
    """Send parsing error with helpful suggestions"""

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    # Create help keyboard
    keyboard = [
        [
            InlineKeyboardButton("📋 Ver Ejemplos", callback_data="examples"),
            InlineKeyboardButton("❓ Ayuda", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = f"❌ {error_message}\n\n"
    message += "💡 **Ejemplos válidos:**\n"
    message += "• '50k almuerzo tarjeta'\n"
    message += "• 'pagué 25000 uber efectivo'\n"
    message += "• 'compré pizza 35mil débito'\n"
    message += "• 'gasolina 70k transferencia'"

    await update.message.reply_text(message, reply_markup=reply_markup)


async def send_ocr_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error_message: str) -> None:
    """Send OCR processing error"""

    message = f"📸 {error_message}\n\n"
    message += "💡 **Para mejores resultados:**\n"
    message += "• Foto clara y bien iluminada\n"
    message += "• Factura completa en la imagen\n"
    message += "• Sin reflejos ni sombras\n"
    message += "• Texto legible\n\n"
    message += "🔄 Intenta con otra foto o escribe los datos manualmente"

    await update.message.reply_text(message)


def setup_message_handlers(application: Application) -> None:
    """Setup all message handlers"""

    logger.info("Setting up message handlers...")

    # Text messages (exclude commands)
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text_message
        )
    )

    # Photo messages
    application.add_handler(
        MessageHandler(
            filters.PHOTO,
            handle_photo_message
        )
    )

    logger.info("✅ Message handlers configured")