"""
Transaction API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, AsyncGenerator
from datetime import datetime, timedelta
import json
import asyncio

from app.core.database import get_db
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionSummary,
    TransactionFilter,
    PaymentMethod
)
from app.services.transaction_service import TransactionService

router = APIRouter()


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    service = TransactionService(db)
    return await service.create_transaction(transaction)


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category_id: Optional[int] = None,
    payment_method: Optional[PaymentMethod] = None,
    telegram_user_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get transactions with optional filtering"""
    service = TransactionService(db)

    filters = TransactionFilter(
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        payment_method=payment_method,
        telegram_user_id=telegram_user_id,
        search_text=search
    )

    return await service.get_transactions(skip=skip, limit=limit, filters=filters)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific transaction by ID"""
    service = TransactionService(db)
    transaction = await service.get_transaction(transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing transaction"""
    service = TransactionService(db)
    transaction = await service.update_transaction(transaction_id, transaction_update)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Delete a transaction"""
    service = TransactionService(db)
    success = await service.delete_transaction(transaction_id)

    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {"message": "Transaction deleted successfully"}


@router.post("/{transaction_id}/validate")
async def validate_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Mark a transaction as validated by the user"""
    service = TransactionService(db)
    transaction = await service.validate_transaction(transaction_id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {"message": "Transaction validated", "transaction": transaction}


@router.get("/summary/daily", response_model=TransactionSummary)
async def get_daily_summary(
    date: Optional[datetime] = None,
    telegram_user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get daily transaction summary"""
    service = TransactionService(db)
    target_date = date or datetime.now()

    return await service.get_daily_summary(target_date, telegram_user_id)


@router.get("/summary/weekly", response_model=TransactionSummary)
async def get_weekly_summary(
    start_date: Optional[datetime] = None,
    telegram_user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get weekly transaction summary"""
    service = TransactionService(db)

    if not start_date:
        start_date = datetime.now() - timedelta(days=datetime.now().weekday())

    end_date = start_date + timedelta(days=6)

    return await service.get_period_summary(start_date, end_date, telegram_user_id)


@router.get("/summary/monthly", response_model=TransactionSummary)
async def get_monthly_summary(
    year: Optional[int] = None,
    month: Optional[int] = None,
    telegram_user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get monthly transaction summary"""
    service = TransactionService(db)

    now = datetime.now()
    target_year = year or now.year
    target_month = month or now.month

    start_date = datetime(target_year, target_month, 1)
    if target_month == 12:
        end_date = datetime(target_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(target_year, target_month + 1, 1) - timedelta(days=1)

    return await service.get_period_summary(start_date, end_date, telegram_user_id)


# Global list to store SSE connections
active_connections: List[asyncio.Queue] = []


@router.get("/stream")
async def stream_transactions():
    """Server-Sent Events endpoint for real-time transaction updates"""

    async def event_stream() -> AsyncGenerator[str, None]:
        queue = asyncio.Queue()
        active_connections.append(queue)

        try:
            # Send initial connection confirmation
            yield f"data: {json.dumps({'type': 'connected', 'message': 'SSE connection established'})}\n\n"

            # Keep connection alive and send updates
            while True:
                try:
                    # Wait for new data with timeout for heartbeat
                    data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"

        except asyncio.CancelledError:
            # Client disconnected
            pass
        finally:
            # Clean up connection
            if queue in active_connections:
                active_connections.remove(queue)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


async def broadcast_transaction_update(transaction_data: dict):
    """Broadcast transaction update to all connected SSE clients"""
    if active_connections:
        # Create message with transaction data
        message = {
            "type": "transaction_created",
            "data": transaction_data
        }

        # Send to all connected clients
        for queue in active_connections[:]:  # Use slice to avoid modification during iteration
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                # Remove disconnected clients
                active_connections.remove(queue)


@router.get("/balance/quick")
async def get_quick_balance(
    telegram_user_id: Optional[int] = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get optimized balance calculation for dashboard"""
    service = TransactionService(db)

    # Calculate start date
    start_date = datetime.now() - timedelta(days=days)

    # Get optimized balance data in a single query
    balance_data = await service.get_optimized_balance(start_date, telegram_user_id)

    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": datetime.now().isoformat(),
        "total_expenses": balance_data["total_expenses"],
        "transaction_count": balance_data["transaction_count"],
        "daily_average": balance_data["daily_average"],
        "top_categories": balance_data["top_categories"],
        "payment_methods": balance_data["payment_methods"]
    }