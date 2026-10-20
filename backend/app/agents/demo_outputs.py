"""ForgeTeam AI - Demo mode mock outputs for all agents."""

from app.schemas.schemas import (
    PlannerOutput,
    ArchitectOutput,
    DeveloperOutput,
    ReviewFinding,
    ReviewerOutput,
    TestResult,
    TesterOutput,
)


def get_demo_planner_output(user_request: str) -> PlannerOutput:
    """Generate deterministic planner output for demo mode."""
    return PlannerOutput(
        project_summary=f"A comprehensive software project based on the request: {user_request[:200]}",
        requirements=[
            "User authentication and registration system",
            "Core CRUD operations for main entities",
            "Dashboard with key metrics and visualizations",
            "RESTful API with proper validation",
            "Responsive user interface",
            "Data persistence with database storage",
            "Error handling and input validation",
            "Basic search and filtering capabilities",
        ],
        task_list=[
            {"id": "T1", "title": "Setup project structure", "priority": "high", "depends_on": []},
            {"id": "T2", "title": "Implement data models", "priority": "high", "depends_on": ["T1"]},
            {"id": "T3", "title": "Create API endpoints", "priority": "high", "depends_on": ["T2"]},
            {"id": "T4", "title": "Build authentication system", "priority": "high", "depends_on": ["T2"]},
            {"id": "T5", "title": "Implement business logic", "priority": "medium", "depends_on": ["T3"]},
            {"id": "T6", "title": "Create frontend components", "priority": "medium", "depends_on": ["T3"]},
            {"id": "T7", "title": "Build dashboard view", "priority": "medium", "depends_on": ["T5", "T6"]},
            {"id": "T8", "title": "Add search and filtering", "priority": "low", "depends_on": ["T5"]},
            {"id": "T9", "title": "Write tests", "priority": "medium", "depends_on": ["T5"]},
            {"id": "T10", "title": "Documentation", "priority": "low", "depends_on": ["T7"]},
        ],
        dependencies=[
            "Python 3.11+",
            "FastAPI",
            "SQLAlchemy",
            "React with TypeScript",
            "SQLite",
            "Pydantic",
            "pytest",
        ],
        acceptance_criteria=[
            "Users can register and log in",
            "CRUD operations work for all entities",
            "Dashboard displays accurate metrics",
            "API returns proper error responses",
            "UI is responsive on desktop and mobile",
            "All critical paths have test coverage",
        ],
        technical_constraints=[
            "Must run locally without cloud dependencies",
            "SQLite for data storage",
            "No paid API dependencies",
        ],
        assumptions=[
            "Single-user application for MVP",
            "No real-time collaboration needed initially",
            "English-only interface",
        ],
    )


def get_demo_architect_output(project_summary: str) -> ArchitectOutput:
    """Generate deterministic architect output for demo mode."""
    return ArchitectOutput(
        architecture_summary=(
            "A clean three-tier architecture with a FastAPI backend, SQLite database, "
            "and React TypeScript frontend. The backend follows a layered pattern with "
            "separate routers, services, models, and schemas."
        ),
        file_tree=[
            "src/",
            "src/main.py",
            "src/config.py",
            "src/database.py",
            "src/models/",
            "src/models/__init__.py",
            "src/models/user.py",
            "src/models/task.py",
            "src/routers/",
            "src/routers/__init__.py",
            "src/routers/auth.py",
            "src/routers/tasks.py",
            "src/routers/dashboard.py",
            "src/schemas/",
            "src/schemas/__init__.py",
            "src/schemas/user.py",
            "src/schemas/task.py",
            "src/services/",
            "src/services/auth_service.py",
            "src/services/task_service.py",
            "tests/",
            "tests/test_auth.py",
            "tests/test_tasks.py",
            "tests/conftest.py",
            "requirements.txt",
            "README.md",
        ],
        component_responsibilities=[
            {"component": "main.py", "responsibility": "FastAPI application entry point and configuration"},
            {"component": "database.py", "responsibility": "Database connection and session management"},
            {"component": "models/", "responsibility": "SQLAlchemy ORM models for data entities"},
            {"component": "routers/", "responsibility": "API endpoint definitions and request handling"},
            {"component": "schemas/", "responsibility": "Pydantic models for request/response validation"},
            {"component": "services/", "responsibility": "Business logic and data access layer"},
        ],
        api_outline=[
            {"method": "POST", "path": "/api/auth/register", "description": "Register a new user"},
            {"method": "POST", "path": "/api/auth/login", "description": "User login"},
            {"method": "GET", "path": "/api/tasks", "description": "List tasks with filtering"},
            {"method": "POST", "path": "/api/tasks", "description": "Create a new task"},
            {"method": "GET", "path": "/api/tasks/{id}", "description": "Get task details"},
            {"method": "PUT", "path": "/api/tasks/{id}", "description": "Update a task"},
            {"method": "DELETE", "path": "/api/tasks/{id}", "description": "Delete a task"},
            {"method": "GET", "path": "/api/dashboard", "description": "Get dashboard metrics"},
        ],
        data_model=[
            {
                "entity": "User",
                "fields": ["id: UUID", "username: str", "email: str", "password_hash: str", "created_at: datetime"],
            },
            {
                "entity": "Task",
                "fields": [
                    "id: UUID", "title: str", "description: str", "priority: enum",
                    "status: enum", "deadline: datetime", "user_id: UUID", "created_at: datetime",
                ],
            },
        ],
        implementation_plan=[
            "1. Set up project structure and configuration",
            "2. Create database models and migrations",
            "3. Implement authentication endpoints",
            "4. Build task CRUD endpoints",
            "5. Add dashboard aggregation endpoint",
            "6. Implement input validation and error handling",
            "7. Write unit and integration tests",
            "8. Create README with setup instructions",
        ],
    )


def get_demo_developer_output(file_tree: list[str]) -> DeveloperOutput:
    """Generate deterministic developer output with real file content."""
    files = [
        {
            "path": "src/main.py",
            "content": '''"""Main application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base
from src.routers import auth, tasks, dashboard

app = FastAPI(title="Task Manager", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
''',
            "description": "FastAPI application entry point",
        },
        {
            "path": "src/config.py",
            "content": '''"""Application configuration."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/app.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
''',
            "description": "Configuration settings",
        },
        {
            "path": "src/database.py",
            "content": '''"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
            "description": "Database setup with SQLAlchemy",
        },
        {
            "path": "src/models/__init__.py",
            "content": '"""Data models package."""\n',
            "description": "Models package init",
        },
        {
            "path": "src/models/user.py",
            "content": '''"""User data model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
''',
            "description": "User SQLAlchemy model",
        },
        {
            "path": "src/models/task.py",
            "content": '''"""Task data model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from src.database import Base


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), default=Priority.MEDIUM.value)
    status = Column(String(20), default=Status.TODO.value)
    deadline = Column(DateTime, nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
''',
            "description": "Task SQLAlchemy model with priority and status enums",
        },
        {
            "path": "src/routers/__init__.py",
            "content": '"""API routers package."""\n',
            "description": "Routers package init",
        },
        {
            "path": "src/routers/auth.py",
            "content": '''"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas.user import UserCreate, UserResponse
from src.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    service = AuthService(db)
    existing = service.get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    existing = service.get_user_by_username(user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = service.create_user(user_data)
    return user


@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.authenticate(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.id}
''',
            "description": "Authentication API endpoints",
        },
        {
            "path": "src/routers/tasks.py",
            "content": '''"""Task management endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from src.services.task_service import TaskService

router = APIRouter()


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    user_id: str = Query(...),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = TaskService(db)
    return service.list_tasks(user_id, status=status, priority=priority)


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    service = TaskService(db)
    return service.create_task(task_data)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, task_data: TaskUpdate, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.update_task(task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    service = TaskService(db)
    if not service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
''',
            "description": "Task CRUD API endpoints",
        },
        {
            "path": "src/routers/dashboard.py",
            "content": '''"""Dashboard endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.services.task_service import TaskService

router = APIRouter()


@router.get("/")
def get_dashboard(user_id: str = Query(...), db: Session = Depends(get_db)):
    service = TaskService(db)
    tasks = service.list_tasks(user_id)
    total = len(tasks)
    by_status = {}
    by_priority = {}
    for t in tasks:
        by_status[t.status] = by_status.get(t.status, 0) + 1
        by_priority[t.priority] = by_priority.get(t.priority, 0) + 1
    return {
        "total_tasks": total,
        "by_status": by_status,
        "by_priority": by_priority,
    }
''',
            "description": "Dashboard metrics API endpoint",
        },
        {
            "path": "src/schemas/__init__.py",
            "content": '"""Pydantic schemas package."""\n',
            "description": "Schemas package init",
        },
        {
            "path": "src/schemas/user.py",
            "content": '''"""User schemas for validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
''',
            "description": "User Pydantic schemas",
        },
        {
            "path": "src/schemas/task.py",
            "content": '''"""Task schemas for validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="medium")
    deadline: Optional[datetime] = None
    user_id: str


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    priority: str
    status: str
    deadline: Optional[datetime]
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
''',
            "description": "Task Pydantic schemas",
        },
        {
            "path": "src/services/auth_service.py",
            "content": '''"""Authentication service."""
import hashlib
from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.user import UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, data: UserCreate) -> User:
        user = User(
            username=data.username,
            email=data.email,
            password_hash=self._hash_password(data.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def authenticate(self, username: str, password: str):
        user = self.get_user_by_username(username)
        if user and user.password_hash == self._hash_password(password):
            return user
        return None
''',
            "description": "Authentication business logic",
        },
        {
            "path": "src/services/task_service.py",
            "content": '''"""Task management service."""
from typing import Optional
from sqlalchemy.orm import Session
from src.models.task import Task
from src.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def list_tasks(self, user_id: str, status: Optional[str] = None,
                   priority: Optional[str] = None) -> list[Task]:
        query = self.db.query(Task).filter(Task.user_id == user_id)
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        return query.order_by(Task.created_at.desc()).all()

    def create_task(self, data: TaskCreate) -> Task:
        task = Task(
            title=data.title,
            description=data.description,
            priority=data.priority,
            deadline=data.deadline,
            user_id=data.user_id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def update_task(self, task_id: str, data: TaskUpdate) -> Optional[Task]:
        task = self.get_task(task_id)
        if not task:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: str) -> bool:
        task = self.get_task(task_id)
        if not task:
            return False
        self.db.delete(task)
        self.db.commit()
        return True
''',
            "description": "Task CRUD business logic",
        },
        {
            "path": "tests/conftest.py",
            "content": '''"""Test configuration and fixtures."""
import pytest
from src.database import Base, engine, SessionLocal


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
''',
            "description": "Pytest fixtures for database setup",
        },
        {
            "path": "tests/test_auth.py",
            "content": '''"""Authentication tests."""
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_register_user():
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"


def test_register_duplicate_email():
    client.post("/api/auth/register", json={
        "username": "user1",
        "email": "dup@example.com",
        "password": "securepassword123",
    })
    response = client.post("/api/auth/register", json={
        "username": "user2",
        "email": "dup@example.com",
        "password": "securepassword123",
    })
    assert response.status_code == 400
''',
            "description": "Authentication endpoint tests",
        },
        {
            "path": "tests/test_tasks.py",
            "content": '''"""Task management tests."""
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_create_task():
    # First create a user
    user_resp = client.post("/api/auth/register", json={
        "username": "taskuser",
        "email": "tasks@example.com",
        "password": "securepassword123",
    })
    user_id = user_resp.json()["id"]

    response = client.post("/api/tasks/", json={
        "title": "Test Task",
        "description": "A test task",
        "priority": "high",
        "user_id": user_id,
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"


def test_list_empty_tasks():
    response = client.get("/api/tasks/", params={"user_id": "nonexistent"})
    assert response.status_code == 200
    assert response.json() == []
''',
            "description": "Task endpoint tests",
        },
        {
            "path": "requirements.txt",
            "content": "fastapi==0.115.0\nuvicorn==0.30.6\nsqlalchemy==2.0.35\npydantic==2.9.2\npython-dotenv==1.0.1\npytest==8.3.3\nhttpx==0.27.2\n",
            "description": "Python dependencies",
        },
        {
            "path": "README.md",
            "content": """# Task Manager Application

A task management application with user registration, task creation, priorities, deadlines, and a dashboard.

## Setup

```bash
pip install -r requirements.txt
python -m uvicorn src.main:app --reload
```

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Running Tests

```bash
pytest tests/ -v
```
""",
            "description": "Project README with setup instructions",
        },
    ]

    return DeveloperOutput(
        files_created=[{"path": f["path"], "description": f["description"], "content": f["content"]} for f in files],
        implementation_notes=(
            "Implemented a complete task management API with user authentication, "
            "task CRUD operations, dashboard metrics, and test coverage. "
            "Used FastAPI with SQLAlchemy ORM and Pydantic validation."
        ),
        files_changed=[f["path"] for f in files],
    )


def get_demo_reviewer_output(files_created: list, iteration: int = 0) -> ReviewerOutput:
    """Generate deterministic reviewer output for demo mode."""
    if iteration >= 1:
        # Second review - approve with minor notes
        return ReviewerOutput(
            findings=[
                ReviewFinding(
                    severity="info",
                    category="documentation",
                    file_path="README.md",
                    description="README could include environment variable documentation",
                    suggestion="Add a section listing configurable environment variables",
                ),
                ReviewFinding(
                    severity="info",
                    category="security",
                    file_path="src/config.py",
                    description="Secret key has a default value in config",
                    suggestion="Ensure SECRET_KEY is always set via environment in production",
                ),
            ],
            approval=True,
            summary="Code implementation meets requirements. Minor documentation improvements suggested.",
            recommendation="APPROVE - The implementation is solid with good structure and error handling.",
        )

    # First review - request some revisions
    return ReviewerOutput(
        findings=[
            ReviewFinding(
                severity="warning",
                category="security",
                file_path="src/services/auth_service.py",
                line_number=10,
                description="Using SHA-256 for password hashing is not recommended",
                suggestion="Use bcrypt or argon2 for password hashing instead of SHA-256",
            ),
            ReviewFinding(
                severity="error",
                category="validation",
                file_path="src/routers/tasks.py",
                line_number=15,
                description="Missing pagination for task listing endpoint",
                suggestion="Add limit/offset or cursor-based pagination to prevent returning unbounded results",
            ),
            ReviewFinding(
                severity="warning",
                category="error_handling",
                file_path="src/routers/auth.py",
                line_number=22,
                description="Login endpoint accepts query parameters instead of request body",
                suggestion="Use a Pydantic model for login credentials in the request body",
            ),
            ReviewFinding(
                severity="info",
                category="maintainability",
                file_path="src/models/task.py",
                description="Priority and Status enums defined but string columns used",
                suggestion="Consider using SQLAlchemy Enum type for type safety",
            ),
        ],
        approval=False,
        summary="Found 4 issues: 1 error, 2 warnings, 1 info. Key concerns are password hashing security and missing pagination.",
        recommendation="REVISE - Address the error and warning-level findings before approval.",
    )


def get_demo_tester_output(files_created: list) -> TesterOutput:
    """Generate deterministic tester output for demo mode."""
    test_files = [
        {
            "path": "tests/test_health.py",
            "content": '''"""Health check tests."""
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
''',
            "description": "Health endpoint test",
        },
        {
            "path": "tests/test_dashboard.py",
            "content": '''"""Dashboard tests."""
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_dashboard_empty():
    response = client.get("/api/dashboard/", params={"user_id": "test"})
    assert response.status_code == 200
    assert response.json()["total_tasks"] == 0
''',
            "description": "Dashboard endpoint test",
        },
    ]

    return TesterOutput(
        test_files_created=[{"path": f["path"], "description": f["description"], "content": f["content"]} for f in test_files],
        test_results=[
            TestResult(test_name="test_health_endpoint", status="passed", message="Health check returns 200 OK"),
            TestResult(test_name="test_register_user", status="passed", message="User registration works correctly"),
            TestResult(test_name="test_register_duplicate_email", status="passed", message="Duplicate email rejected with 400"),
            TestResult(test_name="test_create_task", status="passed", message="Task creation returns 201"),
            TestResult(test_name="test_list_empty_tasks", status="passed", message="Empty task list returns 200 with []"),
            TestResult(test_name="test_dashboard_empty", status="passed", message="Dashboard returns zero counts"),
            TestResult(
                test_name="test_task_update",
                status="skipped",
                message="Runtime execution skipped - no sandbox available",
            ),
            TestResult(
                test_name="test_task_deletion",
                status="skipped",
                message="Runtime execution skipped - no sandbox available",
            ),
        ],
        passed=6,
        failed=0,
        skipped=2,
        blocked=0,
        summary=(
            "6 tests passed via static analysis verification, 2 skipped due to "
            "sandbox unavailability. No test failures detected. Code structure "
            "and API contracts verified."
        ),
        execution_method="static_analysis",
    )
