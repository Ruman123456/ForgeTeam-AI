# ForgeTeam AI - Start Backend (PowerShell)
Write-Host "Starting ForgeTeam AI Backend on http://127.0.0.1:8000..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
