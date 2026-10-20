"""Tests for LangGraph workflow, agents, and artifact generation."""

import pytest
import asyncio
from app.graph.workflow import get_compiled_workflow, revision_decision, test_decision as check_test_decision
from app.graph.state import WorkflowState
from app.agents.demo_outputs import (
    get_demo_planner_output,
    get_demo_architect_output,
    get_demo_developer_output,
    get_demo_reviewer_output,
    get_demo_tester_output,
)
from app.services.artifact_service import artifact_service


def test_demo_outputs_structure():
    # Verify Planner
    planner_out = get_demo_planner_output("Build a real-time collaborative code editor")
    assert len(planner_out.requirements) > 0
    assert len(planner_out.task_list) > 0

    # Verify Architect
    architect_out = get_demo_architect_output("Collaborative editor")
    assert len(architect_out.file_tree) > 0
    assert len(architect_out.api_outline) > 0

    # Verify Developer
    dev_out = get_demo_developer_output(architect_out.file_tree)
    assert len(dev_out.files_created) > 0
    assert any("main.py" in f["path"] for f in dev_out.files_created)

    # Verify Reviewer (iteration 0 requires revision, iteration 1 approves)
    rev_out_0 = get_demo_reviewer_output(dev_out.files_created, iteration=0)
    assert rev_out_0.approval is False
    assert len(rev_out_0.findings) > 0

    rev_out_1 = get_demo_reviewer_output(dev_out.files_created, iteration=1)
    assert rev_out_1.approval is True

    # Verify Tester
    tester_out = get_demo_tester_output(dev_out.files_created)
    assert tester_out.passed > 0
    assert tester_out.skipped > 0
    assert tester_out.failed == 0


def test_conditional_edges_routing():
    # Revision decision: when not approved and under limit -> developer
    state_revise: WorkflowState = {
        "review_output": {"approval": False},
        "revision_count": 1,
        "max_revisions": 2,
    }
    assert revision_decision(state_revise) == "developer"

    # When max revisions reached -> proceed to tester even if not approved
    state_limit: WorkflowState = {
        "review_output": {"approval": False},
        "revision_count": 3,
        "max_revisions": 2,
    }
    assert revision_decision(state_limit) == "tester"

    # Test decision: passed tests -> final report
    state_tests_pass: WorkflowState = {
        "test_results": {"failed": 0},
        "revision_count": 1,
        "max_revisions": 2,
    }
    assert check_test_decision(state_tests_pass) == "final_report"


def test_artifact_service_path_traversal_prevention(tmp_path):
    run_id = "test-run-123"
    artifact_service.base_dir = tmp_path

    # Legitimate write
    p = artifact_service.write_file(run_id, "src/index.py", "print('hello')")
    assert p.exists()

    # Traversal write attempts should fail
    with pytest.raises(ValueError):
        artifact_service.write_file(run_id, "../escape.txt", "evil")

    with pytest.raises(ValueError):
        artifact_service.write_file(run_id, "/root/escape.txt", "evil")

    # ZIP archive creation
    zip_bytes = artifact_service.create_zip(run_id)
    assert zip_bytes is not None
    assert len(zip_bytes) > 0


@pytest.mark.asyncio
async def test_full_compiled_workflow_execution():
    workflow = get_compiled_workflow()
    initial_state = {
        "run_id": "test-graph-run",
        "project_id": "proj-123",
        "user_request": "Build a secure REST API for task scheduling",
        "demo_mode": True,
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
        "max_revisions": 2,
        "run_status": "running",
        "error_messages": [],
        "timestamps": {},
    }

    final_state = await workflow.ainvoke(initial_state)
    assert final_state["run_status"] in ("completed", "completed_with_issues")
    assert len(final_state["agent_messages"]) >= 5
    assert "planner" in final_state["agent_statuses"]
    assert "architect" in final_state["agent_statuses"]
    assert "developer" in final_state["agent_statuses"]
    assert "reviewer" in final_state["agent_statuses"]
    assert "tester" in final_state["agent_statuses"]
    assert "final_summary" in final_state
