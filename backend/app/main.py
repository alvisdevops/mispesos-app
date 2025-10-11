"""
MisPesos FastAPI Backend
Main application entry point
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings
from app.core.database import engine, Base
from app.api import api_router

# Import models to ensure they are registered with SQLAlchemy
from app.models import transaction, category, receipt


async def warmup_ollama_background():
    """Background task to pre-warm Ollama model after startup"""
    # Wait a bit to ensure FastAPI is fully started and healthy
    await asyncio.sleep(5)

    print("🔥 Starting Ollama pre-warming in background...")
    logger.info("Starting Ollama pre-warming in background")

    try:
        from app.services.ai_service import AIService
        ai_service = AIService()

        # Test connection first
        is_connected = await ai_service.test_connection()
        if is_connected:
            # Send dummy message to initialize model
            await ai_service.parse_financial_message("warmup test 1000")
            print("✅ Ollama model pre-warmed successfully")
            logger.info("Ollama model pre-warmed and ready")
        else:
            print("⚠️  Ollama not available - skipping pre-warm")
            logger.warning("Ollama not available for pre-warming")
    except Exception as e:
        print(f"⚠️  Ollama pre-warm failed: {e}")
        logger.warning(f"Ollama pre-warm failed: {e} - will work on first request")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 MisPesos FastAPI starting up...")

    # Create database tables
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

    # Schedule Ollama pre-warming as background task (non-blocking)
    asyncio.create_task(warmup_ollama_background())
    print("🔥 Ollama pre-warming scheduled in background")

    yield

    # Shutdown
    print("🛑 MisPesos FastAPI shutting down...")


# Create FastAPI application
app = FastAPI(
    title="MisPesos API",
    description="Personal Financial Management System API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MisPesos API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "mispesos-fastapi"
    }