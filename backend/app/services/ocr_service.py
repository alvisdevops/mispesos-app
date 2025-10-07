"""
OCR Service for processing receipt images
"""

import os
import cv2
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from typing import Dict, List, Optional, Tuple
from loguru import logger
import re
from datetime import datetime

from app.services.ai_service import AIService


class OCRService:
    """Service for processing receipt images with OCR"""

    def __init__(self):
        self.ai_service = AIService()

        # Configure Tesseract if needed
        # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Already in PATH in Docker

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
            # Step 1: Preprocess the image
            processed_image_path = self._preprocess_image(image_path)

            # Step 2: Extract text with OCR
            extracted_text = self._extract_text_from_image(processed_image_path)

            if not extracted_text.strip():
                return {
                    "success": False,
                    "error": "No se pudo extraer texto de la imagen",
                    "extracted_text": "",
                    "confidence": 0.0
                }

            logger.info(f"Extracted text: {extracted_text[:200]}...")

            # Step 3: Parse financial data using AI
            financial_data = self._parse_financial_data(extracted_text)

            # Step 4: Extract additional receipt metadata
            receipt_metadata = self._extract_receipt_metadata(extracted_text)

            # Clean up processed image
            try:
                if processed_image_path != image_path:
                    os.remove(processed_image_path)
            except:
                pass

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

    def _preprocess_image(self, image_path: str) -> str:
        """
        Preprocess image to improve OCR accuracy

        Args:
            image_path: Path to original image

        Returns:
            Path to processed image
        """

        try:
            # Load image with OpenCV
            image = cv2.imread(image_path)

            if image is None:
                raise ValueError("Could not load image")

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)

            # Apply threshold to get better contrast
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

            # Save processed image
            processed_path = image_path.replace('.jpg', '_processed.jpg').replace('.png', '_processed.png')
            cv2.imwrite(processed_path, opening)

            return processed_path

        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original: {e}")
            return image_path

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

            # Extract text
            text = pytesseract.image_to_string(Image.open(image_path), config=custom_config)

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