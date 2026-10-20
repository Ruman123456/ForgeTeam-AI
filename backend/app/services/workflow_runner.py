"""ForgeTeam AI - Workflow runner service.

Coordinates the multi-agent workflow execution with database persistence.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.graph.workflow import get_compiled_workflow
from app.models.db_models import AgentRun, AgentEvent, Artifact
from app.services.artifact_service import artifact_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class WorkflowRunner:
    """Runs the multi-agent workflow and persists state to the database."""

    def __init__(self):
        self.workflow = get_compiled_workflow()

    async def execute_run(
        self,
        run_id: str,
        project_id: str,
        user_request: str,
        demo_mode: bool = False,
        engine: str = "local",
    ):
        """Execute the full multi-agent workflow for a run.

        This is designed to be called as a background task.
        """
        db = SessionLocal()
        try:
            # Update run status to running
            run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
            if not run:
                logger.error(f"Run {run_id} not found")
                return

            run.status = "running"
            run.started_at = datetime.now(timezone.utc)
            run.current_stage = "planner"
            db.commit()

            self._log_event(db, run_id, "coordinator", "run_started", "running", f"Workflow execution started with engine: {engine}")

            # Build initial state
            initial_state = {
                "run_id": run_id,
                "project_id": project_id,
                "user_request": user_request,
                "demo_mode": demo_mode,
                "engine": engine,
                "requirements": {},
                "architecture": {},
                "task_plan": [],
                "generated_files": {},
                "review_output": {},
                "review_findings": [],
                "test_results": {},
                "current_agent": "coordinator",
                "agent_statuses": {},
                "agent_messages": [],
                "revision_count": 0,
                "max_revisions": settings.max_revision_attempts,
                "run_status": "running",
                "error_messages": [],
                "timestamps": {"started": datetime.now(timezone.utc).isoformat()},
            }

            # Run the graph
            logger.info(f"Starting workflow for run {run_id} (demo_mode={demo_mode})")
            final_state = None

            # Execute the graph step by step to log events
            async for event in self.workflow.astream(initial_state):
                for node_name, node_state in event.items():
                    if isinstance(node_state, dict):
                        final_state = node_state

                        # Update run status in DB
                        current_agent = node_state.get("current_agent", "")
                        run.current_stage = current_agent
                        run.revision_count = node_state.get("revision_count", 0)
                        db.commit()

                        # Log the event
                        messages = node_state.get("agent_messages", [])
                        if messages:
                            latest = messages[-1]
                            self._log_event(
                                db, run_id,
                                latest.get("agent", node_name),
                                latest.get("type", "output"),
                                node_state.get("agent_statuses", {}).get(current_agent, "completed"),
                                latest.get("content", "")[:2000],
                                metadata=json.dumps({"node": node_name})
                            )

            if final_state is None:
                raise Exception("Workflow produced no output")

            # Write generated files to disk
            generated_files = final_state.get("generated_files", {})
            if generated_files.get("files_created"):
                artifact_records = artifact_service.write_generated_files(run_id, generated_files)
                for rec in artifact_records:
                    db_artifact = Artifact(
                        run_id=run_id,
                        relative_path=rec["relative_path"],
                        artifact_type=rec["artifact_type"],
                        description=rec.get("description", ""),
                        checksum=rec.get("checksum"),
                    )
                    db.add(db_artifact)

            # Write test files
            test_results = final_state.get("test_results", {})
            for tf in test_results.get("test_files_created", []):
                if tf.get("path") and tf.get("content"):
                    try:
                        artifact_service.write_file(run_id, tf["path"], tf["content"])
                        db_artifact = Artifact(
                            run_id=run_id,
                            relative_path=tf["path"],
                            artifact_type="test",
                            description=tf.get("description", ""),
                        )
                        db.add(db_artifact)
                    except Exception as e:
                        logger.warning(f"Failed to write test file {tf['path']}: {e}")

            # Write report files
            requirements = final_state.get("requirements", {})
            if requirements:
                report = artifact_service.write_report(
                    run_id, "plan.json", json.dumps(requirements, indent=2)
                )
                if report:
                    db.add(Artifact(run_id=run_id, **report))

            architecture = final_state.get("architecture", {})
            if architecture:
                report = artifact_service.write_report(
                    run_id, "architecture.json", json.dumps(architecture, indent=2)
                )
                if report:
                    db.add(Artifact(run_id=run_id, **report))

            review_output = final_state.get("review_output", {})
            if review_output:
                report = artifact_service.write_report(
                    run_id, "review_report.json", json.dumps(review_output, indent=2)
                )
                if report:
                    db.add(Artifact(run_id=run_id, **report))

            if test_results:
                report = artifact_service.write_report(
                    run_id, "test_report.json", json.dumps(test_results, indent=2)
                )
                if report:
                    db.add(Artifact(run_id=run_id, **report))

            final_summary = final_state.get("final_summary", "")
            if final_summary:
                report = artifact_service.write_report(run_id, "final_report.md", final_summary)
                if report:
                    db.add(Artifact(run_id=run_id, **report))

            # Update run to completed
            run_status = final_state.get("run_status", "completed")
            run.status = run_status
            run.final_summary = final_summary
            run.completed_at = datetime.now(timezone.utc)
            run.current_stage = "completed"

            errors = final_state.get("error_messages", [])
            if errors:
                run.error_summary = "; ".join(errors[:5])

            db.commit()

            self._log_event(
                db, run_id, "coordinator", "run_completed", run_status,
                f"Workflow completed with status: {run_status}"
            )

            logger.info(f"Workflow completed for run {run_id} with status {run_status}")

        except Exception as e:
            logger.error(f"Workflow failed for run {run_id}: {e}", exc_info=True)
            try:
                run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
                if run:
                    run.status = "failed"
                    run.error_summary = str(e)[:1000]
                    run.completed_at = datetime.now(timezone.utc)
                    run.current_stage = "failed"
                    db.commit()

                self._log_event(
                    db, run_id, "coordinator", "run_failed", "failed",
                    f"Workflow error: {str(e)[:500]}"
                )
            except Exception as db_err:
                logger.error(f"Failed to update run status: {db_err}")
        finally:
            db.close()

    def _log_event(
        self, db: Session, run_id: str, agent_name: str,
        event_type: str, status: str, message: str,
        metadata: str = None
    ):
        """Log an agent event to the database."""
        try:
            event = AgentEvent(
                run_id=run_id,
                agent_name=agent_name,
                event_type=event_type,
                status=status,
                message=message[:2000] if message else None,
                metadata_json=metadata,
            )
            db.add(event)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log event: {e}")


# Singleton
workflow_runner = WorkflowRunner()
