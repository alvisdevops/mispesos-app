"""
API routes and endpoints
"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# Import and include route modules
from . import transactions, health, telegram, ai, ocr, categories


# Include route modules
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(ocr.router, tags=["ocr"])
api_router.include_router(categories.router, tags=["categories"])