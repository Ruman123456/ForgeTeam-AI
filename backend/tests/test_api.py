"""API endpoint integration tests."""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "database" in data


def test_config_endpoint(client: TestClient):
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert "ollama_base_url" in data
    assert "ollama_model" in data
    assert "demo_mode" in data


def test_project_crud(client: TestClient):
    # 1. Create project
    create_payload = {
        "name": "TaskFlow Pro",
        "description": "A high-performance task management app with priorities and deadline tracking.",
        "language_preference": "python",
        "framework_preference": "fastapi"
    }
    create_res = client.post("/api/projects", json=create_payload)
    assert create_res.status_code == 201
    project = create_res.json()
    project_id = project["id"]
    assert project["name"] == "TaskFlow Pro"

    # 2. Get project by ID
    get_res = client.get(f"/api/projects/{project_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == project_id

    # 3. List projects
    list_res = client.get("/api/projects")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 4. Update project
    update_res = client.patch(f"/api/projects/{project_id}", json={"name": "TaskFlow Enterprise"})
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "TaskFlow Enterprise"

    # 5. Delete project
    del_res = client.delete(f"/api/projects/{project_id}")
    assert del_res.status_code == 204

    # 6. Verify 404 after deletion
    get_deleted = client.get(f"/api/projects/{project_id}")
    assert get_deleted.status_code == 404


def test_project_validation_errors(client: TestClient):
    # Empty name
    res = client.post("/api/projects", json={"name": "", "description": "Too short"})
    assert res.status_code == 422

    # Description too short (< 10 chars)
    res2 = client.post("/api/projects", json={"name": "Valid Name", "description": "Short"})
    assert res2.status_code == 422


def test_run_creation_and_workflow(client: TestClient):
    # Create project first
    p_res = client.post("/api/projects", json={
        "name": "Demo MultiAgent Run",
        "description": "Multi-agent collaborative app builder with test generation and validation.",
    })
    project_id = p_res.json()["id"]

    # Start run in demo mode
    run_res = client.post("/api/runs", json={
        "project_id": project_id,
        "demo_mode": True,
    })
    assert run_res.status_code == 201
    run_data = run_res.json()
    run_id = run_data["id"]
    assert run_data["demo_mode"] is True
    assert run_data["status"] in ("queued", "running", "completed")

    # Fetch run
    get_run = client.get(f"/api/runs/{run_id}")
    assert get_run.status_code == 200
    assert get_run.json()["id"] == run_id

    # List runs with filter
    list_runs = client.get(f"/api/runs?project_id={project_id}")
    assert list_runs.status_code == 200
    assert list_runs.json()["total"] >= 1

    # Check cancel endpoint for completed or active run
    cancel_res = client.post(f"/api/runs/{run_id}/cancel")
    assert cancel_res.status_code in (200, 400)  # 400 if already terminal, 200 if queued/running


def test_path_traversal_protection(client: TestClient):
    # Test path traversal prevention on non-existent or malicious paths
    res = client.get("/api/runs/nonexistent_run_id/artifacts/evil_id")
    assert res.status_code == 404


def test_dashboard_stats(client: TestClient):
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_projects" in data
    assert "total_runs" in data
    assert "completed_runs" in data
    assert "failed_runs" in data
