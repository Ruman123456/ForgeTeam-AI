"""ForgeTeam AI - Run API routes."""

import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.db_models import AgentRun, AgentEvent, Artifact, Project
from app.schemas.schemas import (
    RunCreate,
    RunResponse,
    RunListResponse,
    EventResponse,
    ArtifactResponse,
    ArtifactContentResponse,
)
from app.services.workflow_runner import workflow_runner
from app.services.artifact_service import artifact_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/runs", tags=["runs"])


def _build_run_response(run: AgentRun, db: Session) -> RunResponse:
    """Build a RunResponse from a database run record."""
    project = db.query(Project).filter(Project.id == run.project_id).first()
    artifact_count = db.query(func.count(Artifact.id)).filter(Artifact.run_id == run.id).scalar()
    event_count = db.query(func.count(AgentEvent.id)).filter(AgentEvent.run_id == run.id).scalar()

    return RunResponse(
        id=run.id,
        project_id=run.project_id,
        project_name=project.name if project else "Unknown",
        original_request=run.original_request,
        selected_model=run.selected_model,
        demo_mode=run.demo_mode,
        status=run.status,
        current_stage=run.current_stage,
        retry_count=run.retry_count,
        final_summary=run.final_summary,
        error_summary=run.error_summary,
        created_at=run.created_at,
        started_at=run.started_at,
        completed_at=run.completed_at,
        artifact_count=artifact_count,
        event_count=event_count,
    )


@router.post("", response_model=RunResponse, status_code=201)
def create_run(
    data: RunCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Create a new agent run and start the workflow."""
    # Validate project exists
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Determine engine and model
    engine = data.engine if data.engine in ("local", "groq", "demo") else ("demo" if data.demo_mode else settings.default_engine)
    is_demo = engine == "demo"
    if engine == "groq":
        model = f"groq:{settings.groq_model}"
    elif engine == "local":
        model = f"ollama:{settings.ollama_model}"
    else:
        model = "demo:mock"

    # Create run record
    run = AgentRun(
        project_id=project.id,
        original_request=project.description,
        selected_model=model,
        demo_mode=is_demo,
        status="queued",
        current_stage="queued",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Start workflow in background
    background_tasks.add_task(
        workflow_runner.execute_run,
        run_id=run.id,
        project_id=project.id,
        user_request=project.description,
        demo_mode=is_demo,
        engine=engine,
    )

    logger.info(f"Created run {run.id} for project {project.id} (engine={engine})")
    resp = _build_run_response(run, db)
    resp.engine = engine
    return resp


@router.get("", response_model=RunListResponse)
def list_runs(
    skip: int = 0,
    limit: int = 50,
    project_id: str = None,
    status: str = None,
    db: Session = Depends(get_db),
):
    """List runs with optional filtering."""
    query = db.query(AgentRun)

    if project_id:
        query = query.filter(AgentRun.project_id == project_id)
    if status:
        query = query.filter(AgentRun.status == status)

    total = query.count()
    runs = query.order_by(AgentRun.created_at.desc()).offset(skip).limit(min(limit, 100)).all()

    return RunListResponse(
        runs=[_build_run_response(r, db) for r in runs],
        total=total,
    )


@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    """Get a run by ID."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _build_run_response(run, db)


@router.get("/{run_id}/logs", response_model=list[EventResponse])
def get_run_logs(run_id: str, db: Session = Depends(get_db)):
    """Get the event log for a run."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    events = (
        db.query(AgentEvent)
        .filter(AgentEvent.run_id == run_id)
        .order_by(AgentEvent.created_at.asc())
        .all()
    )
    return [EventResponse.model_validate(e) for e in events]


@router.get("/{run_id}/artifacts", response_model=list[ArtifactResponse])
def get_run_artifacts(run_id: str, db: Session = Depends(get_db)):
    """List artifacts for a run."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    artifacts = (
        db.query(Artifact)
        .filter(Artifact.run_id == run_id)
        .order_by(Artifact.relative_path.asc())
        .all()
    )
    return [ArtifactResponse.model_validate(a) for a in artifacts]


@router.get("/{run_id}/artifacts/{artifact_id}", response_model=ArtifactContentResponse)
def get_artifact_content(run_id: str, artifact_id: str, db: Session = Depends(get_db)):
    """Get an artifact's content."""
    artifact = (
        db.query(Artifact)
        .filter(Artifact.id == artifact_id, Artifact.run_id == run_id)
        .first()
    )
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    content = artifact_service.read_file(run_id, artifact.relative_path)
    if content is None:
        raise HTTPException(status_code=404, detail="Artifact file not found on disk")

    return ArtifactContentResponse(
        id=artifact.id,
        relative_path=artifact.relative_path,
        artifact_type=artifact.artifact_type,
        content=content,
        description=artifact.description,
    )


@router.get("/{run_id}/download")
def download_run(run_id: str, db: Session = Depends(get_db)):
    """Download a ZIP archive of the run's generated project."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    zip_bytes = artifact_service.create_zip(run_id)
    if not zip_bytes:
        raise HTTPException(status_code=404, detail="No artifacts found for this run")

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="forgeteam-{run_id[:8]}.zip"'},
    )


@router.post("/{run_id}/cancel")
def cancel_run(run_id: str, db: Session = Depends(get_db)):
    """Request cancellation of a running workflow."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if run.status not in ("queued", "running"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel run with status '{run.status}'"
        )

    run.status = "cancelled"
    run.error_summary = "Cancelled by user"
    db.commit()

    return {"message": "Cancellation requested", "run_id": run_id}
