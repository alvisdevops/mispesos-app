"""
MisPesos FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from contextlib import asynccontextmanager
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time

from app.core.config import settings
from app.core.database import engine, Base
from app.core.telemetry import setup_telemetry
from app.core.logging_config import setup_logging
from app.api import api_router
from app.services.prometheus_metrics import track_http_request
from app.middleware import tracing_middleware

# Import models to ensure they are registered with SQLAlchemy
from app.models import transaction, category, receipt


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 MisPesos FastAPI starting up...")

    # Setup structured logging with trace context
    print("📝 Configuring structured logging...")
    setup_logging()

    # Create database tables
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

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

# Setup OpenTelemetry tracing BEFORE any middleware
print("🔍 Configuring OpenTelemetry tracing...")
setup_telemetry(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Tracing middleware (must be first to generate trace IDs)
@app.middleware("http")
async def tracing_middleware_wrapper(request: Request, call_next):
    """Add trace IDs to all requests"""
    return await tracing_middleware(request, call_next)


# Prometheus metrics middleware
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    """Track HTTP requests with Prometheus metrics"""
    # Skip metrics endpoint to avoid recursion
    if request.url.path == "/metrics":
        return await call_next(request)

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    # Track the request
    track_http_request(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        duration=duration
    )

    return response


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


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )