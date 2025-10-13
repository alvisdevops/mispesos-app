"""
Message Parser Service - Uses regex-based parsing for financial messages
"""

import re
import time
from typing import Optional, Dict, Any
from loguru import logger

from app.services.metrics_service import get_metrics_service


class AIParsingResult:
    """Result of parsing with structured data"""

    def __init__(self, data: Dict[str, Any]):
        self.amount: Optional[float] = data.get('amount')
        self.description: Optional[str] = data.get('description')
        self.category: Optional[str] = data.get('category')
        self.payment_method: Optional[str] = data.get('payment_method')
        self.location: Optional[str] = data.get('location')
        self.confidence: float = data.get('confidence', 0.0)
        self.date_offset: int = data.get('date_offset', 0)  # Days from today
        self.raw_response: str = data.get('raw_response', '')
        self.success: bool = self.amount is not None and self.amount > 0


class AIService:
    """Service for regex-based message parsing"""

    def __init__(self):
        self.metrics = get_metrics_service()

    async def parse_financial_message(self, message: str) -> AIParsingResult:
        """
        Parse a financial message using regex to extract structured data
        """
        start_time = time.time()

        try:
            logger.info(f"Parsing message with regex: '{message}'")

            # Extract amount using regex
            amount = self._extract_amount_regex(message)

            # Basic category detection
            category = self._detect_category_regex(message)

            # Basic payment method detection
            payment_method = self._detect_payment_method_regex(message)

            data = {
                'amount': amount,
                'description': message[:100],
                'category': category,
                'payment_method': payment_method,
                'location': None,
                'date_offset': 0,
                'confidence': 0.8 if amount else 0.2,
                'raw_response': 'regex_parsing'
            }

            result = AIParsingResult(data)
            latency = time.time() - start_time

            # Record metrics
            self.metrics.ai_metrics.record_request(
                success=result.success,
                latency=latency,
                confidence=result.confidence,
                from_cache=False,
                used_fallback=False
            )

            logger.info(f"Parsing completed: amount={amount}, category={category}, confidence={result.confidence}")

            return result

        except Exception as e:
            logger.error(f"Parsing error: {e}")
            latency = time.time() - start_time

            # Record error
            self.metrics.ai_metrics.record_request(
                success=False,
                latency=latency,
                from_cache=False,
                used_fallback=False
            )

            # Return default result
            data = {
                'amount': None,
                'description': message[:100],
                'category': 'otros',
                'payment_method': 'tarjeta',
                'location': None,
                'date_offset': 0,
                'confidence': 0.1,
                'raw_response': f'error: {str(e)}'
            }

            return AIParsingResult(data)

    def _extract_amount_regex(self, message: str) -> Optional[float]:
        """Extract amount using regex patterns"""

        # Pattern for amounts like "50k", "50mil", "50000"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*k(?:\s|$)',  # 50k, 50.5k
            r'(\d+(?:\.\d+)?)\s*mil(?:\s|$)',  # 50mil
            r'(\d{4,})',  # 50000 (4+ digits)
            r'(\d+(?:\.\d+)?)\s*(?:mil|k)',  # Alternative patterns
        ]

        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                try:
                    value = float(match.group(1))
                    # Convert k and mil to thousands
                    if 'k' in pattern or 'mil' in pattern:
                        return value * 1000
                    return value
                except ValueError:
                    continue

        return None

    def _detect_category_regex(self, message: str) -> str:
        """Detect category using regex patterns"""

        keywords = {
            'alimentacion': ['almuerzo', 'desayuno', 'cena', 'comida', 'restaurante', 'pizza', 'hamburgues', 'cafe', 'snack', 'merienda'],
            'transporte': ['uber', 'taxi', 'bus', 'transmilenio', 'gasolina', 'combustible', 'peaje', 'parqueadero'],
            'servicios': ['internet', 'telefono', 'luz', 'agua', 'netflix', 'spotify', 'gas', 'arriendo', 'alquiler'],
            'entretenimiento': ['cine', 'bar', 'discoteca', 'concierto', 'teatro', 'juego'],
            'salud': ['farmacia', 'doctor', 'medico', 'hospital', 'medicina'],
            'ropa': ['ropa', 'zapatos', 'camisa', 'pantalon'],
            'educacion': ['libro', 'curso', 'clase', 'universidad', 'colegio'],
            'casa': ['mercado', 'supermercado', 'limpieza', 'mueble'],
        }

        message_lower = message.lower()

        for category, words in keywords.items():
            for word in words:
                if word in message_lower:
                    return category

        return 'otros'

    def _detect_payment_method_regex(self, message: str) -> str:
        """Detect payment method using regex patterns"""

        message_lower = message.lower()

        if any(word in message_lower for word in ['tarjeta', 'card']):
            return 'tarjeta'
        elif any(word in message_lower for word in ['efectivo', 'cash', 'plata']):
            return 'efectivo'
        elif any(word in message_lower for word in ['transferencia', 'transfer']):
            return 'transferencia'
        elif any(word in message_lower for word in ['debito', 'débito']):
            return 'debito'

        return 'tarjeta'  # Default

    async def test_connection(self) -> bool:
        """Test service - always returns True for regex-based parsing"""
        return True
