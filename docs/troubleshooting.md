# ForgeTeam AI — Troubleshooting & Diagnostic Guide

This guide addresses common configuration and environment issues.

---

## 1. Ollama Connection Issues

### Symptom: "Cannot connect to Ollama at http://127.0.0.1:11434"
- **Cause:** Ollama service is not installed or not currently running.
- **Resolution:**
  1. Verify Ollama is installed: `ollama --version`
  2. Start the daemon: `ollama serve`
  3. Verify connection: Visit `http://127.0.0.1:11434/api/tags` in your browser.
  4. If Ollama is not installed, use **Demo Mode** in ForgeTeam AI to evaluate the platform immediately without models.

### Symptom: "Model 'qwen2.5-coder:3b' not found"
- **Cause:** Ollama is running, but the configured model weights have not been downloaded.
- **Resolution:**
  ```powershell
  ollama pull qwen2.5-coder:3b
  ```
  Or change `OLLAMA_MODEL` in `.env` to any existing model installed on your machine.

---

## 2. Constrained Hardware Performance (e.g., 4GB VRAM or CPU Only)

### Slow Inference or GPU Out-of-Memory
- **Resolution:**
  - Switch to a 1.5B parameter model:
    ```powershell
    ollama pull qwen2.5-coder:1.5b
    ```
    Then set `OLLAMA_MODEL=qwen2.5-coder:1.5b` in `backend/.env`.
  - Ollama automatically falls back to CPU system memory when GPU VRAM is full.
  - Keep `OLLAMA_TIMEOUT=180` in `.env` to accommodate slower CPU inference speeds.

---

## 3. Port Conflicts

### Port 8000 (Backend) or 5173 (Frontend) Already in Use
- Change backend port:
  ```powershell
  python -m uvicorn app.main:app --port 8001
  ```
- Change frontend port in `frontend/vite.config.ts`:
  ```ts
  server: { port: 5174 }
  ```

---

## 4. Test Execution & Docker Warning

### "Docker sandbox unavailable on host"
- **Explanation:** This is an expected safety notice when running on machines without Docker Desktop active. ForgeTeam safely skips arbitrary binary execution and performs static Python AST checks. This is the intended secure behavior.
