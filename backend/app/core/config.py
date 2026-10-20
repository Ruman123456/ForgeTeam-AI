"""ForgeTeam AI - Core configuration settings."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_debug: bool = True
    log_level: str = "INFO"

    # Database
    database_url: str = "sqlite:///./forgeteam.db"

    # Ollama
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5-coder:3b"
    ollama_timeout: int = 300
    ollama_max_tokens: int = 16384

    # Groq Cloud (Free Tier)
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_timeout: int = 300
    groq_max_tokens: int = 32768

    # Inference Engine & Demo Mode
    default_engine: str = "local"  # "local" or "groq"
    demo_mode: bool = False

    # Generated Projects
    generated_projects_dir: str = "../generated_projects"

    # Workflow
    max_revision_attempts: int = 2

    # Security
    max_file_size_bytes: int = 1_048_576  # 1MB
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Docker (optional sandboxed execution)
    docker_enabled: bool = False
    docker_timeout: int = 60

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def generated_projects_path(self) -> Path:
        base = Path(__file__).resolve().parent.parent.parent
        return (base / self.generated_projects_dir).resolve()

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
