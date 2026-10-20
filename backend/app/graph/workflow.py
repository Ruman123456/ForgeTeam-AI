"""ForgeTeam AI - LangGraph workflow definition.

Defines the complete multi-agent workflow graph:
START → PLANNER → ARCHITECT → DEVELOPER → REVIEWER → REVISION_DECISION
→ TESTER → TEST_DECISION → FINAL_REPORT → END

With conditional retry loops from reviewer/tester back to developer.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Literal

from langgraph.graph import StateGraph, END

from app.agents.agent_impl import (
    run_planner,
    run_architect,
    run_developer,
    run_reviewer,
    run_tester,
)
from app.graph.state import WorkflowState
from app.core.config import settings

logger = logging.getLogger(__name__)


# ── Node wrappers that add status tracking ───────────────────────

async def planner_node(state: WorkflowState) -> WorkflowState:
    state["agent_statuses"] = state.get("agent_statuses", {})
    state["agent_statuses"]["planner"] = "running"
    state["current_agent"] = "planner"
    ts = datetime.now(timezone.utc).isoformat()
    state.setdefault("timestamps", {})["planner_start"] = ts

    state = await run_planner(state)

    state["agent_statuses"]["planner"] = "completed"
    state["timestamps"]["planner_end"] = datetime.now(timezone.utc).isoformat()
    return state


async def architect_node(state: WorkflowState) -> WorkflowState:
    state["agent_statuses"] = state.get("agent_statuses", {})
    state["agent_statuses"]["architect"] = "running"
    state["current_agent"] = "architect"
    state.setdefault("timestamps", {})["architect_start"] = datetime.now(timezone.utc).isoformat()

    state = await run_architect(state)

    state["agent_statuses"]["architect"] = "completed"
    state["timestamps"]["architect_end"] = datetime.now(timezone.utc).isoformat()
    return state


async def developer_node(state: WorkflowState) -> WorkflowState:
    state["agent_statuses"] = state.get("agent_statuses", {})
    state["agent_statuses"]["developer"] = "running"
    state["current_agent"] = "developer"
    state.setdefault("timestamps", {})["developer_start"] = datetime.now(timezone.utc).isoformat()

    state = await run_developer(state)

    state["agent_statuses"]["developer"] = "completed"
    state["timestamps"]["developer_end"] = datetime.now(timezone.utc).isoformat()
    return state


async def reviewer_node(state: WorkflowState) -> WorkflowState:
    state["agent_statuses"] = state.get("agent_statuses", {})
    state["agent_statuses"]["reviewer"] = "running"
    state["current_agent"] = "reviewer"
    state.setdefault("timestamps", {})["reviewer_start"] = datetime.now(timezone.utc).isoformat()

    state = await run_reviewer(state)

    state["agent_statuses"]["reviewer"] = "completed"
    state["timestamps"]["reviewer_end"] = datetime.now(timezone.utc).isoformat()

    review = state.get("review_output", {})
    if not review.get("approval", True):
        state["revision_count"] = state.get("revision_count", 0) + 1
    return state


async def tester_node(state: WorkflowState) -> WorkflowState:
    state["agent_statuses"] = state.get("agent_statuses", {})
    state["agent_statuses"]["tester"] = "running"
    state["current_agent"] = "tester"
    state.setdefault("timestamps", {})["tester_start"] = datetime.now(timezone.utc).isoformat()

    state = await run_tester(state)

    state["agent_statuses"]["tester"] = "completed"
    state["timestamps"]["tester_end"] = datetime.now(timezone.utc).isoformat()

    tests = state.get("test_results", {})
    if tests.get("failed", 0) > 0:
        state["revision_count"] = state.get("revision_count", 0) + 1
    return state


async def final_report_node(state: WorkflowState) -> WorkflowState:
    """Produce the final run summary."""
    state["current_agent"] = "coordinator"
    state.setdefault("agent_statuses", {})["coordinator"] = "running"

    requirements = state.get("requirements", {})
    review = state.get("review_output", {})
    tests = state.get("test_results", {})
    errors = state.get("error_messages", [])
    revision_count = state.get("revision_count", 0)

    # Determine final status
    has_errors = bool(errors)
    review_approved = review.get("approval", True)
    tests_failed = tests.get("failed", 0)

    if has_errors:
        status = "completed_with_issues"
    elif tests_failed > 0 or not review_approved:
        status = "completed_with_issues"
    else:
        status = "completed"

    summary_parts = [
        f"## ForgeTeam AI - Run Report",
        f"",
        f"### Project Summary",
        f"{requirements.get('project_summary', 'N/A')}",
        f"",
        f"### Workflow Results",
        f"- **Status**: {status}",
        f"- **Revision Cycles**: {revision_count}",
        f"- **Files Generated**: {len(state.get('generated_files', {}).get('files_created', []))}",
        f"",
        f"### Code Review",
        f"- **Approved**: {review.get('approval', 'N/A')}",
        f"- **Findings**: {len(review.get('findings', []))}",
        f"- **Summary**: {review.get('summary', 'N/A')}",
        f"",
        f"### Testing",
        f"- **Passed**: {tests.get('passed', 0)}",
        f"- **Failed**: {tests.get('failed', 0)}",
        f"- **Skipped**: {tests.get('skipped', 0)}",
        f"- **Blocked**: {tests.get('blocked', 0)}",
        f"- **Method**: {tests.get('execution_method', 'N/A')}",
        f"",
    ]

    if errors:
        summary_parts.append("### Errors")
        for err in errors:
            summary_parts.append(f"- {err}")
        summary_parts.append("")

    outstanding = [
        f for f in review.get("findings", [])
        if f.get("severity") in ("error", "warning")
    ]
    if outstanding:
        summary_parts.append("### Outstanding Issues")
        for finding in outstanding:
            summary_parts.append(
                f"- [{finding.get('severity', 'info').upper()}] "
                f"{finding.get('file_path', 'general')}: {finding.get('description', '')}"
            )
        summary_parts.append("")

    state["final_summary"] = "\n".join(summary_parts)
    state["run_status"] = status
    state["agent_statuses"]["coordinator"] = "completed"
    state["agent_messages"] = state.get("agent_messages", []) + [
        {"agent": "coordinator", "type": "final_report", "content": f"Run {status}. {len(errors)} errors."}
    ]
    state.setdefault("timestamps", {})["completed"] = datetime.now(timezone.utc).isoformat()
    return state


# ── Conditional edges ────────────────────────────────────────────

def revision_decision(state: WorkflowState) -> Literal["developer", "tester"]:
    """Decide whether to send code back for revision or proceed to testing."""
    review = state.get("review_output", {})
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", settings.max_revision_attempts)

    if not review.get("approval", True) and revision_count <= max_revisions:
        logger.info(f"Revision needed. Count: {revision_count}/{max_revisions}")
        return "developer"

    if not review.get("approval", True):
        logger.info(f"Revision limit reached ({max_revisions}). Proceeding to testing.")

    return "tester"


def test_decision(state: WorkflowState) -> Literal["developer", "final_report"]:
    """Decide whether test failures warrant another development cycle."""
    tests = state.get("test_results", {})
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", settings.max_revision_attempts)

    failed = tests.get("failed", 0)

    if failed > 0 and revision_count <= max_revisions:
        logger.info(f"Test failures detected. Sending back to developer. Count: {revision_count}")
        return "developer"

    return "final_report"


# ── Build the graph ──────────────────────────────────────────────

def build_workflow() -> StateGraph:
    """Build and compile the multi-agent workflow graph."""
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("tester", tester_node)
    workflow.add_node("final_report", final_report_node)

    # Define edges - linear flow with conditional branches
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "architect")
    workflow.add_edge("architect", "developer")
    workflow.add_edge("developer", "reviewer")

    # After review: either revise or test
    workflow.add_conditional_edges(
        "reviewer",
        revision_decision,
        {
            "developer": "developer",
            "tester": "tester",
        },
    )

    # After testing: either revise or finalize
    workflow.add_conditional_edges(
        "tester",
        test_decision,
        {
            "developer": "developer",
            "final_report": "final_report",
        },
    )

    workflow.add_edge("final_report", END)

    return workflow


def get_compiled_workflow():
    """Get a compiled workflow ready for execution."""
    graph = build_workflow()
    return graph.compile()
