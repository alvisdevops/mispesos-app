"""
Transaction model - Core financial transaction data
"""

from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Financial data
    amount = Column(Float, nullable=False, index=True)
    description = Column(String(500), nullable=False)

    # Classification
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    payment_method = Column(String(50), nullable=False)  # tarjeta, efectivo, transferencia

    # Metadata
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    location = Column(String(200), nullable=True)

    # AI processing metadata
    ai_confidence = Column(Float, nullable=True)  # Confidence score from AI parsing
    ai_model_used = Column(String(50), nullable=True)  # Which AI model was used
    original_text = Column(Text, nullable=True)  # Original user message

    # Telegram integration
    telegram_message_id = Column(BigInteger, nullable=True, index=True)
    telegram_user_id = Column(BigInteger, nullable=False, index=True)

    # Status and validation
    is_validated = Column(Boolean, default=False)  # User confirmed the transaction
    is_correction = Column(Boolean, default=False)  # This is a correction of another transaction
    corrected_transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="transactions")
    receipt = relationship("Receipt", back_populates="transaction", uselist=False)

    # Self-referential relationship for corrections
    corrected_transaction = relationship("Transaction", remote_side=[id])

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, description='{self.description}')>"