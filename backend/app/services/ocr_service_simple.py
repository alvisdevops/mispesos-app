"""
Simple OCR Service for testing without OpenCV dependencies
"""

import os
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, List, Optional, Tuple
from loguru import logger
import re
from datetime import datetime

from app.services.ai_service import AIService


class SimpleOCRService:
    """Simple OCR service using only Tesseract and PIL"""

    def __init__(self):
        self.ai_service = AIService()

    def process_receipt_image(self, image_path: str) -> Dict:
        """
        Process a receipt image and extract financial information

        Args:
            image_path: Path to the receipt image

        Returns:
            Dict with extracted data and confidence scores
        """

        logger.info(f"Processing receipt image: {image_path}")

        try:
            # Step 1: Extract text with OCR
            extracted_text = self._extract_text_from_image(image_path)

            if not extracted_text.strip():
                return {
                    "success": False,
                    "error": "No se pudo extraer texto de la imagen",
                    "extracted_text": "",
                    "confidence": 0.0
                }

            logger.info(f"Extracted text: {extracted_text[:200]}...")

            # Step 2: Parse financial data using AI
            financial_data = self._parse_financial_data(extracted_text)

            # Step 3: Extract additional receipt metadata
            receipt_metadata = self._extract_receipt_metadata(extracted_text)

            return {
                "success": True,
                "extracted_text": extracted_text,
                "financial_data": financial_data,
                "receipt_metadata": receipt_metadata,
                "confidence": financial_data.get("confidence", 0.0)
            }

        except Exception as e:
            logger.error(f"Error processing receipt image: {e}")
            return {
                "success": False,
                "error": f"Error procesando la imagen: {str(e)}",
                "extracted_text": "",
                "confidence": 0.0
            }

    def _extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using Tesseract OCR

        Args:
            image_path: Path to image file

        Returns:
            Extracted text string
        """

        try:
            # Configure Tesseract for Spanish and English
            custom_config = r'--oem 3 --psm 6 -l spa+eng'

            # Load and preprocess image
            image = Image.open(image_path)

            # Convert to grayscale if needed
            if image.mode != 'L':
                image = image.convert('L')

            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)

            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)

            # Clean up the text
            cleaned_text = self._clean_extracted_text(text)

            return cleaned_text

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise

    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text"""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s\$\.\,\:\-\(\)\/]', '', text)

        # Clean up common OCR errors
        text = text.replace('|', 'I')
        text = text.replace('0', 'O').replace('5', 'S')  # Common in Spanish text

        return text.strip()

    def _parse_financial_data(self, text: str) -> Dict:
        """
        Parse financial information from extracted text using AI

        Args:
            text: Raw extracted text from OCR

        Returns:
            Parsed financial data
        """

        try:
            # Create a specialized prompt for receipt parsing
            prompt = f"""
Analiza el siguiente texto extraído de una factura/recibo y extrae la información financiera relevante.

TEXTO EXTRAÍDO:
{text}

INSTRUCCIONES:
1. Busca el TOTAL o monto principal de la compra
2. Identifica la FECHA de la transacción
3. Determina el ESTABLECIMIENTO o tienda
4. Clasifica el TIPO de compra (alimentación, transporte, entretenimiento, etc.)
5. Extrae cualquier MÉTODO DE PAGO mencionado

RESPONDE EN FORMATO JSON:
{{
    "amount": [monto_numerico_sin_simbolos],
    "date": "[fecha_en_formato_YYYY-MM-DD_o_null]",
    "description": "[descripcion_corta_del_gasto]",
    "establishment": "[nombre_del_establecimiento_o_null]",
    "category": "[categoria_del_gasto]",
    "payment_method": "[metodo_de_pago_o_null]",
    "confidence": [0.0_a_1.0],
    "raw_amount_text": "[texto_original_del_monto]"
}}

Solo responde con el JSON, sin explicaciones adicionales.
"""

            # Get AI response (synchronous call)
            import asyncio
            loop = asyncio.get_event_loop()
            ai_response = loop.run_until_complete(self.ai_service.generate_response(prompt))

            if not ai_response or not ai_response.get("success"):
                raise ValueError("AI parsing failed")

            # Parse JSON response
            import json
            try:
                parsed_data = json.loads(ai_response["response"])

                # Validate required fields
                if "amount" not in parsed_data or not parsed_data["amount"]:
                    raise ValueError("No amount found in receipt")

                # Ensure amount is numeric
                amount = parsed_data["amount"]
                if isinstance(amount, str):
                    # Try to extract numeric value
                    amount_match = re.search(r'[\d\.,]+', str(amount))
                    if amount_match:
                        amount = float(amount_match.group().replace(',', ''))
                    else:
                        raise ValueError("Could not parse amount")

                parsed_data["amount"] = float(amount)

                # Set default confidence if not provided
                if "confidence" not in parsed_data:
                    parsed_data["confidence"] = 0.7

                return parsed_data

            except json.JSONDecodeError:
                logger.error("Failed to parse AI JSON response")
                raise ValueError("AI response format error")

        except Exception as e:
            logger.error(f"Financial data parsing failed: {e}")
            return {
                "amount": 0,
                "description": "Factura procesada",
                "category": "otros",
                "confidence": 0.3,
                "error": str(e)
            }

    def _extract_receipt_metadata(self, text: str) -> Dict:
        """Extract additional receipt metadata like tax info, receipt number, etc."""

        metadata = {}

        try:
            # Extract receipt number
            receipt_patterns = [
                r'(?:recibo|ticket|factura)[\s\#\:]*(\d+)',
                r'(?:no|num|number)[\s\.\:]*(\d+)',
                r'(\d{6,})'  # Long number sequences
            ]

            for pattern in receipt_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    metadata["receipt_number"] = match.group(1)
                    break

            # Extract tax information
            tax_patterns = [
                r'iva[\s\:]*(\d+[\.\,]?\d*)',
                r'tax[\s\:]*(\d+[\.\,]?\d*)',
                r'impuesto[\s\:]*(\d+[\.\,]?\d*)'
            ]

            for pattern in tax_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    metadata["tax_amount"] = match.group(1)
                    break

            # Extract phone numbers
            phone_match = re.search(r'(\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4})', text)
            if phone_match:
                metadata["phone"] = phone_match.group(1)

            # Extract email addresses
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if email_match:
                metadata["email"] = email_match.group(1)

        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")

        return metadata

    def test_ocr_installation(self) -> Dict:
        """Test if OCR components are properly installed"""

        try:
            # Test Tesseract
            version = pytesseract.get_tesseract_version()

            # Test languages
            languages = pytesseract.get_languages()

            return {
                "tesseract_version": str(version),
                "available_languages": languages,
                "spanish_available": "spa" in languages,
                "english_available": "eng" in languages,
                "installation_ok": True
            }

        except Exception as e:
            return {
                "installation_ok": False,
                "error": str(e)
            }