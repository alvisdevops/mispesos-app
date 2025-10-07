"""
Receipt Pydantic schemas for API validation
"""

from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, Dict, Any


class ReceiptBase(BaseModel):
    """Base receipt schema"""
    file_name: str
    file_type: str

    @validator('file_type')
    def file_type_must_be_valid(cls, v):
        allowed_types = ['jpg', 'jpeg', 'png', 'pdf']
        if v.lower() not in allowed_types:
            raise ValueError(f'File type must be one of: {", ".join(allowed_types)}')
        return v.lower()


class ReceiptCreate(ReceiptBase):
    """Schema for creating a new receipt"""
    transaction_id: int
    file_path: str
    file_size: Optional[int] = None


class ReceiptUpdate(BaseModel):
    """Schema for updating receipt processing results"""
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    ocr_engine: Optional[str] = None
    ai_extracted_data: Optional[Dict[str, Any]] = None
    ai_confidence: Optional[float] = None
    ai_model_used: Optional[str] = None
    company_name: Optional[str] = None
    company_nit: Optional[str] = None
    receipt_number: Optional[str] = None
    receipt_date: Optional[datetime] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    tax_percentage: Optional[float] = None
    total_amount: Optional[float] = None
    is_processed: Optional[bool] = None
    processing_error: Optional[str] = None
    needs_review: Optional[bool] = None


class ReceiptResponse(ReceiptBase):
    """Schema for receipt responses"""
    id: int
    transaction_id: int
    file_path: str
    file_size: Optional[int]
    ocr_text: Optional[str]
    ocr_confidence: Optional[float]
    ocr_engine: Optional[str]
    ai_extracted_data: Optional[Dict[str, Any]]
    ai_confidence: Optional[float]
    ai_model_used: Optional[str]
    company_name: Optional[str]
    company_nit: Optional[str]
    receipt_number: Optional[str]
    receipt_date: Optional[datetime]
    subtotal: Optional[float]
    tax_amount: Optional[float]
    tax_percentage: Optional[float]
    total_amount: Optional[float]
    is_processed: bool
    processing_error: Optional[str]
    needs_review: bool
    created_at: datetime
    updated_at: Optional[datetime]
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReceiptProcessingStatus(BaseModel):
    """Schema for receipt processing status"""
    receipt_id: int
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    message: Optional[str] = None
    estimated_completion: Optional[datetime] = None