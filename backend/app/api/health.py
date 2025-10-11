"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import httpx

from app.core.database import get_db
from app.core.config import settings
from app.services.metrics_service import get_metrics_service

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "mispesos-fastapi",
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check including database connectivity and metrics"""
    metrics_service = get_metrics_service()

    health_status = {
        "status": "healthy",
        "service": "mispesos-fastapi",
        "version": "1.0.0",
        "checks": {}
    }

    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Check Ollama connectivity
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                health_status["checks"]["ollama"] = {"status": "healthy"}
            else:
                health_status["checks"]["ollama"] = {
                    "status": "degraded",
                    "message": f"HTTP {response.status_code}"
                }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["ollama"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    return health_status


@router.get("/metrics")
async def get_metrics():
    """Get detailed system metrics"""
    metrics_service = get_metrics_service()
    return metrics_service.get_health_status()