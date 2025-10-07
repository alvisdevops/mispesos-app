"""
OCR Queue Manager using Redis and Celery for asynchronous processing
"""

import os
import json
import uuid
from typing import Dict, Optional
from loguru import logger
from celery import Celery
from celery.result import AsyncResult

from app.core.config import settings
try:
    from app.services.ocr_service import OCRService
except ImportError:
    # Fallback to simple OCR service if OpenCV is not available
    from app.services.ocr_service_simple import SimpleOCRService as OCRService
from app.services.transaction_service import TransactionService


# Initialize Celery app
celery_app = Celery(
    "mispesos_ocr",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.services.ocr_queue']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,  # Results expire after 1 hour
    task_routes={
        'app.services.ocr_queue.process_receipt_task': {'queue': 'ocr'},
    }
)


class OCRQueueManager:
    """Manager for OCR task queue operations"""

    def __init__(self):
        self.celery_app = celery_app

    async def submit_ocr_task(
        self,
        image_path: str,
        telegram_user_id: int,
        create_transaction: bool = True,
        task_id: Optional[str] = None
    ) -> str:
        """
        Submit an OCR processing task to the queue

        Args:
            image_path: Path to the receipt image
            telegram_user_id: Telegram user ID
            create_transaction: Whether to create transaction from results
            task_id: Optional custom task ID

        Returns:
            Task ID for tracking
        """

        if not task_id:
            task_id = str(uuid.uuid4())

        logger.info(f"Submitting OCR task {task_id} for user {telegram_user_id}")

        try:
            # Submit task to Celery
            task = process_receipt_task.apply_async(
                args=[image_path, telegram_user_id, create_transaction],
                task_id=task_id,
                queue='ocr'
            )

            logger.info(f"OCR task {task_id} submitted successfully")
            return task_id

        except Exception as e:
            logger.error(f"Failed to submit OCR task: {e}")
            raise

    async def get_task_status(self, task_id: str) -> Dict:
        """
        Get the status of an OCR task

        Args:
            task_id: Task ID to check

        Returns:
            Task status and results
        """

        try:
            result = AsyncResult(task_id, app=celery_app)

            status_info = {
                "task_id": task_id,
                "status": result.status,
                "ready": result.ready(),
                "successful": result.successful() if result.ready() else None,
                "failed": result.failed() if result.ready() else None
            }

            if result.ready():
                if result.successful():
                    status_info["result"] = result.result
                elif result.failed():
                    status_info["error"] = str(result.info)
            else:
                # Task is still pending/processing
                if hasattr(result.info, 'get') and result.info:
                    status_info["progress"] = result.info

            return status_info

        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}")
            return {
                "task_id": task_id,
                "status": "ERROR",
                "error": str(e)
            }

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending OCR task

        Args:
            task_id: Task ID to cancel

        Returns:
            True if canceled successfully
        """

        try:
            celery_app.control.revoke(task_id, terminate=True)
            logger.info(f"OCR task {task_id} canceled")
            return True

        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False


@celery_app.task(bind=True, name='app.services.ocr_queue.process_receipt_task')
def process_receipt_task(self, image_path: str, telegram_user_id: int, create_transaction: bool = True):
    """
    Celery task for processing receipt images

    Args:
        image_path: Path to the receipt image
        telegram_user_id: Telegram user ID
        create_transaction: Whether to create transaction from results

    Returns:
        Processing results
    """

    task_id = self.request.id
    logger.info(f"Starting OCR task {task_id} for user {telegram_user_id}")

    try:
        # Update task state to PROGRESS
        self.update_state(
            state='PROGRESS',
            meta={'step': 'preprocessing', 'progress': 10}
        )

        # Check if image file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Initialize OCR service
        ocr_service = OCRService()

        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'step': 'ocr_processing', 'progress': 30}
        )

        # Process the image
        ocr_result = ocr_service.process_receipt_image(image_path)

        if not ocr_result["success"]:
            return {
                "success": False,
                "error": ocr_result.get("error", "OCR processing failed"),
                "task_id": task_id
            }

        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'step': 'parsing_data', 'progress': 70}
        )

        result_data = {
            "success": True,
            "task_id": task_id,
            "extracted_text": ocr_result["extracted_text"],
            "financial_data": ocr_result["financial_data"],
            "receipt_metadata": ocr_result["receipt_metadata"],
            "confidence": ocr_result["confidence"]
        }

        # Create transaction if requested
        if create_transaction and ocr_result["financial_data"].get("amount"):
            try:
                self.update_state(
                    state='PROGRESS',
                    meta={'step': 'creating_transaction', 'progress': 90}
                )

                transaction_service = TransactionService()
                financial_data = ocr_result["financial_data"]

                transaction_data = {
                    "amount": financial_data["amount"],
                    "description": financial_data.get("description", "Compra procesada por OCR"),
                    "category": financial_data.get("category", "otros"),
                    "payment_method": financial_data.get("payment_method", "desconocido"),
                    "telegram_user_id": telegram_user_id,
                    "confidence": financial_data.get("confidence", 0.7),
                    "source": "ocr_async",
                    "metadata": {
                        "task_id": task_id,
                        "establishment": financial_data.get("establishment"),
                        "receipt_data": ocr_result["receipt_metadata"],
                        "raw_ocr_text": ocr_result["extracted_text"][:500]
                    }
                }

                if financial_data.get("date"):
                    transaction_data["date"] = financial_data["date"]

                transaction = transaction_service.create_transaction(transaction_data)

                result_data["transaction_created"] = True
                result_data["transaction_id"] = transaction.id
                result_data["message"] = f"✅ **Transacción creada desde factura**\n\n" \
                                        f"💰 **${financial_data['amount']:,.0f}** - {financial_data.get('description', 'Compra')}\n" \
                                        f"🏪 **{financial_data.get('establishment', 'Establecimiento no identificado')}**\n" \
                                        f"📊 **{financial_data.get('category', 'otros').title()}**"

                if financial_data.get("confidence", 0) < 0.7:
                    result_data["message"] += "\n\n⚠️ **Baja confianza** - Por favor revisa los datos"

            except Exception as e:
                logger.error(f"Failed to create transaction in task {task_id}: {e}")
                result_data["transaction_created"] = False
                result_data["transaction_error"] = str(e)

        # Clean up image file
        try:
            os.remove(image_path)
            logger.info(f"Cleaned up image file: {image_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up image file {image_path}: {e}")

        logger.info(f"OCR task {task_id} completed successfully")
        return result_data

    except Exception as e:
        logger.error(f"OCR task {task_id} failed: {e}")

        # Clean up image file on error
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except:
            pass

        return {
            "success": False,
            "task_id": task_id,
            "error": str(e)
        }


# Queue manager singleton
queue_manager = OCRQueueManager()