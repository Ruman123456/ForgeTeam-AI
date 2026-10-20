# ForgeTeam AI - Start Backend and Frontend concurrently (PowerShell)
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   ForgeTeam AI - Local Development Stack  " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$backendPath = Resolve-Path "$PSScriptRoot\..\backend"
$frontendPath = Resolve-Path "$PSScriptRoot\..\frontend"

Write-Host "Launching Backend on http://127.0.0.1:8000..." -ForegroundColor Green
$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory $backendPath -PassThru

Start-Sleep -Seconds 2

Write-Host "Launching Frontend on http://127.0.0.1:5173..." -ForegroundColor Green
$frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory $frontendPath -PassThru

Write-Host ""
Write-Host "Both services are running!" -ForegroundColor Cyan
Write-Host "• Frontend UI: http://127.0.0.1:5173" -ForegroundColor White
Write-Host "• Backend API: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C or close this terminal window to stop." -ForegroundColor Yellow

try {
    Wait-Process -Id $backendProcess.Id, $frontendProcess.Id
} finally {
    Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue
}
