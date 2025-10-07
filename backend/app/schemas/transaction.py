"""
Transaction Pydantic schemas for API validation
"""

from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class PaymentMethod(str, Enum):
    """Payment method enumeration"""
    CARD = "tarjeta"
    CASH = "efectivo"
    TRANSFER = "transferencia"
    DEBIT = "debito"


class TransactionBase(BaseModel):
    """Base transaction schema"""
    amount: float
    description: str
    payment_method: PaymentMethod
    transaction_date: datetime
    location: Optional[str] = None

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @validator('description')
    def description_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction"""
    category_id: Optional[int] = None
    telegram_message_id: Optional[int] = None
    telegram_user_id: int
    original_text: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_model_used: Optional[str] = None


class TransactionUpdate(BaseModel):
    """Schema for updating an existing transaction"""
    amount: Optional[float] = None
    description: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    transaction_date: Optional[datetime] = None
    location: Optional[str] = None
    category_id: Optional[int] = None
    is_validated: Optional[bool] = None

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        return v


class TransactionResponse(TransactionBase):
    """Schema for transaction responses"""
    id: int
    category_id: Optional[int]
    telegram_message_id: Optional[int]
    telegram_user_id: int
    ai_confidence: Optional[float]
    ai_model_used: Optional[str]
    original_text: Optional[str]
    is_validated: bool
    is_correction: bool
    corrected_transaction_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    # Nested category information
    category_name: Optional[str] = None
    category_color: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionSummary(BaseModel):
    """Schema for transaction summaries and statistics"""
    total_amount: float
    transaction_count: int
    period_start: datetime
    period_end: datetime
    by_category: Dict[str, float]
    by_payment_method: Dict[str, float]
    daily_totals: Dict[str, float]


class TransactionFilter(BaseModel):
    """Schema for filtering transactions"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category_id: Optional[int] = None
    payment_method: Optional[PaymentMethod] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    search_text: Optional[str] = None
    telegram_user_id: Optional[int] = None
    is_validated: Optional[bool] = None