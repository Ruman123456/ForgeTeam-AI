"""Test configuration and fixtures for ForgeTeam AI backend."""

import os
import sys
import pytest
from pathlib import Path

# Add backend directory to sys.path so 'app' is importable regardless of working directory
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment
os.environ["DATABASE_URL"] = "sqlite:///./test_forgeteam.db"
os.environ["DEMO_MODE"] = "true"
os.environ["APP_DEBUG"] = "false"

from app.database import Base, get_db
from app.main import app
from app.core.config import settings

# Test database
TEST_DB_PATH = Path("./test_forgeteam.db")
test_engine = create_engine("sqlite:///./test_forgeteam.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except Exception:
            pass


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def client():
    return TestClient(app)
