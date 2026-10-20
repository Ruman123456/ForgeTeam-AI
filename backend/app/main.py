"""ForgeTeam AI - FastAPI Application Entry Point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import init_db
from app.api import system, projects, runs

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("forgeteam")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Initializing ForgeTeam AI Database...")
    init_db()
    # Ensure generated projects directory exists
    settings.generated_projects_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Generated projects path: {settings.generated_projects_path}")
    logger.info("ForgeTeam AI Backend ready.")
    yield
    logger.info("ForgeTeam AI Backend shutting down.")


app = FastAPI(
    title="ForgeTeam AI",
    description="Collaborative Multi-Agent AI Software Development Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(system.router)
app.include_router(projects.router)
app.include_router(runs.router)
