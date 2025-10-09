"""
Category Pydantic schemas for API validation
"""

from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str
    description: Optional[str] = None
    color: str = "#3B82F6"
    icon: Optional[str] = None
    is_active: bool = True
    priority: int = 0

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Category name cannot be empty')
        return v.strip()

    @validator('color')
    def color_must_be_hex(cls, v):
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be a valid hex color (e.g., #3B82F6)')
        return v


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    keywords: Optional[List[str]] = []


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category"""
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Category name cannot be empty')
        return v.strip() if v else v

    @validator('color')
    def color_must_be_hex(cls, v):
        if v is not None and (not v.startswith('#') or len(v) != 7):
            raise ValueError('Color must be a valid hex color (e.g., #3B82F6)')
        return v


class CategoryKeywordResponse(BaseModel):
    """Schema for category keyword responses"""
    id: int
    keyword: str
    weight: float
    is_active: bool
    match_count: int
    success_rate: float

    class Config:
        from_attributes = True


class CategoryResponse(CategoryBase):
    """Schema for category responses"""
    id: int
    is_system: bool
    ai_usage_count: int
    accuracy_score: float
    created_at: datetime
    updated_at: Optional[datetime]

    # Nested keywords
    keywords: List[CategoryKeywordResponse] = []

    # Transaction count (computed field)
    transaction_count: Optional[int] = None

    class Config:
        from_attributes = True


class CategoryStats(BaseModel):
    """Schema for category statistics"""
    category_id: int
    category_name: str
    total_amount: float
    transaction_count: int
    average_amount: float
    last_transaction: Optional[datetime]
    percentage_of_total: float