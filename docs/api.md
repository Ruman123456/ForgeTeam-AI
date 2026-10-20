# ForgeTeam AI — API Reference

All backend endpoints are bound to `127.0.0.1:8000` by default. Interactive OpenAPI Swagger documentation is available at `http://127.0.0.1:8000/docs`.

---

## System Endpoints

### `GET /api/health`
Returns application health and database connection status.
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "ollama_configured": true,
  "demo_mode": false
}
```

### `GET /api/config`
Returns safe public configuration options and Ollama connectivity status.

### `POST /api/ollama/check`
Initiates a probe to the local Ollama instance and returns available models.

### `GET /api/dashboard/stats`
Returns aggregated metrics for total projects, total runs, and run statuses.

---

## Projects API

### `POST /api/projects`
Creates a project record.
```json
{
  "name": "Task Manager",
  "description": "Task management system with priorities and deadlines",
  "language_preference": "python",
  "framework_preference": "fastapi"
}
```

### `GET /api/projects`
Lists projects with pagination (`?skip=0&limit=50`).

### `GET /api/projects/{project_id}`
Retrieves a project by identifier.

### `PATCH /api/projects/{project_id}`
Updates an existing project record.

### `DELETE /api/projects/{project_id}`
Deletes a project, its associated run records, and all generated artifacts on disk.

---

## Runs & Multi-Agent Execution API

### `POST /api/runs`
Initializes a new multi-agent run and enqueues background workflow execution.
```json
{
  "project_id": "0df83850-8b4d-44a6-b519-53e7f4c40b82",
  "demo_mode": true
}
```

### `GET /api/runs`
Lists agent runs with optional filtering (`?project_id=...&status=...`).

### `GET /api/runs/{run_id}`
Returns real-time run state, current stage, and revision count.

### `GET /api/runs/{run_id}/logs`
Returns chronological agent activity logs for the run.

### `GET /api/runs/{run_id}/artifacts`
Lists all generated source files and reports.

### `GET /api/runs/{run_id}/artifacts/{artifact_id}`
Returns the file contents and metadata of an individual artifact.

### `GET /api/runs/{run_id}/download`
Streams a ZIP archive containing all project files generated during the run.

### `POST /api/runs/{run_id}/cancel`
Cancels an active or queued agent run safely.
