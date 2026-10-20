# ForgeTeam AI - Start Frontend (PowerShell)
Write-Host "Starting ForgeTeam AI Frontend on http://127.0.0.1:5173..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\..\frontend"
npm run dev
