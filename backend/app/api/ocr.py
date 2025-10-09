"""
OCR API endpoints for receipt processing
"""

import os
import shutil
import time
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from loguru import logger
import tempfile

try:
    from app.services.ocr_service import OCRService
except ImportError:
    # Fallback to simple OCR service if OpenCV is not available
    from app.services.ocr_service_simple import SimpleOCRService as OCRService
from app.services.transaction_service import TransactionService
from app.services.ocr_queue import queue_manager


router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post("/process-image-async")
async def process_receipt_image_async(
    file: UploadFile = File(...),
    telegram_user_id: int = Query(...),
    create_transaction: bool = Query(True)
) -> Dict[str, Any]:
    """
    Process a receipt image asynchronously using Redis queue

    Args:
        file: Receipt image file (JPG, PNG)
        telegram_user_id: Telegram user ID for transaction creation
        create_transaction: Whether to create a transaction from extracted data

    Returns:
        Task ID for tracking progress
    """

    logger.info(f"Submitting async OCR task for user {telegram_user_id}")

    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only image files are supported."
        )

    # Validate file size (10MB max)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 10MB."
        )

    try:
        # Save file to uploads directory for processing
        uploads_dir = "/app/uploads"
        os.makedirs(uploads_dir, exist_ok=True)

        file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
        temp_filename = f"receipt_{telegram_user_id}_{int(time.time())}.{file_extension}"
        temp_path = os.path.join(uploads_dir, temp_filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Submit to queue
        task_id = await queue_manager.submit_ocr_task(
            image_path=temp_path,
            telegram_user_id=telegram_user_id,
            create_transaction=create_transaction
        )

        return {
            "success": True,
            "task_id": task_id,
            "message": "Image submitted for processing",
            "status": "PENDING"
        }

    except Exception as e:
        logger.error(f"Error submitting OCR task: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting task: {str(e)}"
        )


@router.post("/process-image")
async def process_receipt_image(
    file: UploadFile = File(...),
    telegram_user_id: int = Query(...),
    create_transaction: bool = Query(True)
) -> Dict[str, Any]:
    """
    Process a receipt image with OCR and optionally create a transaction

    Args:
        file: Receipt image file (JPG, PNG)
        telegram_user_id: Telegram user ID for transaction creation
        create_transaction: Whether to create a transaction from extracted data

    Returns:
        OCR results and transaction data
    """

    logger.info(f"Processing receipt image upload from user {telegram_user_id}")

    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only image files are supported."
        )

    # Validate file size (10MB max)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 10MB."
        )

    try:
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            # Copy uploaded file to temp location
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        # Process image with OCR
        ocr_service = OCRService()
        ocr_result = ocr_service.process_receipt_image(temp_path)

        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass

        if not ocr_result["success"]:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": ocr_result.get("error", "OCR processing failed"),
                    "extracted_text": ocr_result.get("extracted_text", ""),
                    "confidence": ocr_result.get("confidence", 0.0)
                }
            )

        response_data = {
            "success": True,
            "extracted_text": ocr_result["extracted_text"],
            "financial_data": ocr_result["financial_data"],
            "receipt_metadata": ocr_result["receipt_metadata"],
            "confidence": ocr_result["confidence"]
        }

        # Create transaction if requested and data is sufficient
        if create_transaction and telegram_user_id and ocr_result["financial_data"].get("amount"):
            try:
                transaction_service = TransactionService()

                # Prepare transaction data
                financial_data = ocr_result["financial_data"]

                transaction_data = {
                    "amount": financial_data["amount"],
                    "description": financial_data.get("description", "Compra procesada por OCR"),
                    "category": financial_data.get("category", "otros"),
                    "payment_method": financial_data.get("payment_method", "desconocido"),
                    "telegram_user_id": telegram_user_id,
                    "confidence": financial_data.get("confidence", 0.7),
                    "source": "ocr",
                    "metadata": {
                        "establishment": financial_data.get("establishment"),
                        "receipt_data": ocr_result["receipt_metadata"],
                        "raw_ocr_text": ocr_result["extracted_text"][:500]  # First 500 chars
                    }
                }

                # Parse date if available
                if financial_data.get("date"):
                    transaction_data["date"] = financial_data["date"]

                # Create transaction
                transaction = await transaction_service.create_transaction(transaction_data)

                response_data["transaction_created"] = True
                response_data["transaction_id"] = transaction.id
                response_data["message"] = f"✅ **Transacción creada desde factura**\n\n" \
                                         f"💰 **${financial_data['amount']:,.0f}** - {financial_data.get('description', 'Compra')}\n" \
                                         f"🏪 **{financial_data.get('establishment', 'Establecimiento no identificado')}**\n" \
                                         f"📊 **{financial_data.get('category', 'otros').title()}**"

                if financial_data.get("confidence", 0) < 0.7:
                    response_data["message"] += "\n\n⚠️ **Baja confianza** - Por favor revisa los datos"

            except Exception as e:
                logger.error(f"Failed to create transaction from OCR data: {e}")
                response_data["transaction_created"] = False
                response_data["transaction_error"] = str(e)

        return response_data

    except Exception as e:
        logger.error(f"Error processing receipt image: {e}")

        # Clean up temp file on error
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass

        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


@router.post("/extract-text")
async def extract_text_only(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Extract text from image without creating transaction

    Args:
        file: Receipt image file

    Returns:
        Raw extracted text and metadata
    """

    logger.info("Processing image for text extraction only")

    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only image files are supported."
        )

    try:
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        # Process image with OCR
        ocr_service = OCRService()
        ocr_result = ocr_service.process_receipt_image(temp_path)

        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass

        return {
            "success": ocr_result["success"],
            "extracted_text": ocr_result.get("extracted_text", ""),
            "receipt_metadata": ocr_result.get("receipt_metadata", {}),
            "error": ocr_result.get("error")
        }

    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")

        # Clean up temp file on error
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass

        raise HTTPException(
            status_code=500,
            detail=f"Error extracting text: {str(e)}"
        )


@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of an OCR processing task

    Args:
        task_id: Task ID to check

    Returns:
        Task status and results
    """

    logger.info(f"Checking status for OCR task {task_id}")

    try:
        status = await queue_manager.get_task_status(task_id)
        return status

    except Exception as e:
        logger.error(f"Error checking task status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking task status: {str(e)}"
        )


@router.delete("/task/{task_id}")
async def cancel_task(task_id: str) -> Dict[str, Any]:
    """
    Cancel a pending OCR task

    Args:
        task_id: Task ID to cancel

    Returns:
        Cancellation status
    """

    logger.info(f"Canceling OCR task {task_id}")

    try:
        success = await queue_manager.cancel_task(task_id)

        return {
            "success": success,
            "message": "Task canceled successfully" if success else "Failed to cancel task",
            "task_id": task_id
        }

    except Exception as e:
        logger.error(f"Error canceling task: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error canceling task: {str(e)}"
        )


@router.get("/test-installation")
async def test_ocr_installation() -> Dict[str, Any]:
    """
    Test OCR installation and configuration

    Returns:
        Installation status and available features
    """

    logger.info("Testing OCR installation")

    try:
        ocr_service = OCRService()
        test_result = ocr_service.test_ocr_installation()

        return {
            "success": test_result["installation_ok"],
            "tesseract_info": test_result,
            "message": "OCR installation is working correctly" if test_result["installation_ok"]
                      else "OCR installation has issues"
        }

    except Exception as e:
        logger.error(f"OCR installation test failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "OCR installation test failed"
        }