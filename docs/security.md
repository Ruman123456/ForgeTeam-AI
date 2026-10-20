# ForgeTeam AI — Security & Execution Policy

ForgeTeam AI is designed with defense-in-depth principles. AI-generated code is treated as strictly untrusted user input.

---

## 1. Safe Code Execution Model

### Host Isolation
- AI agents never have shell execution permissions on the host system.
- Generated code is never executed directly by the backend process.

### Containerized Execution (When Docker is Configured)
If `DOCKER_ENABLED=true` and Docker is installed:
1. Tests run inside disposable containers (`python:3.11-slim`).
2. `--network none` disables all network access to prevent unauthorized outbound connections.
3. `--read-only` root filesystem prevents container system tampering.
4. Resource limits: `--memory 512m`, `--cpus 1.0`, `--pids-limit 64`.
5. Execution timeout (default: 60s) terminates hanging processes.
6. Non-root user privileges with dropped Linux capabilities.

### Safe Fallback (When Docker is Unavailable)
1. Python AST parsing (`ast.parse()`) performs static syntax verification.
2. Structure analysis checks imports, classes, and test fixtures without running code.
3. Runtime test execution is explicitly marked as `skipped` with honest status reporting.

---

## 2. Path Traversal & Filesystem Protection

Every run writes to an isolated folder:
```
generated_projects/<run_id>/
```

Enforced security controls:
- **Identifier Sanitization:** Run IDs are sanitized via regex `[^a-zA-Z0-9\-_]` to reject directory traversal characters.
- **Normalized Relative Paths:** All artifact paths are checked against `..`, leading slashes, and drive prefixes (`:`).
- **Filesystem Canonicalization:** `file_path.resolve()` confirms the target path starts with the run's root directory.
- **Safe ZIP Creation:** ZIP packaging validates archive entry paths to prevent zip-slip vulnerabilities.

---

## 3. Local-First Confidentiality

- **No Cloud Inference:** Prompts and code are processed strictly on localhost (`127.0.0.1`).
- **No Secret Leakage:** Configuration endpoints redact internal secrets and environment tokens.
- **Local SQLite Storage:** Project history and logs remain stored in local SQLite databases.
