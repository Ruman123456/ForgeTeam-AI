"""ForgeTeam AI - Project API routes."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.db_models import Project, AgentRun
from app.schemas.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project."""
    project = Project(
        name=data.name,
        description=data.description,
        language_preference=data.language_preference,
        framework_preference=data.framework_preference,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    resp = ProjectResponse.model_validate(project)
    resp.run_count = 0
    return resp


@router.get("", response_model=ProjectListResponse)
def list_projects(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List all projects with pagination."""
    total = db.query(func.count(Project.id)).scalar()
    projects = (
        db.query(Project)
        .order_by(Project.created_at.desc())
        .offset(skip)
        .limit(min(limit, 100))
        .all()
    )

    result = []
    for p in projects:
        resp = ProjectResponse.model_validate(p)
        resp.run_count = db.query(func.count(AgentRun.id)).filter(AgentRun.project_id == p.id).scalar()
        result.append(resp)

    return ProjectListResponse(projects=result, total=total)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get a project by ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    resp = ProjectResponse.model_validate(project)
    resp.run_count = db.query(func.count(AgentRun.id)).filter(AgentRun.project_id == project.id).scalar()
    return resp


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, data: ProjectUpdate, db: Session = Depends(get_db)):
    """Update a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    resp = ProjectResponse.model_validate(project)
    resp.run_count = db.query(func.count(AgentRun.id)).filter(AgentRun.project_id == project.id).scalar()
    return resp


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    """Delete a project and all associated runs."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete associated generated files
    from app.services.artifact_service import artifact_service
    runs = db.query(AgentRun).filter(AgentRun.project_id == project_id).all()
    for run in runs:
        try:
            artifact_service.delete_run_files(run.id)
        except Exception as e:
            logger.warning(f"Failed to delete run files for {run.id}: {e}")

    db.delete(project)
    db.commit()
