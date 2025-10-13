"""
Message Parser Service - Integrates AI parsing with transaction creation
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Tuple
from loguru import logger

from app.services.ai_service import AIService, AIParsingResult
from app.services.transaction_service import TransactionService
from app.models.category import Category
from app.schemas.transaction import TransactionCreate, PaymentMethod
from app.core.config import settings


class MessageParsingResult:
    """Result of message parsing and transaction creation"""

    def __init__(
        self,
        success: bool,
        transaction_id: Optional[int] = None,
        message: str = "",
        confidence: float = 0.0,
        extracted_data: Optional[dict] = None,
        error: Optional[str] = None
    ):
        self.success = success
        self.transaction_id = transaction_id
        self.message = message
        self.confidence = confidence
        self.extracted_data = extracted_data or {}
        self.error = error


class MessageParserService:
    """Service for parsing Telegram messages and creating transactions"""

    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
        self.transaction_service = TransactionService(db)

    async def parse_and_create_transaction(
        self,
        message: str,
        telegram_user_id: int,
        telegram_message_id: Optional[int] = None
    ) -> MessageParsingResult:
        """
        Parse a message using AI and create a transaction if successful
        """
        try:
            logger.info(f"Parsing message: '{message}' from user {telegram_user_id}")

            # Use AI to parse the message
            ai_result = await self.ai_service.parse_financial_message(message)

            if not ai_result.success:
                return MessageParsingResult(
                    success=False,
                    message="No pude entender la información financiera en tu mensaje.",
                    confidence=ai_result.confidence,
                    error="Failed to extract financial data"
                )

            # Map category name to category ID
            category_id = await self._get_category_id(ai_result.category)

            # Calculate transaction date based on date offset
            transaction_date = self._calculate_transaction_date(ai_result.date_offset)

            # Map payment method to enum
            payment_method = self._map_payment_method(ai_result.payment_method)

            # Create transaction data
            transaction_data = TransactionCreate(
                amount=ai_result.amount,
                description=ai_result.description,
                payment_method=payment_method,
                transaction_date=transaction_date,
                location=ai_result.location,
                category_id=category_id,
                telegram_message_id=telegram_message_id,
                telegram_user_id=telegram_user_id,
                original_text=message,
                ai_confidence=ai_result.confidence,
                ai_model_used="regex_parser"
            )

            # Create the transaction
            transaction = await self.transaction_service.create_transaction(transaction_data)

            # Generate confirmation message
            confirmation_message = self._generate_confirmation_message(
                transaction, ai_result.confidence
            )

            return MessageParsingResult(
                success=True,
                transaction_id=transaction.id,
                message=confirmation_message,
                confidence=ai_result.confidence,
                extracted_data={
                    'amount': ai_result.amount,
                    'description': ai_result.description,
                    'category': ai_result.category,
                    'payment_method': ai_result.payment_method,
                    'location': ai_result.location
                }
            )

        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return MessageParsingResult(
                success=False,
                message="Ocurrió un error al procesar tu mensaje. Intenta de nuevo.",
                error=str(e)
            )

    async def _get_category_id(self, category_name: str) -> Optional[int]:
        """Get category ID from category name"""

        category = self.db.query(Category).filter(
            Category.name.ilike(f"%{category_name}%")
        ).first()

        if category:
            return category.id

        # Map common AI category names to database categories
        category_mapping = {
            'alimentacion': 'Alimentación',
            'transporte': 'Transporte',
            'servicios': 'Servicios',
            'entretenimiento': 'Entretenimiento',
            'salud': 'Salud',
            'ropa': 'Ropa',
            'educacion': 'Educación',
            'casa': 'Casa',
            'otros': 'Otros'
        }

        mapped_name = category_mapping.get(category_name.lower())
        if mapped_name:
            category = self.db.query(Category).filter(
                Category.name == mapped_name
            ).first()
            if category:
                return category.id

        # Return "Otros" category as default
        default_category = self.db.query(Category).filter(
            Category.name == 'Otros'
        ).first()

        return default_category.id if default_category else None

    def _calculate_transaction_date(self, date_offset: int) -> datetime:
        """Calculate transaction date based on offset from today"""

        base_date = datetime.now()
        return base_date + timedelta(days=date_offset)

    def _map_payment_method(self, ai_payment_method: str) -> PaymentMethod:
        """Map AI payment method to PaymentMethod enum"""

        method_mapping = {
            'tarjeta': PaymentMethod.CARD,
            'efectivo': PaymentMethod.CASH,
            'transferencia': PaymentMethod.TRANSFER,
            'debito': PaymentMethod.DEBIT
        }

        return method_mapping.get(ai_payment_method.lower(), PaymentMethod.CARD)

    def _generate_confirmation_message(
        self,
        transaction,
        confidence: float
    ) -> str:
        """Generate a confirmation message for the user"""

        # Format amount with thousands separator
        amount_formatted = f"${transaction.amount:,.0f}"

        # Get category name
        category_name = transaction.category_name or "Sin categoría"

        # Format date
        date_str = transaction.transaction_date.strftime("%d/%m/%Y")

        # Base confirmation message
        message = f"✅ Transacción registrada:\n"
        message += f"💰 Monto: {amount_formatted}\n"
        message += f"📝 Descripción: {transaction.description}\n"
        message += f"🏷️ Categoría: {category_name}\n"
        message += f"💳 Método: {transaction.payment_method}\n"
        message += f"📅 Fecha: {date_str}"

        # Add location if available
        if transaction.location:
            message += f"\n📍 Lugar: {transaction.location}"

        # Add confidence indicator
        if confidence < 0.7:
            message += "\n\n⚠️ Revisa que la información sea correcta"
        elif confidence > 0.9:
            message += "\n\n✨ Alta confianza en la información"

        # Add validation prompt
        message += f"\n\nID: {transaction.id} | ✅ Validar | ✏️ Corregir"

        return message

    async def test_ai_connection(self) -> Tuple[bool, str]:
        """Test AI service connection and return status"""

        try:
            is_connected = await self.ai_service.test_connection()

            if is_connected:
                return True, "✅ Conexión con AI exitosa"
            else:
                return False, "❌ No se pudo conectar con el servicio de AI"

        except Exception as e:
            return False, f"❌ Error de conexión: {str(e)}"

    async def parse_message_for_preview(self, message: str) -> dict:
        """
        Parse a message and return extracted data without creating transaction
        Useful for previews and testing
        """

        try:
            ai_result = await self.ai_service.parse_financial_message(message)

            return {
                'success': ai_result.success,
                'amount': ai_result.amount,
                'description': ai_result.description,
                'category': ai_result.category,
                'payment_method': ai_result.payment_method,
                'location': ai_result.location,
                'confidence': ai_result.confidence,
                'date_offset': ai_result.date_offset
            }

        except Exception as e:
            logger.error(f"Error in preview parsing: {e}")
            return {
                'success': False,
                'error': str(e)
            }