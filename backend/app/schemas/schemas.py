"""ForgeTeam AI - Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Project Schemas ──────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str = Field(..., min_length=5, max_length=15000, description="Project requirements")
    language_preference: Optional[str] = Field(None, max_length=100)
    framework_preference: Optional[str] = Field(None, max_length=100)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=5, max_length=15000)
    language_preference: Optional[str] = Field(None, max_length=100)
    framework_preference: Optional[str] = Field(None, max_length=100)


class ProjectEnrichRequest(BaseModel):
    name: Optional[str] = None
    description: str = Field(..., min_length=3, description="Brief or vague project prompt")
    language: Optional[str] = None
    framework: Optional[str] = None


class ProjectEnrichResponse(BaseModel):
    suggested_name: str
    enriched_description: str
    project_type: str = "general"   # "frontend_web", "backend_api", "fullstack", "cli_tool"
    project_tier: str = "medium"    # "small", "medium", "large"
    suggested_language: str
    suggested_framework: str
    key_features: list[str] = []
    summary: str = ""


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    language_preference: Optional[str] = None
    framework_preference: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    run_count: int = 0

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    projects: list["ProjectResponse"]
    total: int


# ── Run Schemas ──────────────────────────────────────────────────

class RunCreate(BaseModel):
    project_id: str = Field(..., description="Project to run agents on")
    demo_mode: bool = Field(False, description="Legacy demo mode flag")
    engine: Optional[str] = Field(None, description="Inference engine: 'local' (Ollama), 'groq' (Groq Free Cloud), or 'demo'")


class RunResponse(BaseModel):
    id: str
    project_id: str
    project_name: str = ""
    original_request: str
    selected_model: Optional[str] = None
    demo_mode: bool
    engine: str = "local"
    status: str
    current_stage: Optional[str] = None
    retry_count: int = 0
    final_summary: Optional[str] = None
    error_summary: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    artifact_count: int = 0
    event_count: int = 0

    model_config = {"from_attributes": True}


class RunListResponse(BaseModel):
    runs: list[RunResponse]
    total: int


# ── Event Schemas ────────────────────────────────────────────────

class EventResponse(BaseModel):
    id: str
    run_id: str
    agent_name: str
    event_type: str
    status: str
    message: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Artifact Schemas ─────────────────────────────────────────────

class ArtifactResponse(BaseModel):
    id: str
    run_id: str
    relative_path: str
    artifact_type: str
    description: Optional[str] = None
    checksum: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ArtifactContentResponse(BaseModel):
    id: str
    relative_path: str
    artifact_type: str
    content: str
    description: Optional[str] = None


# ── Health & Config Schemas ──────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    database: str
    ollama_configured: bool
    demo_mode: bool


class ConfigResponse(BaseModel):
    ollama_base_url: str
    ollama_model: str
    demo_mode: bool
    docker_enabled: bool
    max_revision_attempts: int
    ollama_connected: bool = False
    ollama_model_available: bool = False
    groq_configured: bool = False
    groq_model: str = "llama-3.3-70b-versatile"
    default_engine: str = "local"


class OllamaCheckResponse(BaseModel):
    connected: bool
    model_available: bool
    models: list[str] = []
    error: Optional[str] = None

    model_config = {"protected_namespaces": ()}


# ── Dashboard Schemas ────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_projects: int = 0
    total_runs: int = 0
    completed_runs: int = 0
    failed_runs: int = 0
    running_runs: int = 0


# ── Error Schema ─────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


# ── Coercion Helpers for Robust Agent Parsing ─────────────────────

def _coerce_str_list(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        lines = [line.strip("- *•").strip() for line in v.split("\n") if line.strip()]
        return lines if lines else [v.strip()]
    if isinstance(v, list):
        res = []
        for item in v:
            if isinstance(item, str):
                res.append(item)
            elif isinstance(item, dict):
                text = item.get("description") or item.get("task") or item.get("title") or item.get("step") or item.get("name") or str(item)
                res.append(str(text))
            else:
                res.append(str(item))
        return res
    return [str(v)]


def _coerce_dict_list(v: Any) -> list[dict]:
    if v is None:
        return []
    if isinstance(v, list):
        res = []
        for item in v:
            if isinstance(item, dict):
                res.append(item)
            elif isinstance(item, str):
                res.append({"title": item, "description": item})
            else:
                res.append({"value": str(item)})
        return res
    if isinstance(v, dict):
        return [v]
    if isinstance(v, str):
        return [{"description": v}]
    return []


# ── Agent Output Schemas ─────────────────────────────────────────

from pydantic import field_validator

class PlannerOutput(BaseModel):
    project_summary: str = ""
    requirements: list[str] = []
    task_list: list[dict] = []
    dependencies: list[str] = []
    acceptance_criteria: list[str] = []
    technical_constraints: list[str] = []
    assumptions: list[str] = []
    project_tier: str = "medium"  # "small", "medium", "large"
    project_type: str = "general" # "frontend_web", "backend_api", "fullstack", "cli_tool"
    recommended_stack: dict = {}

    @field_validator("requirements", "dependencies", "acceptance_criteria", "technical_constraints", "assumptions", mode="before")
    @classmethod
    def normalize_str_lists(cls, v):
        return _coerce_str_list(v)

    @field_validator("task_list", mode="before")
    @classmethod
    def normalize_dict_lists(cls, v):
        return _coerce_dict_list(v)


class ArchitectOutput(BaseModel):
    architecture_summary: str = ""
    file_tree: list[str] = []
    component_responsibilities: list[dict] = []
    api_outline: list[dict] = []
    data_model: list[dict] = []
    implementation_plan: list[str] = []
    project_tier: str = "medium"
    project_type: str = "general"

    @field_validator("file_tree", "implementation_plan", mode="before")
    @classmethod
    def normalize_str_lists(cls, v):
        return _coerce_str_list(v)

    @field_validator("component_responsibilities", "api_outline", "data_model", mode="before")
    @classmethod
    def normalize_dict_lists(cls, v):
        return _coerce_dict_list(v)


class DeveloperOutput(BaseModel):
    files_created: list[dict] = []
    implementation_notes: str = ""
    files_changed: list[str] = []

    @field_validator("files_created", mode="before")
    @classmethod
    def normalize_files_created(cls, v):
        if not isinstance(v, list):
            return []
        res = []
        for item in v:
            if isinstance(item, dict):
                path = item.get("path") or item.get("file") or item.get("filename") or "untitled.txt"
                content = item.get("content") or item.get("code") or ""
                desc = item.get("description") or f"Implementation for {path}"
                res.append({"path": str(path), "content": str(content), "description": str(desc)})
        return res

    @field_validator("files_changed", mode="before")
    @classmethod
    def normalize_files_changed(cls, v):
        return _coerce_str_list(v)


class ReviewFinding(BaseModel):
    severity: str = "info"
    category: str = ""
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    description: str = ""
    suggestion: str = ""
    fixed_code_snippet: Optional[str] = None


class ReviewerOutput(BaseModel):
    findings: list[ReviewFinding] = []
    approval: bool = False
    summary: str = ""
    recommendation: str = ""
    quality_score: int = 85

    @field_validator("findings", mode="before")
    @classmethod
    def normalize_findings(cls, v):
        if not isinstance(v, list):
            return []
        res = []
        for item in v:
            if isinstance(item, dict):
                res.append(item)
            elif isinstance(item, str):
                res.append({"severity": "info", "description": item, "suggestion": "Review finding"})
        return res


class TestResult(BaseModel):
    test_name: str = ""
    status: str = "skipped"
    message: str = ""
    file_path: Optional[str] = None


class TesterOutput(BaseModel):
    test_files_created: list[dict] = []
    test_results: list[TestResult] = []
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    blocked: int = 0
    summary: str = ""
    execution_method: str = "static"

    @field_validator("test_files_created", mode="before")
    @classmethod
    def normalize_test_files(cls, v):
        return _coerce_dict_list(v)
