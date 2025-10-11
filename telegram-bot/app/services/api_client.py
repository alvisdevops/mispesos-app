"""
API Client for communicating with FastAPI backend
"""

import httpx
from typing import Optional, Dict, Any, List
from loguru import logger

from app.config import settings


class APIClient:
    """Client for FastAPI backend communication"""

    def __init__(self):
        self.base_url = settings.FASTAPI_URL
        self.timeout = 30.0

    async def parse_message(
        self,
        message: str,
        telegram_user_id: int,
        create_transaction: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Parse a message using AI and optionally create transaction"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/ai/parse",
                    json={
                        "message": message,
                        "telegram_user_id": telegram_user_id,
                        "create_transaction": create_transaction
                    }
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"API parse error: {response.status_code} - {response.text}")
                    return None

        except httpx.TimeoutException:
            logger.error("API parse timeout")
            return None
        except Exception as e:
            logger.error(f"API parse error: {e}")
            return None

    async def get_transaction(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific transaction by ID"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/transactions/{transaction_id}"
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    logger.error(f"API get transaction error: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"API get transaction error: {e}")
            return None

    async def get_transactions(
        self,
        telegram_user_id: int,
        limit: int = 10,
        skip: int = 0
    ) -> Optional[List[Dict[str, Any]]]:
        """Get transactions for a user"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/transactions/",
                    params={
                        "telegram_user_id": telegram_user_id,
                        "limit": limit,
                        "skip": skip
                    }
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"API get transactions error: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"API get transactions error: {e}")
            return None

    async def get_summary(
        self,
        period: str,
        telegram_user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get transaction summary for a period"""

        endpoint_map = {
            'daily': 'daily',
            'weekly': 'weekly',
            'monthly': 'monthly'
        }

        endpoint = endpoint_map.get(period, 'daily')

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/transactions/summary/{endpoint}",
                    params={"telegram_user_id": telegram_user_id}
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"API get summary error: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"API get summary error: {e}")
            return None

    async def validate_transaction(self, transaction_id: int) -> bool:
        """Mark a transaction as validated"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/transactions/{transaction_id}/validate"
                )

                return response.status_code == 200

        except Exception as e:
            logger.error(f"API validate transaction error: {e}")
            return False

    async def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.base_url}/api/v1/transactions/{transaction_id}"
                )

                return response.status_code == 200

        except Exception as e:
            logger.error(f"API delete transaction error: {e}")
            return False

    async def update_transaction(
        self,
        transaction_id: int,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a transaction"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    f"{self.base_url}/api/v1/transactions/{transaction_id}",
                    json=updates
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"API update transaction error: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"API update transaction error: {e}")
            return None

    async def get_categories(self) -> Optional[List[Dict[str, Any]]]:
        """Get all categories"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # For now, return a mock response since we haven't implemented categories endpoint
                # TODO: Implement categories endpoint in FastAPI
                return [
                    {"id": 1, "name": "Alimentación", "icon": "🍽️", "transaction_count": 0},
                    {"id": 2, "name": "Transporte", "icon": "🚗", "transaction_count": 0},
                    {"id": 3, "name": "Servicios", "icon": "⚡", "transaction_count": 0},
                    {"id": 4, "name": "Entretenimiento", "icon": "🎭", "transaction_count": 0},
                    {"id": 5, "name": "Salud", "icon": "🏥", "transaction_count": 0},
                    {"id": 6, "name": "Ropa", "icon": "👕", "transaction_count": 0},
                    {"id": 7, "name": "Educación", "icon": "📚", "transaction_count": 0},
                    {"id": 8, "name": "Casa", "icon": "🏠", "transaction_count": 0},
                    {"id": 9, "name": "Otros", "icon": "📦", "transaction_count": 0}
                ]

        except Exception as e:
            logger.error(f"API get categories error: {e}")
            return None

    async def test_connection(self) -> bool:
        """Test API connection"""

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/health/")
                return response.status_code == 200

        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False

    async def test_ai_connection(self) -> bool:
        """Test AI service connection through API"""

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/ai/test-connection")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("connected", False)
                return False

        except Exception as e:
            logger.error(f"AI connection test failed: {e}")
            return False

    async def process_image_ocr(
        self,
        image_path: str,
        telegram_user_id: int,
        create_transaction: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Process an image using OCR API"""

        try:
            # Upload file to OCR endpoint
            async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for OCR
                with open(image_path, 'rb') as image_file:
                    files = {'file': ('receipt.jpg', image_file, 'image/jpeg')}
                    data = {
                        'telegram_user_id': telegram_user_id,
                        'create_transaction': create_transaction
                    }

                    response = await client.post(
                        f"{self.base_url}/api/v1/ocr/process-image",
                        files=files,
                        data=data
                    )

                    if response.status_code == 200:
                        return response.json()
                    else:
                        logger.error(f"OCR API error: {response.status_code} - {response.text}")
                        return {
                            "success": False,
                            "error": f"Error procesando imagen (código {response.status_code})"
                        }

        except httpx.TimeoutException:
            logger.error("OCR API timeout")
            return {
                "success": False,
                "error": "Timeout procesando la imagen - intenta con una imagen más pequeña"
            }
        except Exception as e:
            logger.error(f"OCR API error: {e}")
            return {
                "success": False,
                "error": "Error de conexión con el servicio OCR"
            }

    async def test_ocr_installation(self) -> Optional[Dict[str, Any]]:
        """Test OCR installation through API"""

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/ocr/test-installation")
                if response.status_code == 200:
                    return response.json()
                return None

        except Exception as e:
            logger.error(f"OCR installation test failed: {e}")
            return None