"""
Receipt model - For OCR processed receipts and fiscal information
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to transaction
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, unique=True)

    # File information
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)  # File size in bytes
    file_type = Column(String(10), nullable=False)  # jpg, png, pdf

    # OCR processing
    ocr_text = Column(Text, nullable=True)  # Raw OCR extracted text
    ocr_confidence = Column(Float, nullable=True)  # OCR confidence score
    ocr_engine = Column(String(50), default="tesseract")  # OCR engine used

    # AI processing
    ai_extracted_data = Column(JSON, nullable=True)  # Structured data extracted by AI
    ai_confidence = Column(Float, nullable=True)  # AI confidence in extraction
    ai_model_used = Column(String(50), nullable=True)  # AI model used for extraction

    # Fiscal information (extracted from receipt)
    company_name = Column(String(200), nullable=True)
    company_nit = Column(String(20), nullable=True, index=True)
    receipt_number = Column(String(50), nullable=True, index=True)
    receipt_date = Column(DateTime(timezone=True), nullable=True)

    # Tax information
    subtotal = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)  # IVA
    tax_percentage = Column(Float, nullable=True)  # Tax rate applied
    total_amount = Column(Float, nullable=True)  # Should match transaction amount

    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)  # Error message if processing failed
    needs_review = Column(Boolean, default=False)  # Flag for manual review

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    transaction = relationship("Transaction", back_populates="receipt")

    def __repr__(self):
        return f"<Receipt(id={self.id}, file_name='{self.file_name}', company='{self.company_name}')>"