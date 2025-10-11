"""
Message Processor - Handles text and photo processing for the bot
"""

from typing import Optional, NamedTuple
from loguru import logger
import os

from app.services.api_client import APIClient


class ProcessingResult(NamedTuple):
    """Result of message processing"""
    success: bool
    message: str
    transaction_id: Optional[int] = None
    confidence: float = 0.0
    extracted_data: Optional[dict] = None
    error: Optional[str] = None


class MessageProcessor:
    """Processes messages and integrates with API backend"""

    def __init__(self):
        self.api_client = APIClient()

    async def process_text_message(
        self,
        message: str,
        telegram_user_id: int,
        telegram_message_id: Optional[int] = None
    ) -> ProcessingResult:
        """Process a text message for financial data extraction"""

        logger.info(f"Processing text message: '{message}' from user {telegram_user_id}")

        try:
            # Check API connection first
            if not await self.api_client.test_connection():
                return ProcessingResult(
                    success=False,
                    message="❌ Servicio temporalmente no disponible. Intenta en unos minutos.",
                    error="API connection failed"
                )

            # Parse message using AI through API
            result = await self.api_client.parse_message(
                message=message,
                telegram_user_id=telegram_user_id,
                create_transaction=True
            )

            if not result:
                return ProcessingResult(
                    success=False,
                    message="❌ Error procesando el mensaje. Intenta de nuevo.",
                    error="API parse failed"
                )

            if result.get('success', False):
                # Successful parsing and transaction creation
                return ProcessingResult(
                    success=True,
                    message=result.get('message', 'Transacción creada exitosamente'),
                    transaction_id=result.get('transaction_id'),
                    confidence=result.get('confidence', 0.0),
                    extracted_data=result.get('extracted_data', {})
                )
            else:
                # Failed to extract financial data
                error_msg = result.get('error', 'No se pudo interpretar el mensaje')
                return ProcessingResult(
                    success=False,
                    message=self._generate_parsing_help_message(message),
                    error=error_msg
                )

        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            return ProcessingResult(
                success=False,
                message="❌ Error inesperado. Por favor intenta de nuevo.",
                error=str(e)
            )

    async def process_photo_message(
        self,
        photo_path: str,
        telegram_user_id: int,
        telegram_message_id: Optional[int] = None
    ) -> ProcessingResult:
        """Process a photo message for OCR and financial data extraction"""

        logger.info(f"Processing photo message from user {telegram_user_id}")

        try:
            # Check API connection first
            if not await self.api_client.test_connection():
                return ProcessingResult(
                    success=False,
                    message="❌ Servicio temporalmente no disponible. Intenta en unos minutos.",
                    error="API connection failed"
                )

            # Upload and process image using OCR API
            result = await self.api_client.process_image_ocr(
                image_path=photo_path,
                telegram_user_id=telegram_user_id,
                create_transaction=True
            )

            if not result:
                return ProcessingResult(
                    success=False,
                    message="❌ Error procesando la imagen. Intenta de nuevo.",
                    error="OCR API call failed"
                )

            if result.get('success', False):
                # Successful OCR processing and transaction creation
                return ProcessingResult(
                    success=True,
                    message=result.get('message', 'Factura procesada exitosamente'),
                    transaction_id=result.get('transaction_id'),
                    confidence=result.get('confidence', 0.0),
                    extracted_data=result.get('financial_data', {})
                )
            else:
                # Failed to process image
                error_msg = result.get('error', 'No se pudo procesar la imagen')
                return ProcessingResult(
                    success=False,
                    message=self._generate_ocr_help_message(error_msg),
                    error=error_msg
                )

        except Exception as e:
            logger.error(f"Error processing photo message: {e}")
            return ProcessingResult(
                success=False,
                message="❌ Error procesando la imagen. Intenta de nuevo.",
                error=str(e)
            )

    def _generate_parsing_help_message(self, original_message: str) -> str:
        """Generate a helpful message when parsing fails"""

        message = "❌ **No pude entender tu mensaje**\n\n"

        # Analyze the message to give specific help
        if not any(char.isdigit() for char in original_message):
            message += "💡 **Falta el monto:** No encontré números en tu mensaje\n"
            message += "**Ejemplo:** '50k almuerzo tarjeta'\n\n"

        elif len(original_message.split()) < 2:
            message += "💡 **Muy corto:** Necesito más información\n"
            message += "**Ejemplo:** '50k almuerzo tarjeta'\n\n"

        else:
            message += "💡 **Formato sugerido:**\n"
            message += "**[Monto] [Descripción] [Método de pago]**\n\n"

        message += "✅ **Ejemplos válidos:**\n"
        message += "• '50k almuerzo tarjeta'\n"
        message += "• 'pagué 25000 uber efectivo'\n"
        message += "• 'compré pizza 35mil débito'\n"
        message += "• 'gasolina 70k transferencia'"

        return message

    def _generate_ocr_help_message(self, error_msg: str) -> str:
        """Generate a helpful message when OCR processing fails"""

        message = f"📸 **{error_msg}**\n\n"
        message += "💡 **Para mejores resultados:**\n"
        message += "• Foto clara y bien iluminada\n"
        message += "• Factura completa en la imagen\n"
        message += "• Sin reflejos ni sombras\n"
        message += "• Texto legible\n\n"
        message += "🔄 Intenta con otra foto o escribe los datos manualmente:\n"
        message += "💡 **Ejemplo:** '50k almuerzo tarjeta'"

        return message

    async def test_services(self) -> dict:
        """Test all services connectivity"""

        results = {}

        # Test API connection
        try:
            results['api'] = await self.api_client.test_connection()
        except Exception as e:
            results['api'] = False
            logger.error(f"API test failed: {e}")

        # Test AI connection through API
        try:
            results['ai'] = await self.api_client.test_ai_connection()
        except Exception as e:
            results['ai'] = False
            logger.error(f"AI test failed: {e}")

        return results