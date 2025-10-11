"""
AI Service for intelligent message parsing using Ollama
"""

import httpx
import json
import re
import asyncio
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
from functools import lru_cache
import time

from app.core.config import settings
from app.services.metrics_service import get_metrics_service
from app.services.prometheus_metrics import track_ai_request, track_ollama_request, AIRequestTracker


class AIParsingResult:
    """Result of AI parsing with structured data"""

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
    """Service for AI-powered message parsing using Ollama"""

    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = 90.0  # Increased to 90s for more reliable processing
        self.max_retries = 2  # Reduced to 2 retries for faster fallback
        self.base_delay = 2.0  # Increased base delay between retries
        self._response_cache: Dict[str, tuple] = {}  # Cache for AI responses
        self.cache_ttl = 3600  # Cache TTL in seconds (1 hour)
        self.metrics = get_metrics_service()

    async def parse_financial_message(self, message: str) -> AIParsingResult:
        """
        Parse a financial message using AI to extract structured data with retry logic and caching
        """
        start_time = time.time()
        from_cache = False
        used_fallback = False

        # Track active request in Prometheus
        with AIRequestTracker():
            try:
                # Normalize message for consistent caching
                normalized_message = message.strip().lower()
                cache_key = self._get_cache_key(normalized_message)

                # Check cache first
                cached_result = self._get_cached_response(cache_key)
                if cached_result:
                logger.info("Using cached AI response")
                from_cache = True
                result = AIParsingResult(cached_result)

                # Record cache hit
                latency = time.time() - start_time
                self.metrics.ai_metrics.record_request(
                    success=True,
                    latency=latency,
                    confidence=result.confidence,
                    from_cache=True,
                    used_fallback=False
                )

                # Track in Prometheus
                track_ai_request(
                    duration=latency,
                    success=True,
                    confidence=result.confidence,
                    from_cache=True,
                    timeout=False,
                    used_fallback=False
                )

                return result

            # Create the prompt for financial parsing
            prompt = self._create_financial_prompt(message)

            # Call Ollama API with retry logic
            response = await self._call_ollama_with_retry(prompt)

            latency = time.time() - start_time

            if response:
                # Parse the AI response
                parsed_data = self._parse_ai_response(response, message)
                result = AIParsingResult(parsed_data)

                # If parsing was successful, cache and return it
                if result.success and result.confidence > 0.6:
                    logger.info(f"AI parsing successful with confidence {result.confidence} (latency: {latency:.2f}s)")
                    self._cache_response(cache_key, parsed_data)

                    # Record successful request
                    self.metrics.ai_metrics.record_request(
                        success=True,
                        latency=latency,
                        confidence=result.confidence,
                        from_cache=False,
                        used_fallback=False
                    )

                    return result
                else:
                    logger.warning(f"AI parsing low confidence ({result.confidence}), falling back to regex")
                    used_fallback = True

                    # Record low confidence as partial success
                    self.metrics.ai_metrics.record_request(
                        success=False,
                        latency=latency,
                        confidence=result.confidence,
                        from_cache=False,
                        used_fallback=True
                    )

                    return await self._fallback_regex_parsing(message)
            else:
                # Fallback to regex parsing
                logger.warning("AI parsing failed after retries, falling back to regex")
                used_fallback = True

                # Record failed request
                self.metrics.ai_metrics.record_request(
                    success=False,
                    latency=latency,
                    from_cache=False,
                    used_fallback=True
                )

                return await self._fallback_regex_parsing(message)

        except Exception as e:
            logger.error(f"AI parsing error: {e}")
            latency = time.time() - start_time

            # Record error
            self.metrics.ai_metrics.record_request(
                success=False,
                latency=latency,
                from_cache=False,
                used_fallback=True
            )

            # Fallback to regex parsing
            return await self._fallback_regex_parsing(message)

    def _create_financial_prompt(self, message: str) -> str:
        """Create a structured prompt for financial message parsing"""

        prompt = f"""
Eres un asistente especializado en extraer información financiera de mensajes en español.

Analiza el siguiente mensaje y extrae la información financiera en formato JSON:

Mensaje: "{message}"

Debes extraer:
- amount: monto numérico (solo números, sin símbolos)
- description: QUÉ se compró o el servicio/producto (NO el método de pago). Ejemplos: "almuerzo", "Uber", "gasolina", "pizza"
- category: categoría más probable (alimentacion, transporte, servicios, entretenimiento, salud, ropa, educacion, casa, otros)
- payment_method: CÓMO se pagó (tarjeta, efectivo, transferencia, debito) - busca al FINAL del mensaje
- location: lugar si se menciona
- date_offset: días desde hoy (0=hoy, -1=ayer, 1=mañana)
- confidence: nivel de confianza (0.0 a 1.0)

IMPORTANTE:
- La descripción debe ser el producto/servicio, NO el método de pago
- El método de pago usualmente aparece al final: "tarjeta", "efectivo", "transferencia", "débito"

Ejemplos:
- "30k en Uber transferencia" → description: "Uber", payment_method: "transferencia"
- "50k almuerzo tarjeta" → description: "almuerzo", payment_method: "tarjeta"
- "pague 25000 gasolina efectivo" → description: "gasolina", payment_method: "efectivo"

Formatos de dinero válidos:
- "50k" = 50000
- "50mil" = 50000
- "50000" = 50000
- "50.5k" = 50500

Responde ÚNICAMENTE con un JSON válido, sin explicaciones adicionales:

{{
  "amount": 50000,
  "description": "almuerzo",
  "category": "alimentacion",
  "payment_method": "tarjeta",
  "location": null,
  "date_offset": 0,
  "confidence": 0.95
}}
"""
        return prompt

    async def _call_ollama_with_retry(self, prompt: str) -> Optional[str]:
        """Call Ollama API with exponential backoff retry logic"""
        timeout_occurred = False

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"AI request attempt {attempt + 1}/{self.max_retries}")

                response = await self._call_ollama(prompt)

                if response:
                    return response

                # If we got None, wait before retrying (unless it's the last attempt)
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"AI request failed, retrying in {delay}s...")
                    await asyncio.sleep(delay)

            except asyncio.TimeoutError:
                timeout_occurred = True
                logger.error(f"AI request attempt {attempt + 1} timed out")

                # Track timeout in metrics
                if attempt == self.max_retries - 1:
                    self.metrics.ai_metrics.record_request(
                        success=False,
                        latency=self.timeout,
                        timeout=True,
                        from_cache=False
                    )

                # If it's not the last attempt, wait before retrying
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"AI request attempt {attempt + 1} failed: {e}")

                # If it's not the last attempt, wait before retrying
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)

        logger.error(f"All {self.max_retries} AI request attempts failed (timeout: {timeout_occurred})")
        return None

    async def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call Ollama API for text generation (single attempt)"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "keep_alive": -1,  # Keep model in memory
                        "options": {
                            "temperature": 0.1,  # Low temperature for consistency
                            "top_p": 0.9,
                            "num_predict": 150,  # Limit output tokens for speed
                            "num_ctx": 1024,  # Smaller context window for speed
                            "num_thread": 4  # Optimize CPU threads
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '')

                    # Validate that we got a meaningful response
                    if len(response_text.strip()) < 10:
                        logger.warning("AI response too short, likely incomplete")
                        return None

                    return response_text
                else:
                    logger.error(f"Ollama API error: {response.status_code}")
                    return None

        except httpx.TimeoutException:
            logger.error("Ollama API timeout")
            return None
        except httpx.ConnectError:
            logger.error("Ollama API connection error")
            return None
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return None

    def _parse_ai_response(self, ai_response: str, original_message: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON data"""

        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)

                # Validate and normalize the data
                return self._validate_and_normalize(data, original_message, ai_response)
            else:
                logger.warning("No JSON found in AI response")
                return self._create_error_result(original_message, ai_response)

        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {e}")
            return self._create_error_result(original_message, ai_response)

    def _validate_and_normalize(self, data: Dict[str, Any], original_message: str, ai_response: str) -> Dict[str, Any]:
        """Validate and normalize AI extracted data"""

        result = {
            'raw_response': ai_response,
            'confidence': min(max(data.get('confidence', 0.0), 0.0), 1.0)
        }

        # Validate amount
        amount = data.get('amount')
        if isinstance(amount, (int, float)) and amount > 0:
            result['amount'] = float(amount)
        else:
            result['amount'] = None
            result['confidence'] = max(result['confidence'] - 0.3, 0.0)

        # Validate description
        description = data.get('description', '').strip()
        if description:
            result['description'] = description[:500]  # Limit length
        else:
            result['description'] = original_message[:100]  # Fallback

        # Validate category
        valid_categories = [
            'alimentacion', 'transporte', 'servicios', 'entretenimiento',
            'salud', 'ropa', 'educacion', 'casa', 'otros'
        ]
        category = data.get('category', '').lower()
        if category in valid_categories:
            result['category'] = category
        else:
            result['category'] = 'otros'
            result['confidence'] = max(result['confidence'] - 0.2, 0.0)

        # Validate payment method
        valid_methods = ['tarjeta', 'efectivo', 'transferencia', 'debito']
        payment_method = data.get('payment_method', '').lower()
        if payment_method in valid_methods:
            result['payment_method'] = payment_method
        else:
            result['payment_method'] = 'tarjeta'  # Default
            result['confidence'] = max(result['confidence'] - 0.1, 0.0)

        # Optional fields
        result['location'] = data.get('location')
        result['date_offset'] = data.get('date_offset', 0)

        return result

    async def _fallback_regex_parsing(self, message: str) -> AIParsingResult:
        """Fallback regex-based parsing when AI fails"""

        logger.info("Using fallback regex parsing")

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
            'confidence': 0.6 if amount else 0.2,
            'raw_response': 'fallback_regex'
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
            'alimentacion': ['almuerzo', 'desayuno', 'cena', 'comida', 'restaurante', 'pizza', 'hamburgues'],
            'transporte': ['uber', 'taxi', 'bus', 'transmilenio', 'gasolina'],
            'servicios': ['internet', 'telefono', 'luz', 'agua', 'netflix', 'spotify'],
            'entretenimiento': ['cine', 'bar', 'discoteca', 'concierto'],
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
        elif any(word in message_lower for word in ['efectivo', 'cash']):
            return 'efectivo'
        elif any(word in message_lower for word in ['transferencia', 'transfer']):
            return 'transferencia'
        elif any(word in message_lower for word in ['debito']):
            return 'debito'

        return 'tarjeta'  # Default

    def _create_error_result(self, original_message: str, ai_response: str) -> Dict[str, Any]:
        """Create error result when parsing fails"""

        return {
            'amount': None,
            'description': original_message[:100],
            'category': 'otros',
            'payment_method': 'tarjeta',
            'location': None,
            'date_offset': 0,
            'confidence': 0.1,
            'raw_response': ai_response
        }

    async def test_connection(self) -> bool:
        """Test connection to Ollama service"""

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False

    def _get_cache_key(self, message: str) -> str:
        """Generate cache key from normalized message"""
        # Create hash of normalized message for consistent caching
        return hashlib.md5(message.encode('utf-8')).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached response if valid"""
        if cache_key in self._response_cache:
            cached_data, timestamp = self._response_cache[cache_key]

            # Check if cache is still valid
            if datetime.now().timestamp() - timestamp < self.cache_ttl:
                return cached_data
            else:
                # Remove expired entry
                del self._response_cache[cache_key]

        return None

    def _cache_response(self, cache_key: str, parsed_data: Dict[str, Any]) -> None:
        """Cache successful AI response"""
        # Only cache successful results with good confidence
        if parsed_data.get('amount') and parsed_data.get('confidence', 0) > 0.6:
            timestamp = datetime.now().timestamp()
            self._response_cache[cache_key] = (parsed_data, timestamp)

            # Clean up old entries to prevent memory bloat
            self._cleanup_cache()

            logger.debug(f"Cached AI response (cache size: {len(self._response_cache)})")

    def _cleanup_cache(self) -> None:
        """Clean up expired cache entries"""
        current_time = datetime.now().timestamp()
        expired_keys = [
            key for key, (_, timestamp) in self._response_cache.items()
            if current_time - timestamp >= self.cache_ttl
        ]

        for key in expired_keys:
            del self._response_cache[key]

        # Also limit cache size to prevent excessive memory usage
        if len(self._response_cache) > 1000:
            # Remove oldest entries
            sorted_items = sorted(
                self._response_cache.items(),
                key=lambda x: x[1][1]  # Sort by timestamp
            )
            # Keep only the newest 800 entries
            self._response_cache = dict(sorted_items[-800:])
            logger.info(f"Cache size limited to {len(self._response_cache)} entries")