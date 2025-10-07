"""
AI and Message Parsing API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.services.message_parser import MessageParserService

router = APIRouter()


class MessageParseRequest(BaseModel):
    """Request schema for message parsing"""
    message: str
    telegram_user_id: Optional[int] = 12345  # Default for testing
    create_transaction: bool = False  # If true, creates transaction


class MessageParseResponse(BaseModel):
    """Response schema for message parsing"""
    success: bool
    extracted_data: dict
    confidence: float
    message: Optional[str] = None
    transaction_id: Optional[int] = None
    error: Optional[str] = None


@router.post("/parse", response_model=MessageParseResponse)
async def parse_message(
    request: MessageParseRequest,
    db: Session = Depends(get_db)
):
    """
    Parse a financial message using AI
    Can optionally create a transaction
    """
    parser_service = MessageParserService(db)

    if request.create_transaction:
        # Parse and create transaction
        result = await parser_service.parse_and_create_transaction(
            message=request.message,
            telegram_user_id=request.telegram_user_id or 12345
        )

        return MessageParseResponse(
            success=result.success,
            extracted_data=result.extracted_data,
            confidence=result.confidence,
            message=result.message,
            transaction_id=result.transaction_id,
            error=result.error
        )
    else:
        # Parse only (preview mode)
        result = await parser_service.parse_message_for_preview(request.message)

        return MessageParseResponse(
            success=result.get('success', False),
            extracted_data=result,
            confidence=result.get('confidence', 0.0),
            error=result.get('error')
        )


@router.get("/test-connection")
async def test_ai_connection(db: Session = Depends(get_db)):
    """Test AI service connection"""

    parser_service = MessageParserService(db)
    is_connected, message = await parser_service.test_ai_connection()

    return {
        "connected": is_connected,
        "message": message,
        "service": "ollama",
        "model": "llama3.2:3b"
    }


@router.post("/examples")
async def test_with_examples(db: Session = Depends(get_db)):
    """Test AI parsing with example messages"""

    parser_service = MessageParserService(db)

    examples = [
        "50k almuerzo tarjeta",
        "pagué 25000 de uber efectivo ayer",
        "compré pizza por 35mil con débito",
        "gasolina 80k transferencia",
        "cine 15000 efectivo",
        "supermercado 120k tarjeta"
    ]

    results = []

    for example in examples:
        try:
            result = await parser_service.parse_message_for_preview(example)
            results.append({
                "input": example,
                "output": result
            })
        except Exception as e:
            results.append({
                "input": example,
                "output": {"error": str(e)}
            })

    return {
        "message": "AI parsing test results",
        "examples_tested": len(examples),
        "results": results
    }