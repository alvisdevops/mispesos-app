"""
Category models - For transaction classification
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Category information
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#3B82F6")  # Hex color for UI
    icon = Column(String(50), nullable=True)  # Icon name for UI

    # Classification settings
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # System categories can't be deleted
    priority = Column(Integer, default=0)  # Higher priority categories are checked first

    # AI learning metadata
    ai_usage_count = Column(Integer, default=0)  # How many times AI selected this category
    accuracy_score = Column(Float, default=0.0)  # User validation accuracy for AI selections

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    transactions = relationship("Transaction", back_populates="category")
    keywords = relationship("CategoryKeyword", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class CategoryKeyword(Base):
    __tablename__ = "category_keywords"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to category
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Keyword data
    keyword = Column(String(100), nullable=False, index=True)
    weight = Column(Float, default=1.0)  # Weight for keyword matching (0.0 to 1.0)
    is_active = Column(Boolean, default=True)

    # Learning metadata
    match_count = Column(Integer, default=0)  # How many times this keyword matched
    success_rate = Column(Float, default=0.0)  # How often this keyword led to correct classification

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="keywords")

    def __repr__(self):
        return f"<CategoryKeyword(id={self.id}, keyword='{self.keyword}', category='{self.category.name if self.category else None}')>"