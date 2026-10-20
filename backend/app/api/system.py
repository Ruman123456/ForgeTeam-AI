"""ForgeTeam AI - Health, config, and Ollama check routes."""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.db_models import Project, AgentRun
from app.schemas.schemas import (
    HealthResponse,
    ConfigResponse,
    OllamaCheckResponse,
    DashboardStats,
)
from app.services.ollama_client import ollama_client
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["system"])


@router.get("/api/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        db.execute(func.count(Project.id).select())
        db_status = "connected"
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        database=db_status,
        ollama_configured=bool(settings.ollama_base_url),
        demo_mode=settings.demo_mode,
    )


from app.services.groq_client import groq_client

@router.get("/api/config", response_model=ConfigResponse)
async def get_config():
    """Get public configuration."""
    connected = await ollama_client.check_connection()
    model_available = False
    if connected:
        model_available = await ollama_client.check_model_available()

    return ConfigResponse(
        ollama_base_url=settings.ollama_base_url,
        ollama_model=settings.ollama_model,
        demo_mode=settings.demo_mode,
        docker_enabled=settings.docker_enabled,
        max_revision_attempts=settings.max_revision_attempts,
        ollama_connected=connected,
        ollama_model_available=model_available,
        groq_configured=groq_client.is_configured(),
        groq_model=settings.groq_model,
        default_engine=settings.default_engine,
    )


@router.post("/api/groq/check")
async def check_groq():
    """Verify Groq API connection."""
    if not groq_client.is_configured():
        return {
            "configured": False,
            "connected": False,
            "model": settings.groq_model,
            "message": "Groq API key not set. Paste your free key below and click Save & Connect."
        }
    connected = await groq_client.check_connection()
    return {
        "configured": True,
        "connected": connected,
        "model": settings.groq_model,
        "message": "Connected to Groq Cloud free tier!" if connected else "Failed to connect with current key"
    }


@router.post("/api/groq/key")
async def save_groq_key(payload: dict):
    """Save Groq API key directly from UI and test connection."""
    key = payload.get("api_key", "").strip()
    if not key:
        return {"success": False, "connected": False, "message": "Key cannot be empty"}
    groq_client.set_api_key(key)
    connected = await groq_client.check_connection()
    return {
        "success": True,
        "connected": connected,
        "message": "Groq API key verified and saved successfully!" if connected else "Key saved, but connection failed. Please double check the key."
    }


@router.post("/api/ollama/check", response_model=OllamaCheckResponse)
async def check_ollama():
    """Check Ollama connection and list available models."""
    try:
        connected = await ollama_client.check_connection()
        if not connected:
            return OllamaCheckResponse(
                connected=False,
                model_available=False,
                error="Cannot connect to Ollama. Is it running? Start with: ollama serve",
            )

        models = await ollama_client.list_models()
        model_available = any(settings.ollama_model in m for m in models)

        return OllamaCheckResponse(
            connected=True,
            model_available=model_available,
            models=models,
            error=None if model_available else (
                f"Model '{settings.ollama_model}' not found. "
                f"Install with: ollama pull {settings.ollama_model}"
            ),
        )
    except Exception as e:
        return OllamaCheckResponse(
            connected=False,
            model_available=False,
            error=str(e),
        )


@router.get("/api/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    total_projects = db.query(func.count(Project.id)).scalar() or 0
    total_runs = db.query(func.count(AgentRun.id)).scalar() or 0
    completed_runs = (
        db.query(func.count(AgentRun.id))
        .filter(AgentRun.status.in_(["completed", "completed_with_issues"]))
        .scalar() or 0
    )
    failed_runs = (
        db.query(func.count(AgentRun.id))
        .filter(AgentRun.status == "failed")
        .scalar() or 0
    )
    running_runs = (
        db.query(func.count(AgentRun.id))
        .filter(AgentRun.status.in_(["queued", "running"]))
        .scalar() or 0
    )

    return DashboardStats(
        total_projects=total_projects,
        total_runs=total_runs,
        completed_runs=completed_runs,
        failed_runs=failed_runs,
        running_runs=running_runs,
    )
