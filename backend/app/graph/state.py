"""ForgeTeam AI - LangGraph workflow state definition."""

from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    """Shared state for the multi-agent workflow."""

    # Identifiers
    run_id: str
    project_id: str

    # Input
    user_request: str
    demo_mode: bool

    # Agent outputs
    requirements: dict[str, Any]         # Planner output
    architecture: dict[str, Any]         # Architect output
    task_plan: list[dict[str, Any]]      # Task breakdown
    generated_files: dict[str, Any]      # Developer output
    review_output: dict[str, Any]        # Reviewer output
    review_findings: list[dict[str, Any]]  # Reviewer findings
    test_results: dict[str, Any]         # Tester output

    # Workflow control
    current_agent: str
    agent_statuses: dict[str, str]
    agent_messages: list[dict[str, Any]]
    revision_count: int
    max_revisions: int
    run_status: str
    final_summary: str
    error_messages: list[str]

    # Metadata
    timestamps: dict[str, str]
